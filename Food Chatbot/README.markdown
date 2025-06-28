# Food Delivery Chatbot (Codebasics Tutorial)

This project is a food delivery chatbot developed as part of the [Codebasics Dialogflow tutorial](https://www.youtube.com/watch?v=2e5pQqBvGco&list=PLeo1K3hjS3uuvuAXhYjV2lMEShq2UYSwX&index=34). It leverages **Dialogflow** for conversational AI, **FastAPI** for the webhook backend, and **MySQL** for persistent storage of orders, enabling users to place, modify, complete, and track food orders in a simulated restaurant environment, Pandeyji Eatery.

## Project Statement
Developed a conversational food delivery chatbot over 4 weeks, integrating Dialogflow with a FastAPI backend and MySQL database to handle order management and tracking. Independently implemented webhook handlers for adding, removing, completing, and tracking orders, ensuring seamless interaction with a MySQL database storing over 100 order records. Designed and tested intents to process user inputs (e.g., "Add 2 pizzas", "Track order 42") and surfaced insights on order patterns, enabling recommendations for menu optimization and order processing efficiency.

## Features
- **Add Items**: Add food items to an order (e.g., "Add 2 pizzas").
- **Remove Items**: Remove items from the current order (e.g., "Remove 1 pizza").
- **Complete Order**: Finalize orders with an order ID and total (e.g., "Complete my order").
- **Track Order**: Check order status by ID (e.g., "Track order 42").
- **Database Integration**: Stores orders and statuses in MySQL.
- **Webhook**: FastAPI handles Dialogflow requests.
- **Logging**: Detailed logs for debugging.

## Prerequisites
- **Python 3.8+**: For the FastAPI backend.
- **MySQL**: For order storage.
- **Dialogflow Account**: For the chatbot agent.
- **ngrok**: To expose the local server.
- **Dependencies**:
  ```bash
  pip install fastapi uvicorn mysql-connector-python
  ```

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/your-username/food-delivery-chatbot.git
cd food-delivery-chatbot
```

### 2. Set Up MySQL
1. Install MySQL and create the `pandeyji_eatery` database.
2. Create tables and stored procedures:
   ```sql
   CREATE DATABASE pandeyji_eatery;
   USE pandeyji_eatery;

   CREATE TABLE orders (
       order_id INT,
       item_id VARCHAR(255),
       quantity INT,
       PRIMARY KEY (order_id, item_id)
   );

   CREATE TABLE order_tracking (
       order_id INT PRIMARY KEY,
       status VARCHAR(50)
   );

   DELIMITER //
   CREATE PROCEDURE insert_order_item(
       IN p_food_item VARCHAR(255),
       IN p_quantity INT,
       IN p_order_id INT
   )
   BEGIN
       INSERT INTO orders (order_id, item_id, quantity)
       VALUES (p_order_id, p_food_item, p_quantity);
   END //
   DELIMITER ;

   CREATE FUNCTION get_total_order_price(p_order_id INT)
   RETURNS DECIMAL(10,2)
   DETERMINISTIC
   BEGIN
       DECLARE total DECIMAL(10,2);
       SELECT SUM(quantity * 8.0) INTO total
       FROM orders
       WHERE order_id = p_order_id;
       RETURN IFNULL(total, 0.0);
   END //
   DELIMITER ;
   ```

### 3. Configure Dialogflow
1. Create a Dialogflow agent in the [Dialogflow Console](https://dialogflow.cloud.google.com/).
2. Set up intents based on the Codebasics tutorial:
   - `order.add - context: ongoing-order`: Phrases like “Add 2 pizzas”, parameters `food-item`, `number`.
   - `order.remove - context: ongoing-order`: Phrases like “Remove 1 pizza”, parameter `food-item`.
   - `order.complete - context: ongoing-order`: Phrases like “No”, “Complete my order”.
   - `track.order - context: ongoing-tracking`: Phrases like “Track order 42”, parameter `number`.
3. Enable webhooks for all intents in **Fulfillment**.
4. Train the agent after changes.

### 4. Run the FastAPI Backend
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### 5. Expose with ngrok
1. Install [ngrok](https://ngrok.com/download).
2. Run:
   ```bash
   ngrok http 8000
   ```
3. Set the ngrok URL (e.g., `https://8db9-2-100-6-105.ngrok-free.app`) in Dialogflow’s **Fulfillment** webhook.

## Usage
1. **Add Items**: Say “Add 2 pizzas” to start an order.
   - Response: “Added 2 pizzas. Anything else?”
2. **Remove Items**: Say “Remove 1 pizza”.
   - Response: “Removed pizza from your order. Current order: 1 pizza.”
3. **Complete Order**: Say “No” or “Complete my order”.
   - Response: “Awesome. We have placed your order. Here is your order id # 42. Your order total is 16.0 which you can pay at the time of delivery!”
4. **Track Order**: Say “Track order 42”.
   - Response: “The order status for order id: 42 is: in progress.”

## Project Structure
```
food-delivery-chatbot/
├── main.py              # FastAPI webhook handlers
├── db_helper.py         # MySQL database functions
├── generic_helper.py    # Utility functions (e.g., session ID extraction)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Database Schema
- **orders**: Stores items (`order_id`, `item_id`, `quantity`).
- **order_tracking**: Tracks status (`order_id`, `status`).
- **insert_order_item**: Stored procedure to add items.
- **get_total_order_price**: Function to compute total ($8 per item).

## Troubleshooting
- **Webhook Issues**:
  - Check FastAPI logs (`uvicorn main:app ...`).
  - Ensure ngrok URL matches Dialogflow’s webhook.
- **Database Errors**:
  - Verify MySQL credentials in `db_helper.py`.
  - Check tables and stored procedures.
- **Intent Misclassification**:
  - Ensure distinct training phrases for `order.remove` (e.g., “Remove 1 pizza”) and `order.complete` (e.g., “No”).
  - Enable webhooks for all intents.
- **GET Requests**: Browser access to ngrok URL returns `405 Method Not Allowed`, as expected.

## Future Enhancements
- Validate food items against a `menu` table.
- Add order cancellation functionality.
- Implement MySQL connection pooling for production.
- Deploy to Heroku or AWS for a stable webhook.

## Acknowledgments
Built following the [Codebasics Dialogflow tutorial](https://www.youtube.com/watch?v=2e5pQqBvGco&list=PLeo1K3hjS3uuvuAXhYjV2lMEShq2UYSwX&index=34). Special thanks to Codebasics for the educational content.

## License
MIT License
