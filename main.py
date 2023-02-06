import os
import datetime
from time import sleep

import schedule
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

# from pyvirtualdisplay import Display

# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait

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
            return "2023-02-18"  # TODO: REMOVE
    raise ValueError("Couldn't find a future Thursday. Please contact Tobias")

def retry(func):
    def inner():
        for i in range(NUMBER_OF_RETRIES):
            try:
                flag = func()
                break  # Break the retry loop
            except Exception:
                print(f"... Failed {i + 1} / {NUMBER_OF_RETRIES}. Retries...")
                continue

        return flag
    return inner

@retry
def login() -> None:
    driver.get(URL_LOGIN)
    print(f"... Opened {URL_LOGIN}")
    driver.implicitly_wait(
        20
    )  # 20 seconds upper limit for page to load relevant elements

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


# def book_court1() -> None:
#     court1_18_19 = "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/table/tbody/tr[2]/td[2]/table/tbody/tr/td[13]"
#     court1_19_20 = "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/table/tbody/tr[2]/td[2]/table/tbody/tr/td[14]"

#     for court_hour in [court1_18_19, court1_19_20]:
#         court_hour_box = driver.find_element(By.XPATH, court_hour)
#         court_hour_box.click()


def book_court2() -> None:
    court2_18_19 = "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[13]"
    court2_19_20 = "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[14]"

    # for court_hour in [court2_18_19, court2_19_20]:
    for court_hour in [court2_18_19]:  # TODO: REMOVE
        court_hour_box = driver.find_element(By.XPATH, court_hour)
        court_hour_box.click()

@retry
def book() -> None:
    date = find_next_future_thursday()
    print(f"... Book hours on {date}")
    url = URL_TEMPLATE.format(date=date, sport=SPORT)

    driver.get(url)
    print(f"... Changed page to {url}")

    multi_reserve_box = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[1]/div[2]/div[2]/a",
    )
    multi_reserve_box.click()

    book_court2()

    book_box = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[3]/section[2]/div[2]/div/div[1]/div[2]/div/div/div[1]/div[2]/div[2]/div/a[1]",
    )
    book_box.click()

    confirm_box = driver.find_element(By.XPATH, '//*[@id="btnSubmit"]')
    confirm_box.click()

    page_state = driver.execute_script("return document.readyState;")
    if page_state == "complete":
        print("... Booked")
        return True
    return False


if "__main__" == __name__:
    # TODO: Outcomment
    # schedule.every().day.at("19:40").do(login)
    # schedule.every().day.at("19:41").do(book)
    # schedule.every().day.at("23:59").do(retry(login))
    # schedule.every().day.at("00:00").do(retry(book))

    while True:
        login()
        flag = book()

        schedule.run_pending()
        if flag:
            break
        sleep(0.5)
