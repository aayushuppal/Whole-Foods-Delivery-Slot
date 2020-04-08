#!/usr/bin/env python3.7
# pylint: disable=missing-function-docstring, too-few-public-methods

"""
whole foods delivery slot finder - chrome
"""

import os
import time
import re
import bs4
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# ==================================================================================================


class Config:
    """
    Configuration params
    """

    del_un_patt1 = ".*Please check back later or shop a Whole Foods Market near you.$"
    del_un_patt2 = "^No delivery windows available. New windows are released throughout the day.$"
    del_un_regex = re.compile(f"{del_un_patt1}|{del_un_patt2}")

    date_not_avail_patt1 = "Not available"

    next_avail_patt1 = "Next available"

    wf_checkout_url = (
        "https://www.amazon.com/gp/buy/shipoptionselect"
        + "/handlers/display.html?hasWorkingJavascript=1"
    )

    whitespaces_regex = re.compile("\\s+")


class SoupObj:
    """
    beautiful soup object container
    """

    def __init__(self):
        self.soup = None


def get_normalized_text(txt):
    return Config.whitespaces_regex.sub(" ", txt).strip()


def alert_util(msg):
    os.system(f'espeak "{msg}"')


# ==================================================================================================


def is_delivery_unavailable_banner_present(soup_):
    htm_elems = soup_.findAll("h4", {"class": "a-alert-heading"})
    for htm_elem in htm_elems:
        txt = get_normalized_text(htm_elem.text)
        if Config.del_un_regex.match(txt) is not None:
            return True
    print("is_delivery_unavailable_banner_present = False")
    return False


def some_date_has_availability(soup_):
    htm_elems = soup_.findAll("div", {"class": "ufss-date-select-toggle-text-availability"})
    for htm_elem in htm_elems:
        txt = get_normalized_text(htm_elem.text)
        if Config.date_not_avail_patt1 not in txt:
            print("some_date_has_availability = True")
            return True
    return False


def is_next_available_banner_present(soup_):
    htm_elems = soup_.findAll("h4", class_="ufss-slotgroup-heading-text a-text-normal")
    for htm_elem in htm_elems:
        txt = get_normalized_text(htm_elem.text)
        if Config.next_avail_patt1 in txt:
            print("is_next_available_banner_present = True")
            return True
    return False


def are_delivery_slots_available(soup):
    return (
        is_next_available_banner_present(soup)
        or some_date_has_availability(soup)
        or not is_delivery_unavailable_banner_present(soup)
    )


# ==================================================================================================


def wf_dlvry_slot_finder_driver(checkout_pg_url):
    """
    slot check driver method
    """
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(checkout_pg_url)
    print(f"sign in and then navigate in the open tab to url={checkout_pg_url}")
    time.sleep(60)

    sobj = SoupObj()

    def soup_refresh():
        time.sleep(4)
        driver.refresh()
        print("refreshed")
        print(driver.current_url)
        html = driver.page_source
        sobj.soup = bs4.BeautifulSoup(html, features="html.parser")

    soup_refresh()

    while not are_delivery_slots_available(sobj.soup):
        print("no delivery slots available")
        soup_refresh()

    print("delivery slots available")
    alert_util("Slots for delivery opened")


if __name__ == "__main__":
    wf_dlvry_slot_finder_driver(Config.wf_checkout_url)
