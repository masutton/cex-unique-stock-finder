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

import tkinter
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Custom CeX Product Lookup")
        self.geometry(f"{1280}x{720}")
        self.minsize(640, 360)
        self.maxsize(1280, 720)

        # configure grid layout (4x4)
        self.grid_columnconfigure((1,2,3), weight=1)
        # self.grid_columnconfigure((2, 3), weight=0)
        # self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=0)
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=2, column=0, padx=20, pady=(10, 10))

        self.radiobutton_frame = customtkinter.CTkFrame(self.sidebar_frame)
        self.radiobutton_frame.grid(row=3, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Select Browser:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, columnspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Product ID")
        self.entry.grid(row=2, column=1, columnspan=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.entry1 = customtkinter.CTkEntry(self, placeholder_text="Product Name")
        self.entry1.grid(row=2, column=2, columnspan=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.entry2 = customtkinter.CTkEntry(self, placeholder_text="Store Name")
        self.entry2.grid(row=2, column=3, columnspan=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.thread_updates)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.main_button_1.configure(text = "Search")
        
        self.radio_button_1.configure(text = "Chrome")
        self.radio_button_2.configure(text = "Edge")
        self.radio_button_3.configure(text = "FireFox")

    def get_rarer_items(self, storeName):
        url_strings = ["categoryIds=1139&categoryName=DVD+Movies+1+Pound", "categoryIds=1137&categoryName=DVD+Anime+1+Pound", "categoryIds=1134&categoryName=DVD+Sport+1+Pound", "categoryIds=746&categoryName=DVD+Anime"]
        productIds = list()
        browserId = self.radio_var.get()
        if browserId == 0:
            print("Chrome")
            driver = webdriver.Chrome()
        if browserId == 1:
            print("Edge")
            driver = webdriver.Edge()
        if browserId == 2:
            print("FireFox")
            driver = webdriver.Firefox()
        self.textbox.insert("end", "\nLoading CeX via Browser to review stock unique to the selected store.")
        for url_string in url_strings:
            self.textbox.insert("end", f"\nReviewing for store unique items in the Category for: {url_string.split('=')[2].replace('+', ' ')}")
            url = f"https://uk.webuy.com/search?{url_string}&sortBy=prod_cex_uk_popularity_desc&stores={storeName}"
            driver.get(url)
            time.sleep(10)
            count = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div/div[1]/div[2]/div/div[3]/div[2]/div[3]/div[1]/div/div[1]/p")
            print(count.text)
            if not count.text:
                continue
            count = count.text
            count = int(count.split(" ")[0].replace(",",""))
            print(f"Count - {count}")
            if count > 1000:
                continue
            else:
                last = count/17
                print(f"Last = {last}")
                if last < 1:
                    pages = 1
                    last = count
                else:
                    last = last - int(np.ceil(count/17) - 1)
                    print(f"Last = {last}")
                    last = int(round(last * 17, 0))
                    print(f"Last = {last}")
                    pages = int(np.ceil(count/17))
                print(f"Last = {last}")
                print(f"Pages = {pages}")
                time.sleep(10)
                url = f"https://uk.webuy.com/search?page={pages}&{url_string}&sortBy=prod_cex_uk_popularity_desc&stores={storeName}"
                driver.get(url)
                time.sleep(10)
                i = 1
                while i <= last:
                    count = driver.find_element(By.XPATH, f"/html/body/div[1]/div/main/div/div/div[1]/div[2]/div/div[3]/div[2]/div[3]/div[3]/div/div/div[{i}]")
                    # print(count.get_attribute('innerHTML'))
                    soup = BeautifulSoup(count.get_attribute('innerHTML'), "html.parser")
                    for a in soup.find_all("a"):
                        productId = re.search(r"id=([0-9A-Za-z]*)", a['href'])
                        productIds.append(productId.group(1))
                    i += 1
                time.sleep(2)
        driver.close()
        return productIds
        
    def thread_updates(self):
        t = Thread(target=self.open_input_dialog_event)
        t.start()
    
    def item_store_lookup(self, product_id):
        api_url = f"https://wss2.cex.uk.webuy.io/v3/boxes/{product_id}/neareststores?latitude=0&longitude=0"
        api_answer = requests.get(api_url) #Get the product information
        api_answer = api_answer.json() #Convert it to JSON
        try:
            api_answer = api_answer['response']['data']['nearestStores']
            return api_answer
        except:
            return False
        
    def open_input_dialog_event(self):
        self.main_button_1.configure(state="disabled")
        self.radio_button_1.configure(state="disabled")
        self.radio_button_2.configure(state="disabled")
        self.radio_button_3.configure(state="disabled")
        self.textbox.delete("0.0", "end")
        product_id = self.entry.get()
        store_name = self.entry2.get()
        product_name = self.entry1.get()
        data_validation = 1
        if product_id == "":
            data_validation = 0
        if data_validation == 1 and store_name == "":
            data_validation = 0
        if product_name == "":
            product_name = product_id
        temp_stores = self.item_store_lookup(product_id)
        if not temp_stores:
            data_validation = 2
            self.textbox.insert("end", "\nProduct ID does not appear to exist. Please recheck and try again.")
        if data_validation == 1:
            storeList = list()
            text_box = ""
            store_list_string = f"{product_name} is available in the following stores:"
            i = 1
            for store in temp_stores:
                if i < len(temp_stores):
                    store_list_string = store_list_string + " " + store['storeName'] + ", "
                else:
                    store_list_string = store_list_string + " " + store['storeName']
                storeList.append(store['storeName'])
                i += 1
            self.textbox.insert("0.0", store_list_string)
            if store_name not in storeList:
                self.textbox.insert("end", f"{product_name} is available in the store you entered ({store_name}).")
            else:
                productIds = self.get_rarer_items(store_name)
                productIds = list(set(productIds))
                unique_to_store = list()
                self.textbox.insert("end", f"\nReviewing Product IDs to ensure they are unique to {store_name}")
                for id in productIds:
                    time.sleep(5)
                    temp_stores = self.item_store_lookup(id)
                    # print(id)
                    temp_unique = 0
                    for store in temp_stores:
                        # print(store['storeName'])
                        if store['storeName'] in storeList and store['storeName'] != store_name:
                            # print(f"Not Unqiue - {store['storeName']}")
                            temp_unique = 2
                        else:
                            if temp_unique < 2:
                                temp_unique = 1
                    if temp_unique == 1:
                        # print("Adding")
                        unique_to_store.append(id)
                unique_to_store = list(set(unique_to_store))
                self.textbox.insert("end", f"\nDVD Product ID's unique to {store_name} for ensuring you get {product_name} from {store_name}.")
                for i in unique_to_store:
                    self.textbox.insert("end", f"\n{i}")
                # self.textbox.insert("end", text_box)
        elif data_validation == 0:
            self.textbox.insert("0.0", "Missing Value in Product ID or Store Name")
        self.main_button_1.configure(state="enabled")
        self.radio_button_1.configure(state="normal")
        self.radio_button_2.configure(state="normal")
        self.radio_button_3.configure(state="normal")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()