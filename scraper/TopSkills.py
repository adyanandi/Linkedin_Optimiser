from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter
import time

def get_top_skills(search_query):
    # Prepare the URL for the job role search on Naukri
    url = f"https://www.naukri.com/{search_query.replace(' ', '-')}-jobs?k={search_query.replace(' ', '%20')}"
    
    # Set up Chrome options for headless browsing
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Scroll to load job listings
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)

    # Wait until job cards are loaded
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
        )
    except:
        driver.quit()
        return []

    # Find all job cards and extract skills
    job_cards = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
    all_skills = []

    for card in job_cards:
        try:
            # Find skills in the job card
            skill_list = card.find_elements(By.CSS_SELECTOR, ".row5 ul.tags-gt li.dot-gt.tag-li")
            skills = [s.text.strip().lower() for s in skill_list if s.text.strip()]
            all_skills.extend(skills)
        except:
            continue

    # Get the top 5 most common skills
    top_5_skills = Counter(all_skills).most_common(5)

    # Close the driver after scraping
    driver.quit()

    return top_5_skills








