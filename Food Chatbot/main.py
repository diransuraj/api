from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()
inprogress_orders = {}


@app.get("/")
async def handle_get_request():
    logging.info("Received GET request to root endpoint")
    return JSONResponse(content={"fulfillmentText": "This endpoint expects POST requests for Dialogflow webhooks."},
                        status_code=405)


@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        logging.info(f"Received POST request: {payload}")
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        try:
            session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
        except (IndexError, KeyError) as e:
            logging.error(f"Failed to extract session_id: {e}")
            session_id = "unknown_session"
        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing-order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'track.order - context: ongoing-tracking': track_order
        }
        handler = intent_handler_dict.get(intent, lambda params, sid: JSONResponse(
            content={"fulfillmentText": f"Unknown intent: {intent}"}))
        return handler(parameters, session_id)
    except Exception as e:
        logging.error(f"Error in handle_request: {e}")
        return JSONResponse(content={"fulfillmentText": "Internal server error. Please try again later."},
                            status_code=500)


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])
    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, please specify the quantity for each food item."
    else:
        if session_id not in inprogress_orders:
            inprogress_orders[session_id] = {}
        for food, qty in zip(food_items, quantities):
            inprogress_orders[session_id][food] = qty
        fulfillment_text = f"Added {generic_helper.get_str_from_food_dict(inprogress_orders[session_id])}. Anything else?"
    logging.info(f"Added to order: {inprogress_orders.get(session_id, {})}")
    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def remove_from_order(parameters: dict, session_id: str):
    logging.info(f"Remove order parameters: {parameters}, session_id: {session_id}")
    if session_id not in inprogress_orders:
        fulfillment_text = "No order found to remove items from. Please add items first."
        return JSONResponse(content={"fulfillmentText": fulfillment_text})

    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])
    current_order = inprogress_orders[session_id]
    removed_items = []

    for food in food_items:
        if food in current_order:
            removed_items.append(food)
            del current_order[food]

    if removed_items:
        fulfillment_text = f"Removed {', '.join(removed_items)} from your order. Current order: {generic_helper.get_str_from_food_dict(current_order) if current_order else 'empty'}."
        if not current_order:
            del inprogress_orders[session_id]
    else:
        fulfillment_text = "No specified items found in your order."

    logging.info(f"Removed from order: {inprogress_orders.get(session_id, {})}")
    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def complete_order(parameters: dict, session_id: str):
    logging.info(f"Completing order for session_id: {session_id}, inprogress_orders: {inprogress_orders}")
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
        return JSONResponse(content={"fulfillmentText": fulfillment_text})

    order = inprogress_orders[session_id]
    order_id = save_to_db(order)
    if order_id == -1:
        fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please place a new order again."
    else:
        order_total = db_helper.get_total_order_price(order_id)
        fulfillment_text = f"Awesome. We have placed your order. Here is your order id # {order_id}. Your order total is {order_total} which you can pay at the time of delivery!"
        del inprogress_orders[session_id]
    logging.info(
        f"Complete order response: {fulfillment_text}, order_id: {order_id if 'order_id' in locals() else 'not set'}")
    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def save_to_db(order: dict):
    logging.info(f"Saving order to database: {order}")
    next_order_id = db_helper.get_next_order_id()
    if next_order_id == -1:
        logging.error("Failed to get next order_id")
        return -1
    for food_item, quantity in order.items():
        try:
            qty = int(quantity)  # Convert float to int for database
            rcode = db_helper.insert_order_item(food_item, qty, next_order_id)
            if rcode == -1:
                logging.error(f"Failed to insert order item: {food_item}, quantity: {qty}, order_id: {next_order_id}")
                return -1
        except ValueError as e:
            logging.error(f"Invalid quantity for {food_item}: {quantity}, error: {e}")
            return -1
    db_helper.insert_order_tracking(next_order_id, "in progress")
    logging.info(f"Order saved successfully, order_id: {next_order_id}")
    return next_order_id


def track_order(parameters: dict, session_id: str):
    logging.info(f"Track order parameters: {parameters}, session_id: {session_id}")
    order_id = parameters.get('number', [None])[0]
    if not order_id:
        logging.error("No order_id found in parameters")
        return JSONResponse(content={"fulfillmentText": "Please provide a valid order ID."})
    try:
        order_id = int(order_id)
        if order_id <= 0:
            raise ValueError("Order ID must be positive")
    except (ValueError, TypeError) as e:
        logging.error(f"Invalid order_id: {order_id}, error: {e}")
        return JSONResponse(content={"fulfillmentText": "Invalid order ID format. Please provide a valid number."})
    order_status = db_helper.get_order_status(order_id)
    fulfillment_text = f"The order status for order id: {order_id} is: {order_status}" if order_status else f"No order found with order id: {order_id}"
    logging.info(f"Track order response: {fulfillment_text}")
    return JSONResponse(content={"fulfillmentText": fulfillment_text})