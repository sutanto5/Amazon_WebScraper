import time
import pandas as pd
import re  # Import regex module to extract numbers safely
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import KEYS

# Replace with your Amazon credentials
AMAZON_EMAIL = KEYS.EMAIL
AMAZON_PASSWORD = KEYS.PSWD
OUTPUT_FILE = KEYS.CSV  # The file to store all reviews

# Set up Selenium WebDriver
options = Options()
options.headless = False  # Change to True for headless mode
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Function to log into Amazon
def amazon_login():
    """Logs into Amazon and navigates to the reviews page."""
    driver.get(KEYS.URL)
    time.sleep(3)

    # Enter email
    email_input = driver.find_element(By.ID, "ap_email")
    email_input.send_keys(AMAZON_EMAIL)
    email_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # Enter password
    password_input = driver.find_element(By.ID, "ap_password")
    password_input.send_keys(AMAZON_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    # Handle CAPTCHA manually
    input("Solve CAPTCHA if needed, then press Enter to continue...")

    print("Login successful!")

# Function to scrape Amazon reviews including username, review date, rating, and review text
def scrape_reviews():
    """Scrapes customer reviews including User Name, Review Date, Review Rating, and Review Body."""
    driver.get(KEYS.BODY)
    time.sleep(5)

    first_page = True  # Track whether it's the first page (for CSV header handling)

    while True:
        reviews = []
        print("Scraping current page...")

        # Find all review containers where ID starts with 'customer_review-'
        review_containers = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'customer_review-')]")
        print(f"Found {len(review_containers)} reviews on this page.")

        for review in review_containers:
            try:
                # Extract User Name
                user_name = review.find_element(By.XPATH, ".//*[contains(@class, 'a-profile-name')]").text.strip()
                
                # Extract Review Date
                review_date = review.find_element(By.XPATH, ".//*[contains(@class, 'review-date')]").text.strip()

                # Extract Review Rating using a robust XPath
                try:
                    rating_element = review.find_elements(By.XPATH, ".//i[contains(@class, 'review-rating')]/span")
                    print("This is the rating: " + rating_element)
                    if rating_element:
                        rating_text = rating_element[0].text.strip()  # Get the text from span
                        rating_match = re.findall(r"[\d.]+", rating_text)  # Extract numbers (e.g., "5.0" from "5.0 out of 5 stars")
                        rating = float(rating_match[0]) if rating_match else None  # Convert to float
                    else:
                        rating = None  # If no rating exists
                except Exception as e:
                    print(f"Error extracting rating: {e}")
                    rating = None  # Set rating as None if missing
                
                # Extract Review Body
                body = review.find_element(By.XPATH, ".//*[contains(@class, 'review-text-content')]")
                review_text = body.text.strip()
                
                # Save data
                reviews.append({
                    "User Name": user_name,
                    "Review Date": review_date,
                    "Review Rating": rating,  # Numerical rating
                    "Review Body": review_text
                })
            except Exception as e:
                print(f"Skipping review due to error: {e}")
                continue

        # Append data to a single CSV file
        df = pd.DataFrame(reviews)
        if first_page:
            df.to_csv(OUTPUT_FILE, mode='w', index=False)  # Overwrite if first page
            first_page = False  # Next pages will append
        else:
            df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)  # Append for subsequent pages

        print(f"Saved reviews to {OUTPUT_FILE}.")

        # Try to go to the next page
        try:
            next_button = driver.find_element(By.XPATH, "//li[@class='a-last']/a")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)
        except:
            print("No more pages. Exiting loop.")
            break  

    driver.quit()
    print("Scraping complete.")

# Run the login function first
amazon_login()

# Then scrape reviews
scrape_reviews()
