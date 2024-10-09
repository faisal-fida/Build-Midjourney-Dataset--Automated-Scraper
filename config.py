import os
import json

RETRY_AFTER_DEFAULT = 60
SLEEP_MIN = 0.5
SLEEP_MAX = 1
SAVE_INTERVAL = 300 * 300
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "messages.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
MAX_RETRIES = 5
RETRY_DELAY = 5


def load_config():
    with open("data/config.json") as f:
        config = json.load(f)
        return config


def save_config(params):
    config = load_config()
    config["params"] = params
    with open("data/config.json", "w") as f:
        json.dump(config, f)
