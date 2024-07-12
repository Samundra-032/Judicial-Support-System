from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import time
import os

from nepali_datetime import date
from datetime import timedelta

# Ignoring SSL errors if they occur
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://supremecourt.gov.np/cp/#listTable")

# Wait to load site
wait = WebDriverWait(driver, 10)

# Select Enter the अदालत
court_type = wait.until(EC.element_to_be_clickable((By.NAME, 'court_type')))
court_type.send_keys('सर्वोच्च अदालत')

# Select अदालतको नाम
court_name = wait.until(EC.element_to_be_clickable((By.NAME, 'court_id')))
court_name.send_keys('सर्वोच्च अदालत')

start_date = date(2070, 3, 21)
final_end_date = date(2070, 3, 31)

while start_date <= final_end_date:
    # Convert the Nepali date to a string
    darta_date_str = start_date.strftime('%Y-%m-%d')
    
    darta_date = wait.until(EC.element_to_be_clickable((By.NAME, 'darta_date')))
    darta_date.clear()
    darta_date.send_keys(darta_date_str)

    # Click खोज्नु होस्
    try:
        submit_button = wait.until(EC.element_to_be_clickable((By.NAME, 'submit')))
        ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
    except TimeoutException:
        print("Timed out waiting for submit button to be clickable.")
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", submit_button)

    # Wait until the table is present and rows are loaded
    try:
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        rows = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
    except TimeoutException:
        print(f"Table not found for date {darta_date_str}. Skipping to next date.")
        start_date += timedelta(days=1)
        continue

    data = []

    for i, row in enumerate(rows):
        cols = row.find_elements(By.TAG_NAME, 'td') if row.find_elements(By.TAG_NAME, 'td') else row.find_elements(By.TAG_NAME, 'th')

        row_data = []
        has_link = False

        for col in cols:
            link = col.find_element(By.TAG_NAME, 'a') if col.find_elements(By.TAG_NAME, 'a') else None

            if link:
                row_data.append(link.get_attribute('href'))
                has_link = True
            else:
                row_data.append(col.text)

        if i == 0:
            header = row_data
        else:
            if has_link:
                data.append(row_data)

    df = pd.DataFrame(data, columns=header) 

    file_path = "./courtdata.xlsx"

    if os.path.exists(file_path):
        ex_df = pd.read_excel(file_path)
        combined_df = pd.concat([ex_df, df], ignore_index=True)
    else:
        combined_df = df
    combined_df.to_excel(file_path, index=False)

    print(f"Data for date {darta_date_str} scraped successfully.")
    start_date += timedelta(days=1)

time.sleep(5)
driver.quit()
