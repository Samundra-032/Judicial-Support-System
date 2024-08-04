from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import os

# Load the initial data from Excel
file_path = "./courtdata_update.xlsx"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"{file_path} not found. Please run the first script to generate the Excel file.")

df = pd.read_excel(file_path)

# Setup WebDriver
chrome_driver_path = "/home/oceanic/.wdm/drivers/chromedriver/linux64/127.0.6533.88/chromedriver-linux64/chromedriver"
driver = webdriver.Chrome(service=Service(chrome_driver_path))

# Define the column for the additional data
df['आदेश /फैसलाको किसिम'] = None

# Define a WebDriverWait instance
wait = WebDriverWait(driver, 10)

# Loop through each case in the DataFrame
for index, row in df.iterrows():
    case_no = row['registration_no']  # Adjusted for the actual column name
    driver.get("https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=107213")
    
    try:
        # Enter the case number
        case_input = wait.until(EC.element_to_be_clickable((By.ID, 'regno')))
        case_input.send_keys(case_no)
        
        # Click the search button
        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.btn.btn-primary[value="    खोज्ने     "]')))
        search_button.click()
        
        # Wait for the case details link and navigate to it
        case_details_link = wait.until(EC.presence_of_element_located((By.XPATH, "//td[@class='nepali whbrd']//a[contains(text(),'मुद्दाको बिस्तृत विवरण')]"))).get_attribute('href')
        driver.get(case_details_link)
        
        # Extract the desired value from the table
        details_table = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'पेशी को विवरण')]/following::table[1]")))
        rows = details_table.find_elements(By.TAG_NAME, "tr")
        last_row = rows[-1]
        columns = last_row.find_elements(By.TAG_NAME, "td")
        case_type = columns[-1].text.strip()
        df.at[index, 'आदेश /फैसलाको किसिम'] = case_type
    
    except TimeoutException as e:
        print(f"Timed out processing case number {case_no}: {str(e)}")

# Save the updated DataFrame to Excel
df.to_excel(file_path, index=False)

# Close the WebDriver
time.sleep(5)
driver.quit()
