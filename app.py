import os
import json
import random
import logging
import time
from typing import List, Dict, Any

import requests
from config import (
    load_config,
    save_config,
    RETRY_AFTER_DEFAULT,
    SLEEP_MIN,
    SLEEP_MAX,
    SAVE_INTERVAL,
    DATA_DIR,
    DATA_FILE,
    CONFIG_FILE,
    MAX_RETRIES,
    RETRY_DELAY,
)

logging.basicConfig(level=logging.INFO)
json_data = load_config()


def make_request() -> requests.Response:
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.post(**json_data)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            retries += 1
            logging.error(f"Request failed: {e}. Retrying {retries}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    raise requests.RequestException(f"Failed request after {MAX_RETRIES} retries")


def get_messages() -> Dict[str, Any]:
    while True:
        response = make_request()
        if response.status_code == 429:
            retry_after = int(response.headers.get("retry-after", RETRY_AFTER_DEFAULT))
            logging.error(f"Rate limit exceeded. Sleeping for {retry_after} seconds")
            time.sleep(retry_after)
        else:
            break

    if response.status_code != 201:
        logging.error(f"{response.status_code} - {response.text} - {response.headers}")
        return {}

    return response.json()


def get_next_message_id(data: Dict[str, Any]) -> str:
    return data.get("messages", [{}])[0].get("id", "")


def scraper() -> List[Dict[str, Any]]:
    messages = []
    logging.info(f"Scraping messages from {json_data['json']['messages']['id_lt']}")

    while True:
        data = get_messages()
        if not data.get("messages"):
            break

        messages.extend(data["messages"])
        logging.info(f"Scraped {len(messages)} messages")
        time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))
        json_data["json"]["messages"]["id_lt"] = get_next_message_id(data)

        if len(messages) % SAVE_INTERVAL == 0:
            save_messages(messages)
            messages.clear()
            save_config(json_data)
            logging.info(f"Scraped {len(messages)} messages. Saved to {DATA_FILE}")
    return messages


def save_messages(messages: List[Dict[str, Any]]) -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(CONFIG_FILE):
        logging.error(
            "Rename config.example.json to config.json and set the required values"
        )
        exit(1)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            existing_messages = json.load(f)
    else:
        existing_messages = []

    existing_messages.extend(messages)

    with open(DATA_FILE, "w") as f:
        f.write(json.dumps(existing_messages, indent=4))


if __name__ == "__main__":
    scraper()
