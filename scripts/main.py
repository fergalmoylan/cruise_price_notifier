from selenium import webdriver
from datetime import datetime
from cruise_price_notifier.send_mail import send_mail_html
import time
import logging
import tomli
import argparse
from cruise_price_notifier.log_config import setup_logging
import cruise_price_notifier.scrape_url
import cruise_price_notifier.render_results

setup_logging()
log = logging.getLogger(__name__)


def load_config(filepath: str):
    with open(filepath, "rb") as f:
        config = tomli.load(f)
    return config


def main():
    parser = argparse.ArgumentParser(description="Python application with configurable settings.")
    parser.add_argument("config_path", help="Path to the configuration file (TOML).")
    args = parser.parse_args()
    config_path = args.config_path
    config = load_config(config_path)
    current_date = datetime.now().strftime("%Y-%m-%d")
    log.info(current_date)
    url = config.get("url")
    driver = webdriver.Safari()
    cruise_price_notifier.scrape_url.wait_for_spinner(driver)

    time.sleep(1)
    cruise_price_notifier.scrape_url.read_page(driver, url)

    file_name = f"csvs/result_{current_date}.csv"
    #cruise_price_notifier.render_results.write_to_csv(file_name)
    html_content = cruise_price_notifier.render_results.create_html_from_results(config.get("headers"), config.get("sort_by"))

    send_mail_html(html_content, cruise_price_notifier.render_results.format_date(), config.get("recipients"))


if __name__ == "__main__":
    main()

