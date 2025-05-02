from selenium import webdriver
import time
import pickle

driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/login"
           )
input("Login manually, then press Enter here...")
pickle.dump(driver.get_cookies(), open("cookies/linkedin_cookies.pkl", "wb"))
driver.quit()
