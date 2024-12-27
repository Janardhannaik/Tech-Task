from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import datetime
import uuid

# Initialize Flask app
app = Flask(__name__)

# Setup MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["twitter_trends"]
collection = db["trending_topics"]

# Selenium WebDriver setup
CHROME_DRIVER_PATH = "path_to_chromedriver"  # Replace with your actual ChromeDriver path

def scrape_twitter_trends():
    """Scrape the top 5 trending topics from Twitter."""
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    
    # Open Twitter login page
    driver.get("https://twitter.com/login")
    
    # Login to Twitter
    driver.find_element(By.NAME, "text").send_keys("your_twitter_username\n")
    driver.implicitly_wait(5)
    driver.find_element(By.NAME, "password").send_keys("your_twitter_password\n")
    driver.implicitly_wait(5)

    # Fetch trending topics
    trends = []
    try:
        trending_items = driver.find_elements(By.XPATH, "//span[contains(text(), '#')]")
        trends = [trend.text for trend in trending_items[:5]]  # Get top 5 trends
    except Exception as e:
        print(f"Error while scraping: {e}")
    finally:
        driver.quit()

    # Create a record to store in MongoDB
    record = {
        "_id": str(uuid.uuid4()),  # Unique ID
        "trend1": trends[0] if len(trends) > 0 else "N/A",
        "trend2": trends[1] if len(trends) > 1 else "N/A",
        "trend3": trends[2] if len(trends) > 2 else "N/A",
        "trend4": trends[3] if len(trends) > 3 else "N/A",
        "trend5": trends[4] if len(trends) > 4 else "N/A",
        "timestamp": datetime.datetime.now()  # Current date and time
    }

    # Save the record in MongoDB
    collection.insert_one(record)

    return record

@app.route("/")
def index():
    """Render the main webpage."""
    return render_template("index.html")

@app.route("/run-script")
def run_script():
    """Run the scraping script and return the result."""
    result = scrape_twitter_trends()
    return jsonify(result)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
