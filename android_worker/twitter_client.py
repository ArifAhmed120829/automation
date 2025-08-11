import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

class TwitterAutomation:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.driver = None
        self.logged_in = False
        
    def setup_driver(self):
        """Setup Chrome driver for Android-like behavior"""
        options = Options()
        
        # Mobile user agent
        ua = UserAgent()
        mobile_ua = ua.chrome
        options.add_argument(f'--user-agent={mobile_ua}')
        
        # Mobile viewport
        options.add_argument('--window-size=375,667')  # iPhone size
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # For headless operation (uncomment in production)
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self) -> bool:
        """Login to Twitter"""
        try:
            if not self.driver:
                self.setup_driver()
            
            # Go to Twitter login
            self.driver.get("https://twitter.com/i/flow/login")
            
            # Wait for username field
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            
            # Enter username
            username_field.send_keys(self.username)
            time.sleep(random.uniform(1, 2))
            
            # Click next
            next_button = self.driver.find_element(By.XPATH, '//span[text()="Next"]/..')
            next_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_field.send_keys(self.password)
            time.sleep(random.uniform(1, 2))
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, '//span[text()="Log in"]/..')
            login_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Check if login successful
            try:
                # Look for home timeline or profile elements
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Home timeline"]'))
                    )
                )
                self.logged_in = True
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def like_tweet(self, tweet_url: str) -> dict:
        """Like a tweet"""
        try:
            if not self.logged_in and not self.login():
                return {"success": False, "error": "Login failed"}
            
            # Navigate to tweet
            self.driver.get(tweet_url)
            time.sleep(random.uniform(2, 4))
            
            # Find like button (heart icon)
            like_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="like"]'))
            )
            
            # Random delay to simulate human behavior
            time.sleep(random.uniform(1, 3))
            
            # Click like button
            like_button.click()
            
            # Wait a bit to ensure action completed
            time.sleep(random.uniform(1, 2))
            
            return {
                "success": True,
                "action": "like",
                "tweet_url": tweet_url,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to like tweet: {str(e)}",
                "tweet_url": tweet_url
            }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
