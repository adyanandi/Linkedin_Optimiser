# utils/human_actions.py
import time
import random

def human_scroll(driver):
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    while current_position < scroll_height:
        increment = random.randint(100, 300)
        current_position += increment
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(random.uniform(0.5, 1.5))

def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))
