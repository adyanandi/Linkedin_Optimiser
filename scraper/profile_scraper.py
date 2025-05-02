# scraper/profile_scraper.py


import json
import time
import re
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# Add root directory to sys.path so utils module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cookies_handler import load_cookies
from utils.human_action import human_scroll, random_delay

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")  # Headless mode
    options.add_argument("--disable-gpu")   # Optional but recommended
    options.add_argument("--window-size=1920,1080")  # Required for some websites to load correctly
    options.add_argument("--log-level=3")  # Suppress logs
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_profile_data(driver, profile_url):
    driver.get("https://www.linkedin.com")
    load_cookies(driver, "cookies/linkedin_cookies.pkl")  # Load LinkedIn session cookies
    driver.get(profile_url)
    time.sleep(2)

    # Human-like scroll
    human_scroll(driver)
    random_delay()

    data = {}

    # Extract Name
    try:
        name = driver.find_element(By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]').text
        data['Name'] = name
    except:
        data['Name'] = None

    # Extract Headline
    try:
        headline = driver.find_element(By.XPATH, '//div[contains(@class, "text-body-medium break-words")]').text
        data['Headline'] = headline
    except:
        data['Headline'] = None

    # Extract Location
    try:
        location = driver.find_element(By.XPATH, '//span[contains(@class, "text-body-small inline t-black--light break-words")]').text
        data['Location'] = location
    except:
        data['Location'] = None

    # Extract About Section
    try:
    # Wait for the About section to appear
     about_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//section[contains(@class, "artdeco-card") and .//span[text()="About"]]'))
     )

    # Click "See more" if present
     try:
        see_more_button = about_section.find_element(By.XPATH, './/button[contains(text(), "See more")]')
        driver.execute_script("arguments[0].click();", see_more_button)  # Click using JavaScript for reliability
     except:
        pass  # No "See more" button found, continue

    # Wait for the full text to load
     WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//section[contains(@class, "artdeco-card") and .//span[text()="About"]]'))
     )

    # Extract text again after clicking "See more"
     about_text = about_section.text.replace("About", "").strip()

    # Ensure "…see more" is removed if still present
     if "…see more" in about_text:
        about_text = about_text.replace("…see more", "").strip()

     data['About'] = about_text

    except Exception as e:
     print(f"[!] Error scraping About section: {e}")
     data['About'] = None

    # Extract Experience Section
    try:
        experience_section = driver.find_element(By.XPATH, '//section[.//span[contains(text(),"Experience")]]')
        experience_items = experience_section.find_elements(By.XPATH, './/li[contains(@class, "artdeco-list__item")]')

        experience_data = []
        seen_entries = set()

        for item in experience_items:
            lines = item.text.strip().split("\n")
            cleaned = "\n".join(line for i, line in enumerate(lines) if i == 0 or line != lines[i - 1])
            if cleaned and cleaned not in seen_entries:
                experience_data.append(cleaned)
                seen_entries.add(cleaned)

        data['Experience'] = experience_data
    except:
        data['Experience'] = None

   # NEW: Extract Education Section
    try:
        education_section = driver.find_element(By.XPATH, '//section[.//span[contains(text(),"Education")]]')
        education_items = education_section.find_elements(By.XPATH, './/li[contains(@class, "artdeco-list__item")]')
    
        education_data = []
        for item in education_items:
            edu_text = item.text.strip()
            if edu_text:
                lines = edu_text.split("\n")
                # Remove duplicate consecutive lines
                cleaned_lines = [line for i, line in enumerate(lines) if i == 0 or line != lines[i - 1]]
            
                institute = cleaned_lines[0] if len(cleaned_lines) > 0 else ''
                duration = ''
                gpa_or_percentage = ''
            
            # Find duration and percentage/CGPA from the rest of the lines
                for line in cleaned_lines:
                    if any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                        duration = line
                    if 'CGPA' in line or 'Grade' in line or '%' in line:
                        gpa_or_percentage = line
            
                education_data.append({
                    'Institute': institute,
                    'Duration': duration,
                    'GPA_or_Percentage': gpa_or_percentage
                })

            data['Education'] = education_data

    except Exception as e:
          data['Education'] = None
 

    # ---- Extract Skills Section ----
    try:
        skills_url = profile_url.rstrip('/') + "/details/skills/"
        print(f"[*] Navigating to Skills page: {skills_url}")
        driver.get(skills_url)
        time.sleep(3)
        human_scroll(driver)

        print("[*] Extracting skills from the page...")
        skill_elements = driver.find_elements(By.XPATH, "//li[contains(@class,'pvs-list__paged-list-item')]//span[@aria-hidden='true']")
        raw_skills = [elem.text.strip() for elem in skill_elements if elem.text.strip()]

        # Fallback if no skills found
        if not raw_skills:
            print("[!] No skills found using standard XPath. Trying fallback method...")
            all_spans = driver.find_elements(By.TAG_NAME, "span")
            raw_skills = [elem.text.strip() for elem in all_spans if elem.text.strip()]

        # Cleanup and filter
        blacklist_keywords = [
            "endorsement", "endorsements", "certified", "certification", "course", "intern", "E-Learning",
            "project", "university", "college", "institute", "mahendergarh", "iit", "dr. angela yu", "certificate",
            "central university", "development centre", "project intern", "3 endorsements", "2 endorsements", "1 endorsement"
        ]

        cleaned_skills = []
        seen = set()

        for skill in raw_skills:
            skill_lower = skill.lower()
            if any(kw in skill_lower for kw in blacklist_keywords):
                continue
            if re.search(r"\d+\s+endorsement", skill_lower):
                continue
            if len(skill.split()) > 6:
                continue
            if not skill.isascii():
                continue
            if skill not in seen:
                seen.add(skill)
                cleaned_skills.append(skill)

        data['Skills'] = cleaned_skills

    except Exception as e:
        print("[!] Error extracting skills:", e)
        data['Skills'] = None


    ##------Extract project section------
    try:
     projects_url = profile_url.rstrip('/') + "/details/projects/"
     print(f"[*] Navigating to Projects page: {projects_url}")
     driver.get(projects_url)
     time.sleep(3)
     human_scroll(driver)

     projects_data = []
     project_items = driver.find_elements(By.XPATH, "//li[contains(@class,'pvs-list__paged-list-item')]")

     for item in project_items:
        project_name = ""
        duration = ""
        description = ""

        try:
            project_name = item.find_element(By.XPATH, ".//span[@aria-hidden='true']").text.strip()
        except:
            pass

        try:
            duration = item.find_element(By.XPATH, ".//span[contains(@class,'t-14 t-normal')]").text.strip()
        except:
            pass

        try:
          # Updated XPath to match the correct container
           description_element = item.find_element(By.XPATH, ".//div[contains(@class, 'pvs-entity__sub-components')]")  
           description = description_element.text.strip() if description_element.text else ""
        except NoSuchElementException:
                print("[!] Project description not found.")
                description = ""
        except:
            pass

        if project_name:
            projects_data.append({
                'Project Name': project_name,
                'Duration': duration,
                'Description': description
            })

     data['Projects'] = projects_data if projects_data else None  # Assign None if no projects found

    except Exception as e:
     print(f"[!] Error extracting projects: {e}")
     data['Projects'] = None    

    #----- Extract certifications----
    try:
        certifications_url = profile_url.rstrip('/') + "/details/certifications/"
        print(f"[*] Navigating to Certifications page: {certifications_url}")
        driver.get(certifications_url)
        time.sleep(3)
        human_scroll(driver)

        certifications_data = []
        cert_items = driver.find_elements(By.XPATH, "//li[contains(@class,'pvs-list__paged-list-item')]")

        for item in cert_items:
            cert_name = ""
            issuing_org = ""
            issue_date = ""

            # Extract Certification Name
            try:
                cert_name_element = item.find_element(By.XPATH, ".//span[@aria-hidden='true']")
                cert_name = cert_name_element.text.strip() if cert_name_element else ""
            except NoSuchElementException:
                pass

            # Extract Issuing Organization (Fixing duplication issue)
            try:
                issuing_org_elements = item.find_elements(By.XPATH, ".//span[contains(@class,'t-14 t-normal')]")
                issuing_org = ", ".join(set([elem.text.strip() for elem in issuing_org_elements if elem.text.strip()]))
            except NoSuchElementException:
                pass

            # Extract Issue Date
            try:
                issue_date_elements = item.find_elements(By.XPATH, ".//span[contains(@class,'t-14 t-normal')]/following-sibling::span")
                issue_date = ", ".join(set([elem.text.strip() for elem in issue_date_elements if elem.text.strip()]))
            except NoSuchElementException:
                pass

            # Append to the list only if a certification name is found
            if cert_name:
                certifications_data.append({
                    'Certification': cert_name,
                    'Issued By': issuing_org,
                    'Date': issue_date
                })

        # Store in data dictionary
        data['Certifications'] = certifications_data if certifications_data else None

    except Exception as e:
        print(f"[!] Error extracting certifications: {e}")
        data['Certifications'] = None 

    #---Awards and honors----
    try:
        honors_url = profile_url.rstrip('/') + "/details/honors/"
        print(f"[*] Navigating to Honors & Awards page: {honors_url}")
        driver.get(honors_url)
        time.sleep(3)
        human_scroll(driver)

        honors_data = []
        honor_items = driver.find_elements(By.XPATH, "//li[contains(@class,'pvs-list__paged-list-item')]")

        for item in honor_items:
            honor_name = ""
            issuing_org = ""
            

            # Extract Honor/Award Name
            try:
                honor_name_element = item.find_element(By.XPATH, ".//span[@aria-hidden='true']")
                honor_name = honor_name_element.text.strip() if honor_name_element else ""
            except NoSuchElementException:
                pass

            # Extract Issuing Organization (Fix duplication)
            try:
                issuing_org_element = item.find_element(By.XPATH, ".//span[contains(@class,'t-14 t-normal')]")
                issuing_org = issuing_org_element.text.strip().split("\n")[0]  # Take only the first line
            except NoSuchElementException:
                pass

            

            # Append to the list only if an honor/award name is found
            if honor_name:
                honors_data.append({
                    'Honor/Award': honor_name,
                    'Issued By': issuing_org,
                    
                })

        # Store in data dictionary
        data['Honors & Awards'] = honors_data if honors_data else None

    except Exception as e:
        print(f"[!] Error extracting honors & awards: {e}")
        data['Honors & Awards'] = None
    

    return data


# ---- Runner ----
if __name__ == "__main__":
    profile_url = input("Enter LinkedIn profile URL: ").strip()
    driver = setup_driver()
    profile_data = scrape_profile_data(driver, profile_url)
    driver.quit()

    # Save to a TXT file
    with open("profile_data.txt", "w", encoding="utf-8") as file:
        file.write(json.dumps(profile_data, indent=4, ensure_ascii=False))

    print("\n✅ Profile data saved to profile_data.txt successfully!")



