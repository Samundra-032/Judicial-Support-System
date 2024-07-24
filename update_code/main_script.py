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

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://supremecourt.gov.np/cp/#listTable")

# wait to load site
wait = WebDriverWait(driver, 10)

# Select Enter the अदालत
court_type = wait.until(EC.element_to_be_clickable((By.NAME, 'court_type')))
court_type.send_keys('सर्वोच्च अदालत')

# Select अदालतको नाम
court_name = wait.until(EC.element_to_be_clickable((By.NAME, 'court_id')))
court_name.send_keys('सर्वोच्च अदालत')

# Enter the मुद्दा दर्ता मिति
darta_date = wait.until(EC.element_to_be_clickable((By.NAME, 'darta_date')))
darta_date.send_keys('2070-01-02')

# click खोज्नु होस्
try:
    submit_button = wait.until(EC.element_to_be_clickable((By.NAME, 'submit')))
    ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
except TimeoutException:
    print("Timed out waiting for submit button to be clickable.")
except ElementClickInterceptedException:
    driver.execute_script("arguments[0].click();", submit_button)

# start scraping
time.sleep(20)
table = driver.find_element(By.TAG_NAME, 'table')
rows = table.find_elements(By.TAG_NAME, 'tr')

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

df = pd.DataFrame(data[1:], columns=header)

# Define the column for the additional data
df['आदेश /फैसलाको किसिम'] = None

# Extract additional data from the second link
for index, row in df.iterrows():
    case_no = row['दर्ता नं.']
    detail_url = f"https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno={case_no}"
    
    driver.get(detail_url)
    
    try:
        case_type = wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'आदेश /फैसलाको किसिम')]//following-sibling::td"))).text
        df.at[index, 'आदेश /फैसलाको किसिम'] = case_type
    except TimeoutException:
        print(f"Timed out waiting for case details for case number {case_no}")

# Save to Excel
file_path = "./dataset.xlsx"

if os.path.exists(file_path):
    ex_df = pd.read_excel(file_path)
    combined_df = pd.concat([ex_df, df], ignore_index=True)
else:
    combined_df = df
combined_df.to_excel(file_path, index=False)

time.sleep(5)
driver.quit()
