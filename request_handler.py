import logging
import time
import requests
from config import MAX_RETRIES, RETRY_DELAY, RETRY_AFTER_DEFAULT


def make_request(json_data: dict) -> requests.Response:
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.post(**json_data)
            if response.status_code != 201:
                logging.error(
                    f"Request failed: {response.status_code} - {response.text}"
                )
                raise requests.RequestException("Failed request")
            return response
        except requests.RequestException as e:
            retries += 1
            logging.error(f"Request failed: {e}. Retrying {retries}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    raise requests.RequestException(f"Failed request after {MAX_RETRIES} retries")


def get_messages(json_data: dict) -> dict:
    while True:
        response = make_request(json_data)
        if response.status_code == 429:
            retry_after = int(response.headers.get("retry-after", RETRY_AFTER_DEFAULT))
            logging.error(f"Rate limit exceeded. Sleeping for {retry_after} seconds")
            time.sleep(retry_after)
        else:
            return response.json()
