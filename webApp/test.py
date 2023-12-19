from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize the Chrome driver
driver = webdriver.Chrome()

def test_register(username, password):
    driver.get("http://localhost:5001/register")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "register-button").click()
    time.sleep(2)  

# Function to test login
def test_login(username, password):
    driver.get("http://localhost:5001/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    time.sleep(2)  # Wait for page to load

# Function to test change password
def test_change_password(old_password, new_password):
    driver.get("http://localhost:5001/settings/change-password")
    driver.find_element(By.ID, "currentPassword").send_keys(old_password)
    driver.find_element(By.ID, "newPassword").send_keys(new_password)
    driver.find_element(By.ID, "change-password-button").click()
    time.sleep(2)  # Wait for response

# Function to test change username
def test_change_username(new_username):
    driver.get("http://localhost:5001/settings/change-username")
    driver.find_element(By.ID, "newUsername").send_keys(new_username)
    driver.find_element(By.ID, "change-username-button").click()
    time.sleep(2)  # Wait for response

# Test Execution
try:
    test_register("newtestuser12", "newtestpassword12")
    test_login("newtestuser12", "newtestpassword12")
    test_change_password("newtestpassword12", "updatednewpassword13133")
    test_change_username("updatednewusername1023")
finally:
    driver.quit()
