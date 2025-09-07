from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import os
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("naukri_update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def update_resume_on_naukri(username, password):
    driver = None
    try:
        logger.info("Setting up Chrome options...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode when automated
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        logger.info("Initializing WebDriver...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="latest").install()), options=chrome_options)
        driver.maximize_window()
        
        logger.info("Opening Naukri website...")
        driver.get("https://www.naukri.com/")
        time.sleep(random.uniform(2, 5))  # Random delay

        logger.info("Checking for CAPTCHA or blocking...")
        if "CAPTCHA" in driver.page_source or "Access Denied" in driver.page_source:
            logger.warning("CAPTCHA or blocking detected. Taking screenshot for manual review.")
            driver.save_screenshot(f"captcha_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            return False

        logger.info("Waiting for the Login button...")
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@title='Jobseeker Login' and text()='Login']"))
        )
        login_button.click()
        time.sleep(random.uniform(1, 3))

        logger.info("Entering username...")
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your active Email ID / Username']"))
        )
        username_field.send_keys(username)
        time.sleep(random.uniform(1, 3))

        logger.info("Entering password...")
        password_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
        password_field.send_keys(password)
        time.sleep(random.uniform(1, 3))

        logger.info("Clicking on the Login button...")
        login_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_submit_button.click()
        time.sleep(random.uniform(5, 7))

        driver.get('https://www.naukri.com/mnjuser/homepage')
        time.sleep(random.uniform(3, 5))
        logger.info("Opening User's Naukari homepage...")
        logger.info(f"Current page URL: {driver.current_url}")

        driver.get('https://www.naukri.com/mnjuser/profile')
        time.sleep(random.uniform(5, 10))
        logger.info("Navigating to the Profile section...")
        logger.info(f"Current page URL: {driver.current_url}")

        logger.info("Clicking on the 'Update Resume' button...")
        update_resume_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@value='Update resume']"))
        )
        update_resume_button.click()
        time.sleep(random.uniform(2, 4))

        logger.info("Uploading the resume file...")
        # Get script directory and construct resume path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        resume_path = os.path.join(script_dir, "utils", "Akshay_Vinayak.pdf")
        
        if not os.path.exists(resume_path):
            logger.error(f"Resume file not found at: {resume_path}")
            return False
            
        resume_file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        resume_file_input.send_keys(resume_path)
        time.sleep(random.uniform(5, 7))

        logger.info(f"Resume updated successfully on Naukri at: {datetime.datetime.now()}")
        return True

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if driver:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            driver.save_screenshot(f"error_screenshot_{timestamp}.png")
        return False

    finally:
        logger.info("Closing the browser...")
        if driver:
            driver.quit()

def main():
    # Get credentials from environment variables
    username = os.getenv("NAUKRI_USERNAME")
    password = os.getenv("NAUKRI_PASSWORD")
    

    # Check if credentials are available
    if not username or not password:
        logger.error("Missing credentials. Set NAUKRI_USERNAME and NAUKRI_PASSWORD environment variables.")
        sys.exit(1)  # Exit with error code 1
    
    logger.info(f"Starting the resume update process at {datetime.datetime.now()}...")
    success = update_resume_on_naukri(username, password)
    
    if success:
        logger.info("Resume update process completed successfully.")
        sys.exit(0)  # Exit with success code 0
    else:
        logger.warning("Resume update process completed with errors.")
        sys.exit(1)  # Exit with error code 1

if __name__ == "__main__":
    main()