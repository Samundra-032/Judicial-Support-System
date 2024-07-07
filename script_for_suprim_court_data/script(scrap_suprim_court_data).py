from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import pandas as pd
import time

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://supremecourt.gov.np/cp/#listTable")

# wait to load site
wait = WebDriverWait(driver, 10)

# Select  Enter the अदालत 
court_type = wait.until(EC.element_to_be_clickable((By.NAME, 'court_type')))
court_type.send_keys('सर्वोच्च अदालत')

try:
    popup_close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.popup-close-button-css')))  # Adjust the CSS selector as needed
    popup_close_button.click()
except TimeoutException:
    print("Popup did not appear or close button not found.")

# Select अदालतको नाम
court_type = wait.until(EC.element_to_be_clickable((By.NAME, 'court_id')))
court_type.send_keys('सर्वोच्च अदालत')

# Enter the मुद्दा दर्ता मिति
darta_date = wait.until(EC.element_to_be_clickable((By.NAME, 'darta_date')))
darta_date.send_keys('2070-01-02')

#click खोज्नु होस्
try:
    submit_button = wait.until(EC.element_to_be_clickable((By.NAME, 'submit')))
    ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
except TimeoutException:
    print("Timed out waiting for submit button to be clickable.")
except ElementClickInterceptedException:
    driver.execute_script("arguments[0].click();", submit_button)

#start scraping
time.sleep(20)  
table = driver.find_element(By.TAG_NAME, 'table')
rows = table.find_elements(By.TAG_NAME, 'tr')

data = []
for row in rows:
    cols = row.find_elements(By.TAG_NAME, 'td') if row.find_elements(By.TAG_NAME, 'td') else row.find_elements(By.TAG_NAME, 'th')
    row_data = []
    for col in cols:
        # Check links
        link = col.find_element(By.TAG_NAME, 'a') if col.find_elements(By.TAG_NAME, 'a') else None
        if link:
            row_data.append(link.get_attribute('href'))
        else:
            row_data.append(col.text)
    data.append(row_data)

df = pd.DataFrame(data[1:], columns=data[0])
df.to_excel('./Case_details.xlsx', index=False)

time.sleep(5)
driver.quit()
