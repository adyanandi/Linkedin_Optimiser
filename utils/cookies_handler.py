# utils/cookie_handler.py
import pickle

def save_cookies(driver, filepath):
    with open(filepath, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, filepath):
    with open(filepath, "rb") as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)
