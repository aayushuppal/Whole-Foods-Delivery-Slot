#!/usr/bin/env python3.7

"""
whole foods delivery slot finder - chrome
"""

import os
import time
import bs4
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

WF_CHECKOUT_URL = (
    "https://www.amazon.com/gp/buy/shipoptionselect/handlers/display.html?hasWorkingJavascript=1"
)


def alert_util(msg):
    """
    alert utility method
    """
    os.system(f'espeak "{msg}"')


def get_wf_slot(checkout_pg_url):
    """
    slot check method
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(checkout_pg_url)
    html = driver.page_source
    soup = bs4.BeautifulSoup(html)
    time.sleep(60)
    no_open_slots = True

    while no_open_slots:
        driver.refresh()
        print("refreshed")
        html = driver.page_source
        soup = bs4.BeautifulSoup(html)
        time.sleep(4)

        try:
            pattern_text = "Next available"
            next_slot_text = soup.find(
                "h4", class_="ufss-slotgroup-heading-text a-text-normal"
            ).text
            if pattern_text in next_slot_text:
                print("SLOTS OPEN!")
                alert_util("Slots for delivery opened!")
                no_open_slots = False
                time.sleep(1400)
        except AttributeError:
            continue

        try:
            pattern_text = "Not available"
            all_dates = soup.findAll("div", {"class": "ufss-date-select-toggle-text-availability"})
            for each_date in all_dates:
                if pattern_text not in each_date.text:
                    print("SLOTS OPEN!")
                    alert_util("Slots for delivery opened!")
                    no_open_slots = False
                    time.sleep(1400)
        except AttributeError:
            continue

        try:
            no_slot_pattern_text = (
                "No delivery windows available. New windows are released throughout the day."
            )
            if no_slot_pattern_text == soup.find("h4", class_="a-alert-heading").text:
                print("NO SLOTS!")
        except AttributeError:
            print("SLOTS OPEN!")
            alert_util("Slots for delivery opened!")
            no_open_slots = False


if __name__ == "__main__":
    get_wf_slot(WF_CHECKOUT_URL)
