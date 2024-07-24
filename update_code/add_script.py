from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import os

# Load the initial data from Excel
# file_path = "./dataset.xlsx"
file_path = "./full_courtdata.xlsx"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"{file_path} not found. Please run the first script to generate the Excel file.")

df = pd.read_excel(file_path)

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define the column for the additional data
df['आदेश /फैसलाको किसिम'] = None

# Extract additional data from the second link
wait = WebDriverWait(driver, 10)
for index, row in df.iterrows():
    case_no = row['दर्ता नं.']
    driver.get("https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=107213")
    
    # Enter the मुद्दा नं in the appropriate form field
    try:
        case_input = wait.until(EC.element_to_be_clickable((By.ID, 'regno')))
        case_input.send_keys(case_no)
    except TimeoutException:
        print(f"Timed out waiting for case input for case number {case_no}")

    # Click the खोज्ने button
    try:
        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.btn.btn-primary[value="    खोज्ने     "]')))
        search_button.click()
    except TimeoutException:
        print(f"Timed out waiting for search button to be clickable for case number {case_no}")

    # Wait for the table to be displayed and extract the link
    try:
        case_details_link = wait.until(EC.presence_of_element_located((By.XPATH, "//td[@class='nepali whbrd']//a[contains(text(),'मुद्दाको बिस्तृत विवरण')]"))).get_attribute('href')
        driver.get(case_details_link)
    except TimeoutException:
        print(f"Timed out waiting for case details link for case number {case_no}")

    # Extract the आदेश /फैसलाको किसिम value
    try:
        # Find the "पेशी को विवरण" table
        details_table = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'पेशी को विवरण')]/following::table[1]")))
        rows = details_table.find_elements(By.TAG_NAME, "tr")
        last_row = rows[-1]
        columns = last_row.find_elements(By.TAG_NAME, "td")
        case_type = columns[-1].text.strip()
        df.at[index, 'आदेश /फैसलाको किसिम'] = case_type
    except TimeoutException:
        print(f"Timed out waiting for case details for case number {case_no}")

# Save to Excel
df.to_excel(file_path, index=False)

time.sleep(5)
driver.quit()
