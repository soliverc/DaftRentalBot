import csv
import os
import time
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from exceptions import DaftRentalBotLoginError
from generate_data import GenerateLink
from generate_data import generate_end_time


class SetUp:
    def __init__(self):
        load_dotenv(".env")
        self.SECRET_ID = os.environ.get("secretUser")
        self.SECRET_PASSWORD = os.environ.get("secretPassword")
        self.firstname = os.environ.get("firstname")
        self.surname = os.environ.get("surname")
        self.email = os.environ.get("email")
        self.phone = os.environ.get("phone")
        self.message = os.environ.get("message")

        # Create new csv file to log submissions
        self.file = open("logger.csv", "a")
        self.writer = csv.writer(self.file)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def login(self):
        self.driver.get("http://www.daft.ie")
        sleep(1)

        self.driver.maximize_window()
        # Policy Button
        
        self.driver.find_element(
            By.XPATH, '//*[@id="didomi-notice-agree-button"]'
        ).click()
        sleep(3)
        # Sign-in Button
        
        self.driver.find_element(
            By.XPATH, '//*[@id="__next"]/div[2]/header/div/div[2]/div[3]/ul/li/a'
        ).click()
        sleep(3)
        # EmailID field
        self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(
            self.SECRET_ID
        )
        sleep(3)
        # Password field
        self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(
            self.SECRET_PASSWORD
        )
        sleep(3)
        # Sign-in button
        # 
        # old: '//*[@id="kc-login-form"]/div[2]/input'
        self.driver.find_element(
            By.XPATH, '//*[@id="login"]'
        ).click()

        # Checking if error occured after login
        # if self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]"):
        #     raise DaftRentalBotLoginError(
        #         "Incorrect username or password. Please try again."
        #     )

        print("Logged in successfully!")


class Apply(SetUp):
    def apply(self):
        self.login()
        self.applied_url = None
        generate_link = GenerateLink()
        self.link = "https://www.daft.ie/property-for-rent/ireland?rentalPrice_to=1800&location=cork-city&location=cork-city-centre-cork&location=cork-city-suburbs-cork&location=carrigaline-cork&location=ballincollig-cork&location=ovens-cork&numBeds_from=2&sort=publishDateDesc"
        self.applicationProcess()

        # Run automation for this interval of time
        end_time = generate_end_time()

        while time.time() < end_time:
            print(f"Debug 1: self.link value is {self.link}")
            print("going to link")
            sleep(3)
            self.driver.get(self.link)
            sleep(3)

            # Click the latest ad on the page.
            self.latest_ad = self.driver.find_element(
                By.XPATH,
                '//*[@id="__next"]/main/div[3]/div[1]/ul/li[1]/a/div/div[1]/div[2]',
            ).click()
            if self.applied_url != None and self.applied_url != self.driver.current_url:
                self.applicationProcess()
            else:
                print("Already applied for this house.")

        print("Finishing up the process!")

        self.driver.quit()
        self.file.close()

    def checkFeedback(self):
        # Check if there is a feedfack form on the page
        try:
            # Click on close feedback if exists
            self.driver.find_element(By.XPATH, '//*[@id="wootric-close"]').click()
        except:
            print("Feedback form had popped up! I took care of it.")

    def applicationProcess(self):
        print(f"Debug 2: self.link value is {self.link}")
        print("goign to the link")
        sleep(3)
        self.driver.get( "https://www.daft.ie/property-for-rent/ireland?rentalPrice_to=1800&location=cork-city&location=cork-city-centre-cork&location=cork-city-suburbs-cork&location=carrigaline-cork&location=ballincollig-cork&location=ovens-cork&numBeds_from=2&sort=publishDateDesc")
        sleep(3)
        self.checkFeedback()

        # Click the latest ad on the page.
        self.latest_ad = self.driver.find_element(
            By.XPATH,
            '//*[@id="__next"]/main/div[3]/div[1]/ul/li[1]/a/div/div[1]/div[2]',
        ).click()
        self.checkFeedback()

        sleep(3)
        self.applied_url = self.driver.current_url
        
        # save the address
        log_address = self.driver.find_element(
            By.XPATH, '//*[@id="__next"]/main/div[3]/div[1]/div[1]/div/div[2]/h1'
        ).text

        print(log_address)
        if "student" in log_address.lower():
            print("Skipping student accommodation")
            return  # Skip this property
        
        # save price
        log_price = self.driver.find_element(
            By.XPATH,
            '//*[@id="__next"]/main/div[3]/div[1]/div[1]/div/div[2]/div[1]/h2',
        ).text
        print("Price: ", log_price)
        log_price = "EUR " + log_price[1:]
        log_entry = [log_price, log_address, self.applied_url, "Applied"]

        # click on the link that opens a new window
        self.driver.switch_to.active_element
        # Fill the application in pop-up
        # Click on email_button
        self.driver.find_element(
            By.XPATH,
            '//*[@id="__next"]/main/div[3]/div[2]/div/div[1]/div[2]/div[2]/button',
        ).click()
        sleep(3)
        self.checkFeedback()

        # use this to check if this has already been applied for
        already_applied_text = '//*[@id="contact-form-modal"]/div[2]/div[3]/div/div/span/svg'

        # Enter First Name
        self.driver.find_element(By.XPATH, '//*[@id="keyword1"]').send_keys(
            self.firstname
        )

        # Surname
        self.driver.find_element(By.XPATH, '//*[@id="keyword2"]').send_keys(
            self.surname
        )
        self.checkFeedback()

        # Enter Email-ID
        self.driver.find_element(By.XPATH, '//*[@id="keyword3"]').send_keys(
            self.email
        )
        self.checkFeedback()

        # Enter Contact Number
        self.driver.find_element(By.XPATH, '//*[@id="keyword4"]').send_keys(
            self.phone
        )
        self.checkFeedback()
        # Enter Application text
        self.driver.find_element(By.XPATH, '//*[@id="message"]').send_keys(
            self.message
        )

        self.checkFeedback()

        sleep(5)
        # add number of people
        plusOne = '//*[@id="input-wrapper-adultTenants"]/div/div/div/button[2]'
        self.driver.find_element(
            By.XPATH, plusOne
        ).click()
        sleep(2)

        # specify no pets
        noPets = '//*[@id="hasPets-item-1"]'
        # Click no pets
        self.driver.find_element(
            By.XPATH, noPets
        ).click()
        sleep(2)

        # Send the applicaiton
        self.driver.find_element(
            By.XPATH, '//*[@id="contact-form-modal"]/div[2]/form/div/div[9]/div/button/div/span'
        ).click()
        sleep(2)

        self.checkFeedback()

        # Close the window
        self.driver.find_element(
            By.XPATH, '//*[@id="contact-form-modal"]/div[1]/button'
        ).click()

        self.checkFeedback()

        try:
            # Check if already applied
            text = self.driver.find_element(
                By.XPATH, '//*[@id="__next"]/div[1]/div'
            ).text
            if text == "Sorry, something went wrong.":
                print("Already applied for this house!")
        except:
            self.writer.writerow(log_entry)
            print("Applied for a house!")
        # Wait 10 seconds till you apply for the next one
        sleep(10)


run = Apply()
run.apply()
