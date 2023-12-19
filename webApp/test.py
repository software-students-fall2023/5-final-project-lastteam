from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Initialize the Chrome driver
driver = webdriver.Chrome()

# Function to test login
def test_login(username, password):
    driver.get("http://localhost:5001/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    time.sleep(2)  # Wait for page to load
    assert "PokerMain" in driver.current_url

# Function to test change password
def test_change_password(old_password, new_password):
    driver.get("http://localhost:5000/settings/change-password")
    driver.find_element(By.ID, "currentPassword").send_keys(old_password)
    driver.find_element(By.ID, "newPassword").send_keys(new_password)
    driver.find_element(By.ID, "change-password-button").click()
    time.sleep(2)  # Wait for response
    assert "passwordChanged" in driver.current_url

# Function to test change username
def test_change_username(new_username):
    driver.get("http://localhost:5000/settings/change-username")
    driver.find_element(By.ID, "newUsername").send_keys(new_username)
    driver.find_element(By.ID, "change-username-button").click()
    time.sleep(2)  # Wait for response
    assert "usernameChanged" in driver.current_url

# Test Execution
try:
    test_login("testuser", "testpassword")
    test_change_password("testpassword", "newpassword")
    test_change_username("newusername")
finally:
    driver.quit()
