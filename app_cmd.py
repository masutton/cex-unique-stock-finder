import argparse
import requests
import re
import urllib.request
import time

import numpy as np

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from threading import *

PROGRAM_TITLE = 'CeX Delivery Trick'
PROGRAM_DESCRIPTION = 'Add Product ID, Store and Browser of Choice to Run.\nProgram will then output the various Product IDs for DVD\'s available at only that store as part of the CeX trick.'


def get_rarer_items(storeName, browser):
    url_strings = ["categoryIds=1139&categoryName=DVD+Movies+1+Pound", "categoryIds=1137&categoryName=DVD+Anime+1+Pound", "categoryIds=1134&categoryName=DVD+Sport+1+Pound", "categoryIds=746&categoryName=DVD+Anime"]
    productIds = list()
    if browser == "Chrome":
        print("Loading Chrome...")
        driver = webdriver.Chrome()
    if browser == "Edge":
        print("Loading Edge...")
        driver = webdriver.Edge()
    if browser == "FireFox":
        print("Loading FireFox...")
        driver = webdriver.Firefox()
    print("Loading CeX via Browser to review stock unique to the selected store.")
    for url_string in url_strings:
        print(f"Reviewing for store unique items in the Category for: {url_string.split('=')[2].replace('+', ' ')}")
        url = f"https://uk.webuy.com/search?{url_string}&sortBy=prod_cex_uk_popularity_desc&stores={storeName}"
        driver.get(url)
        time.sleep(10)
        count = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div/div[1]/div[2]/div/div[3]/div[2]/div[3]/div[1]/div/div[1]/p")
        print(count.text)
        if not count.text:
            continue
        count = count.text
        count = int(count.split(" ")[0].replace(",",""))
        if count > 1000:
            continue
        else:
            last = count/17
            if last < 1:
                pages = 1
                last = count
            else:
                last = last - int(np.ceil(count/17) - 1)
                last = int(round(last * 17, 0))
                pages = int(np.ceil(count/17))
            time.sleep(10)
            url = f"https://uk.webuy.com/search?page={pages}&{url_string}&sortBy=prod_cex_uk_popularity_desc&stores={storeName}"
            driver.get(url)
            time.sleep(10)
            i = 1
            while i <= last:
                count = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div/div/div[1]/div[2]/div/div[3]/div[2]/div[3]/div[3]/div/div/div[{i}]")
                soup = BeautifulSoup(count.get_attribute('innerHTML'), "html.parser")
                for a in soup.find_all("a"):
                    productId = re.search(r"id=([0-9A-Za-z]*)", a['href'])
                    productIds.append(productId.group(1))
                i += 1
            time.sleep(2)
    driver.close()
    return productIds


def item_store_lookup(product_id):
    api_url = f"https://wss2.cex.uk.webuy.io/v3/boxes/{product_id}/neareststores?latitude=0&longitude=0"
    api_answer = requests.get(api_url) #Get the product information
    api_answer = api_answer.json() #Convert it to JSON
    try:
        api_answer = api_answer['response']['data']['nearestStores']
        storeList = list()
        for store in api_answer:
            storeList.append(store['storeName'])
        return storeList
    except:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=PROGRAM_TITLE,
        description=PROGRAM_DESCRIPTION)
    parser.add_argument('-p', '--productid')
    parser.add_argument('-s', '--storename')
    parser.add_argument('-b', '--browser', choices=["Edge", "FireFox", "Chrome"], default="Edge")

    args = parser.parse_args()

    product_id = args.productid
    store_name = args.storename
    browser = args.browser

    print(product_id, store_name, browser)

    if not product_id or not store_name or not browser:
        print("Please ensure all variable are declared.")

    storeList = item_store_lookup(product_id)
    
    if not storeList:
        print("Product ID does not appear to exist. Please recheck and try again.")

    if store_name not in storeList:
        print(f"Product does not appear to be available at {store_name}")
    else:
        productIds = get_rarer_items(store_name, browser)
        productIds = list(set(productIds))
        unique_to_store = list()
        print(f"\nReviewing Product IDs to ensure they are unique to {store_name}")
        for id in productIds:
            time.sleep(5)
            temp_stores = item_store_lookup(id)
            temp_unique = 0
            for store in temp_stores:
                if store in storeList and store != store_name:
                    temp_unique = 2
                else:
                    if temp_unique < 2:
                        temp_unique = 1
            if temp_unique == 1:
                unique_to_store.append(id)
        unique_to_store = list(set(unique_to_store))
        print(f"DVD Product ID's unique to {store_name} for ensuring you get {product_id} from {store_name}.")
        for i in unique_to_store:
            print(f"{i}")
