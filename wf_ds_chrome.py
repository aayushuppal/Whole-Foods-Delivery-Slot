#!/usr/bin/env python3.7
# pylint: disable=missing-function-docstring, too-few-public-methods

"""
whole foods delivery slot finder - chrome
"""

import sys
import time
import re
import bs4
import pyttsx3
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

    initial_load_wait = 60
    refresh_wait = 3

    alert_count = 3


PYTTSX_ENGINE = pyttsx3.init()


class SoupObj:
    """
    beautiful soup object container
    """

    def __init__(self):
        self.soup = None


class ChromeDriverSession:
    """
    Singleton for Chrome webdriver
    """

    __instance = None

    @staticmethod
    def get_instance():
        """
        ChromeDriverSession singleton get instance
        """
        if ChromeDriverSession.__instance is None:
            ChromeDriverSession()
        return ChromeDriverSession.__instance

    def __init__(self):
        """
        ChromeDriverSession singleton constructor
        """
        if ChromeDriverSession.__instance is not None:
            raise Exception("This class is a singleton!")

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(Config.wf_checkout_url)
        print(
            f"""
        - Sign in
        - Navigate in the open tab to url={Config.wf_checkout_url}
        - you have {Config.initial_load_wait} seconds
        """
        )
        self.web_driver = driver
        time.sleep(Config.initial_load_wait)
        ChromeDriverSession.__instance = self


def get_normalized_text(txt):
    return Config.whitespaces_regex.sub(" ", txt).strip()


def alert_util(msg):
    for i in range(Config.alert_count):
        PYTTSX_ENGINE.say(msg)
        PYTTSX_ENGINE.runAndWait()
        if i == Config.alert_count - 1:
            break
        time.sleep(1)


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


def wf_dlvry_slot_finder_driver():
    """
    slot check driver method
    """
    driver = ChromeDriverSession.get_instance().web_driver

    sobj = SoupObj()

    def soup_refresh():
        time.sleep(Config.refresh_wait)
        driver.refresh()
        print(f"refreshed {driver.current_url}")
        html = driver.page_source
        sobj.soup = bs4.BeautifulSoup(html, features="html.parser")

    soup_refresh()

    while not are_delivery_slots_available(sobj.soup):
        print("no delivery slots available")
        soup_refresh()

    print("delivery slots available")
    alert_util("Slots for delivery opened")


if __name__ == "__main__":
    EXIT_SESSION = False

    while not EXIT_SESSION:
        wf_dlvry_slot_finder_driver()

        USER_IN = input("Exit Session: Y/N\n")
        if USER_IN.lower() == "y":
            EXIT_SESSION = True

    print("Session finished")
    ChromeDriverSession.get_instance().web_driver.quit()
    sys.exit()
