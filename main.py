import logging
from config import load_config
from scraper import scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%M:%S",
    filename="data/scraper.log",
)


def main():
    json_data = load_config()
    scraper(json_data)


if __name__ == "__main__":
    main()
