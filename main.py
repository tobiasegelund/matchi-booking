import os
import sys
import datetime
from time import sleep

import schedule
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



load_dotenv()

USERNAME = os.getenv("MATCHI_USER")
PASSWORD = os.getenv("MATCHI_PASSWROD")
SPORT = "5"  # Padel
URL_LOGIN = "https://www.matchi.se/login"
URL_TEMPLATE = "https://www.matchi.se/facilities/S%C3%B8nders%C3%B8HallernesPadelcenter?date={date}&sport={sport}"
NUMBER_OF_RETRIES = 3
# CENTER = "Nordfyns Padel Center"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")  # Ensure no mobile version
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(30)
# set xvfb display since there is no GUI in docker container.
# display = Display(visible=0, size=(800, 600))
# display.start()


def find_next_future_thursday() -> str:
    # We are only interested in Thursdays 14 days from today
    future_date = datetime.date.today() + datetime.timedelta(days=14)

    for i in range(7):
        date = future_date + datetime.timedelta(days=i)
        if date.isoweekday() == 4:
            # return date.strftime("%Y-%m-%d")
            return "2023-02-26"  # TODO: REMOVE
    raise ValueError("Couldn't find a future Thursday. Please contact Tobias")


def retry(func):
    def inner(*args, **kwargs):
        for i in range(NUMBER_OF_RETRIES):
            try:
                func(i)
                break  # Break the retry loop
            except Exception as e:
                if i == NUMBER_OF_RETRIES - 1:
                    sys.exit()
                print(
                    f"... Failed due to: {e}\n... Retry {i + 1} / {NUMBER_OF_RETRIES - 1}."
                )
                continue

    return inner


@retry
def login(*args) -> None:
    driver.get(URL_LOGIN)
    print(f"... Opened {URL_LOGIN}")

    cookie_box = driver.find_element(By.XPATH, '//*[@id="cookiescript_accept"]')
    cookie_box.click()

    username_box = driver.find_element(By.ID, "username")
    password_box = driver.find_element(By.ID, "password")

    username_box.send_keys(USERNAME)
    password_box.send_keys(PASSWORD)

    login_box = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div[3]/form/button"
    )
    login_box.click()
    print(f"... Logged in as {USERNAME}")


def book_court1() -> None:
    xpath = "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/table/tbody/tr[2]/td[2]/table/tbody/tr/td[{row}]"
    court1_18 = xpath.format(row=13)
    court1_19 = xpath.format(row=14)

    for court_hour in [court1_19]:
        court_hour_box = driver.find_element(By.XPATH, court_hour)
        court_hour_box.click()


def book_court2() -> None:
    xpath = "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[{row}]"
    court2_18 = xpath.format(row=13)
    court2_19 = xpath.format(row=14)

    for court_hour in [court2_18]:
        court_hour_box = driver.find_element(By.XPATH, court_hour)
        court_hour_box.click()


@retry
def book(*args) -> None:
    i = args[0]
    date = find_next_future_thursday()
    url = URL_TEMPLATE.format(date=date, sport=SPORT)

    driver.get(url)
    print(f"... Changed page to {url}")

    multi_reserve_box = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[1]/div[2]/div[2]/a",
    )
    multi_reserve_box.click()
    driver.save_screenshot(f"screenshots/{str(i)}.{str(datetime.datetime.now())}.png")

    sleep(i * 3)

    book_court2()
    # book_court1()  # Pop-up interfere with book button (cannot be found because of it)

    # View selected timeslots
    driver.save_screenshot(f"screenshots/{str(i)}.{str(datetime.datetime.now())}.png")

    book_box = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[1]/div[2]/div[2]/div/a[1]",
    )
    book_box.click()
    # Observe the pop-up box
    sleep(i * 3 + 2)
    driver.save_screenshot(f"screenshots/{str(i)}.{str(datetime.datetime.now())}.png")

    confirm_box = driver.find_element(By.XPATH, '//*[@id="btnSubmit"]')
    confirm_box.click()

    sleep(30)
    driver.save_screenshot(f"screenshots/{str(i)}.{str(datetime.datetime.now())}.png")
    sys.exit()


if "__main__" == __name__:
    date = find_next_future_thursday()
    print(f"... Book hours on {date}")

    # login()
    # book()

    schedule.every().day.at("23:59").do(retry(login))
    schedule.every().day.at("00:00").do(retry(book))

    while True:
        schedule.run_pending()
        sleep(0.5)
