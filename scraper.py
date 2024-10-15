import logging
import os
import json
import random
import time
from typing import List, Dict, Any

from config import (
    save_config,
    SLEEP_MIN,
    SLEEP_MAX,
    SAVE_INTERVAL,
    DATA_DIR,
    DATA_FILE,
)
from request_handler import get_messages


def get_next_message_id(data: Dict[str, Any]) -> str:
    return data.get("messages", [{}])[0].get("id", "")


def save_messages(messages: List[Dict[str, Any]]) -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            existing_messages = json.load(f)
    else:
        existing_messages = []

    existing_messages.extend(messages)

    with open(DATA_FILE, "w") as f:
        json.dump(existing_messages, f, indent=4)


def scraper(json_data: dict) -> List[Dict[str, Any]]:
    messages = []
    logging.info(f"Scraping messages from {json_data['json']['messages']['id_lt']}")

    while True:
        data = get_messages(json_data)
        if not data.get("messages"):
            break

        messages.extend(data["messages"])
        logging.info(f"Scraped {len(messages)} messages")
        time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))
        json_data["json"]["messages"]["id_lt"] = get_next_message_id(data)

        if len(messages) % SAVE_INTERVAL == 0 or len(data.get("messages")) < 300:
            save_messages(messages)
            messages.clear()
            save_config(json_data)
            logging.info(f"Saved to {DATA_FILE}. Config updated.")
    return messages
