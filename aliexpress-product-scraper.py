import time
import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_product_details(url, driver):
    """
    Function to extract product details (name, price, features) from AliExpress page using Selenium.

    Args:
    - url: URL of the AliExpress product page.
    - driver: Selenium WebDriver instance.

    Returns:
    - Dictionary containing 'name', 'price', and 'features' of the product.
    """
    try:
        driver.get(url)

        # Wait for the product name element to be present
        product_name_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-pl="product-title"]')))
        product_name = product_name_elem.text.strip()

        # Extract product price
        price_elem = driver.find_element(By.CSS_SELECTOR, 'div.es--wrap--vZDQqfj')
        price = price_elem.text.strip()

        # Extract product features
        product_features = {}
        features_elem = driver.find_element(By.CLASS_NAME, 'specification--list--fiWsSyv')
        feature_lines = features_elem.find_elements(By.CLASS_NAME, 'specification--line--iUJOqof')

        if feature_lines:
            for line in feature_lines:
                props = line.find_elements(By.CLASS_NAME, 'specification--prop--RejitI8')
                for prop in props:
                    title_elem = prop.find_element(By.CLASS_NAME, 'specification--title--UbVeyic')
                    title = title_elem.find_element(By.TAG_NAME, 'span').text.strip()

                    desc_elem = prop.find_element(By.CLASS_NAME, 'specification--desc--Mz148Bl')
                    description = desc_elem.find_element(By.TAG_NAME, 'span').text.strip()

                    product_features[title] = description

        return {
            'name': product_name,
            'price': price,
            'features': product_features
        }
    except Exception as e:
        print(f"Failed to retrieve product details from {url}: {str(e)}")
        return None

def read_urls_from_file(filename):
    """
    Function to read URLs from a text file.

    Args:
    - filename: Name of the file containing URLs.

    Returns:
    - List of URLs read from the file.
    """
    with open(filename, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

def save_to_csv(data, filename):
    """
    Function to save product details to a CSV file.

    Args:
    - data: List of dictionaries containing product details.
    - filename: Name of the CSV file to save.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Product details saved to '{filename}'")

def main(filename):
    """
    Main function to extract product details from AliExpress and save them to a CSV file.

    Args:
    - filename: Name of the file containing URLs.
    """
    # Setup Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

    # Path to your Chromedriver executable
    chrome_driver_path = 'C:/chromedriver.exe'  # Replace with your Chromedriver path
    service = Service(chrome_driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        urls = read_urls_from_file(filename)
        if not urls:
            print("No valid URLs found in the file.")
            return

        all_product_details = []

        for url in urls:
            product_details = get_product_details(url, driver)
            if product_details:
                all_product_details.append(product_details)

        if all_product_details:
            save_to_csv(all_product_details, 'aliexpress_products.csv')
        else:
            print("No valid product details found.")

    finally:
        driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract and save product details from AliExpress using Selenium.")
    parser.add_argument('filename', type=str, help="Name of the file containing URLs")
    args = parser.parse_args()

    main(args.filename)
