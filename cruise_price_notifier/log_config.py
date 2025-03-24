import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/cruise-price-notifier.log'),
            logging.StreamHandler()
        ]
    )


log = logging.getLogger(__name__)
