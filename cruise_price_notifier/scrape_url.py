import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import json
import time
import re
import logging

log = logging.getLogger(__name__)


def wait_for_spinner(driver):
    log.info("waiting for spinner")
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'MuiCircularProgress-root'))
        WebDriverWait(driver, 10).until_not(element_present)
    except Exception as e:
        log.error(f"An error occurred: {str(e)}")


def load_all_results(driver):
    log.info("Loading all results")
    while True:
    # for i in range(2):
        try:
            load_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'load-more-button')))
            load_more_button.click()
            time.sleep(2)
        except Exception as e:
            break


def get_main_cruise_details(cruise):
    cruise_details = {}
    # with open("resources/cruise_details.html", "a") as file:
    #     file.write(cruise.prettify())
    cruise_details["cruise_name"] = cruise.find("h4",
                                                class_="RefinedCruiseCard-styles__RefinedCruiseCardName-sc-3126d0eb-4 jXSNsb").text.strip()
    cruise_details["cruise_duration"] = cruise.find("h3",
                                                    class_="RefinedCruiseCard-styles__RefinedCruiseCardTotalNights-sc-3126d0eb-3 cQZHYa").text.strip()
    cruise_details["cruise_ship"] = cruise.find("h3",
                                                class_="CruiseCardShip-styles__CruiseCardShipName-sc-36a3f506-1 dCppir").text.strip()
    cruise_details["cruise_destinations"] = [item.text.strip() for item in cruise.find_all("li",
                                                                                           "CruiseCardLocationList-styles__CruiseCardLocationListItem-sc-fbffed9d-3 YrOsx")]
    cruise_details["url-date"] = datetime.now().strftime("%Y-%m-%d")
    return cruise_details


def get_cruise_price_per_room(view_dates_button, driver, cruise_details):
    time.sleep(2)
    button_id = view_dates_button.get('data-testid')
    selenium_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"button[data-testid='{button_id}']")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", selenium_button)
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[data-testid='{button_id}']")))
    retries = 3
    for attempt in range(retries):
        try:
            log.info("retrying view dates button click")
            driver.execute_script("arguments[0].click();", selenium_button)
            break
        except Exception as e:
            if attempt == retries - 1:
                log.error("Error Viewing Dates: {}".format(str(e)))
                raise
            driver.execute_script("window.scrollBy(0, 100);")  # Minor scroll adjustment
            time.sleep(0.5)

    # selenium_button.click()
    time.sleep(1)

    cruise_dates_html = driver.page_source
    cruise_dates_soup = BeautifulSoup(cruise_dates_html, 'html.parser')
    room_details = cruise_dates_soup.find('div', class_='RefinedCruiseDetailsPanelCardList-styles__RefinedCruiseDetailsPanelCardListBase-sc-e3222771-0 jEOFqI')
    current_url = driver.current_url
    # with open("resources/cruise_dates.html", "w") as file:
    #     file.write(room_details.prettify())

    rooms = room_details.find_all('div', class_='RefinedCruiseDetailsPanelCard-styles__RefinedCruiseDetailsPanelCardDetails-sc-23d56c5b-2 bCTkEF')
    for room in rooms:
        room_type = room.find('span', class_='RefinedCruiseDetailsPanelCard-styles__RefinedCruiseDetailsPanelCardStateroomName-sc-23d56c5b-4 kWZXnb').get_text(strip=True)
        if room_type == "Interna":
            room_type = "Interior"
        if room_type == "Exterior" or room_type == "Vista externa":
            room_type = "Outside View"
        elif room_type == "Balcón" or room_type == "Con Balcone" or room_type == "Cabine com varanda":
            room_type = "Balcony"
        elif room_type == "Suíte" or room_type == "Su\u00edte" or room_type == "Royal Suite Class" or room_type == "Suites":
            room_type = "Suite"
        price_div = room.find('div', class_='RefinedCruiseDetailsPanelCardPrice-styles__RefinedCruiseDetailsPanelCardPriceBase-sc-fc6ae0-0 gTBir')
        if price_div.find('span', class_='RefinedCruiseDetailsPanelCardPrice-styles__RefinedCruiseDetailsPanelCardPriceLabel-sc-fc6ae0-4 gjUyTZ sold-out'):
            price_text = price_div.find('span').get_text(strip=True)
        else:
            price_text = price_div.find('span', class_='RefinedCruiseDetailsPanelCardPrice-styles__RefinedCruiseDetailsPanelCardPriceValue-sc-fc6ae0-2 csJTcr').get_text(strip=True)
        cruise_details[room_type] = price_text
    cruise_details["URL"] = current_url
    close_dates_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "cruise-detail-close-button")))
    close_dates_button.click()
    time.sleep(1)
    return cruise_details


def read_page(driver, url):
    try:
        log.info("Loading driver...")
        driver.get(url)
        log.info("Driver loaded")
        time.sleep(1)
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
            accept_button.click()
        except Exception as e:
            log.error("Error Accepting Cookies: {}".format(str(e)))
        time.sleep(1)

        load_all_results(driver)
        results = driver.page_source
        soup = BeautifulSoup(results, 'html.parser')
        number_of_cruises_div = soup.find("div",
                                          class_="MuiTypography-root MuiTypography-title2 styles__SectionTitle-sc-2ec14447-5 jTxkZA css-13jcdqr")
        number_of_results = number_of_cruises_div.find_all('span')[1].text
        log.info("Found {} cruises".format(number_of_results))

        cruise_results_wrapper = driver.find_element(By.ID, "cruise-results-wrapper")
        cruise_results_html = cruise_results_wrapper.get_attribute('innerHTML')
        soup = BeautifulSoup(cruise_results_html, 'html.parser')
        with open("resources/results.html", "w") as file:
            file.write(soup.prettify())
        cruises = soup.find_all("div",
                                class_="CruiseCard-styles__CruiseCardBase-sc-c980be92-0 RefinedCruiseCard-styles__RefinedCruiseCardBase-sc-3126d0eb-0 iirDCV eFYknU")
        results = []
        i = 1
        for cruise in cruises:
            cruise_details = get_main_cruise_details(cruise)
            view_dates_button = cruise.find("button", {"data-testid": re.compile(r"^cruise-view-dates-button-")})
            try:
                cruise_details = get_cruise_price_per_room(view_dates_button, driver, cruise_details)
                results.append(cruise_details)
            except Exception as e:
                log.warning("Error getting cruise prices: {}".format(str(e)))
                log.info("Attempting to load more results")
                try:
                    load_more_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'load-more-button')))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
                    time.sleep(1)
                    load_more_button.click()
                    time.sleep(1)
                    try:
                        cruise_details = get_cruise_price_per_room(view_dates_button, driver, cruise_details)
                        results.append(cruise_details)
                    except Exception as e:
                        log.error("Error getting cruise details: {}".format(str(e)))
                except Exception as e:
                    log.error("Error loading more results: {}".format(str(e)))

            log.info("Processed {}/{} Cruises".format(i, number_of_results))
            i += 1
        if not results:
            log.error("No results collected. Shutting down.")
            sys.exit(0)
        with open("resources/output.json", 'w+') as file:
            file.write(json.dumps(results, indent=4))

    except Exception as e:
        log.error("Error reading page: {}".format(str(e)))
    finally:
        driver.quit()
