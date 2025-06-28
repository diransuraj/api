import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_str_from_food_dict(food_dict: dict):
    result = ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
    return result

def extract_session_id(session_str: str):
    match = re.search(r"/sessions/([^/]+)/contexts/", session_str)
    if match:
        session_id = match.group(1)
        logging.info(f"Extracted session_id: {session_id}")
        return session_id
    logging.error(f"Invalid session string: {session_str}")
    return ""