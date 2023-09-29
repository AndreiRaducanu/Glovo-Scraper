# Standard Library Imports
import datetime
import json
import os
import threading
from typing import Dict, List

# Third-Party Library Imports
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Custom Module Imports
from glovo.credentials import (
    GLOVO_USERNAME,
    GLOVO_PASSWORD,
    GLOVO_LAT,
    GLOVO_LONG,
)


# Get the access token to make requests
def get_access_token():
    login_url = "https://api.glovoapp.com/oauth/token"
    payload = {
        'grantType': 'password',
        'username': GLOVO_USERNAME,
        'password': GLOVO_PASSWORD
        }
    headers = {
        "glovo-api-version": "14",
        "glovo-location-city-code": "BUC",
        }
    response = requests.post(login_url, json=payload, headers=headers)
    login_data = response.json()
    if "access" in login_data and "accessToken" in login_data["access"]:
        access_token = login_data["access"]["accessToken"]
        print(f"Login successful {response}. Access token obtained.")
        return access_token
    else:
        print(f"Login failed {response}. Unable to get access token.")
        exit()


# Get user location and add it to headers
def header_location(headers):
    # get_user_location()
    latitude = GLOVO_LAT
    longitude = GLOVO_LONG
    headers["Glovo-Delivery-Location-Latitude"] = latitude
    headers["Glovo-Delivery-Location-Longitude"] = longitude
    return headers


# Covert current time for headers
def local_datetime_to_milliseconds():
    # Convert the local datetime to a Unix timestamp in seconds
    local_datetime = datetime.datetime.now()
    timestamp_in_seconds = local_datetime.timestamp()
    # Convert the timestamp to milliseconds
    timestamp_in_milliseconds = int(timestamp_in_seconds * 1000)
    return str(timestamp_in_milliseconds)


# Returns integer used for looping trough pages
def get_total_pages():
    # url that returns HTML
    html_url = "https://glovoapp.com/ro/ro/bucuresti/restaurante_1/"
    response = requests.get(html_url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    elements = soup.find_all(class_="current-page-text")
    # always return the number after 'din'
    for element in elements:
        reply = (element.text).strip()
        match = re.search(r"din (\d+)", reply)
        if match:
            number = match.group(1)
            return int(number)


def create_directory():
    directory_path = "output"
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' already exists.")


# returns a DataFrame containing data of all restaurants per one page
def get_restaurants_per_page(querystring, headers):
    headers = {
        "glovo-api-version": "14",
        "glovo-app-platform": "web",
        "glovo-delivery-location-accuracy": "0",
        "glovo-location-city-code": "BUC"
        }
    headers = header_location(headers)
    headers["glovo-delivery-location-timestamp"] = local_datetime_to_milliseconds()
    json_page_url = "https://api.glovoapp.com/v3/feeds/categories/1"
    response_page = requests.request("GET", json_page_url, headers=headers, params=querystring)
    # json data for a whole page of restaurants, usually 48 per page
    json_page = response_page.json()
    # create an empty DataFrame that will be used for appending data
    restaurants_per_page = pd.DataFrame()
    for restaurant in json_page['elements']:
        # check to ensure that the nested keys exist before accessing them
        if restaurant and restaurant.get("singleData") and restaurant["singleData"].get("storeData") and restaurant["singleData"]["storeData"].get("store"):
            restaurant_path = restaurant["singleData"]["storeData"]["store"]
            store_name = restaurant_path["name"]
            if store_name == "KFC":
                pass
            store_url = 'https://glovoapp.com/ro/ro/bucuresti/' + str(restaurant_path["slug"])
            store_id = int(restaurant_path["id"])
            store_address_id = int(restaurant_path["addressId"])
            is_open = restaurant_path["open"]
            delivery_fee = restaurant_path["serviceFee"]
            if is_open is False:
                print(f"STORE {store_name} IS CLOSED")
            # check for promotions
            try:
                promotions = restaurant_path["promotions"][0]
                if promotions["id"] == -1 and promotions["type"] == "FREE_DELIVERY":
                    delivery_fee = 0
                else:
                    print(f"Unkown promotion for {store_name}")
                    raise TypeError("Unkown promotion")
            except (IndexError, TypeError):
                print(f"Restaurant {store_name} has no promotions")
            # create dataframe for current restuarant to be later added to main DF
            restaurant_df = pd.DataFrame({
                "Store_name": [store_name], "Store_url": [store_url],
                "Delivery_fee": [delivery_fee], "Store_id": [store_id],
                "Address_id": [store_address_id], "Open": [is_open]
               })
            # if the restaurant is closed, drop it from DF
            restaurant_df = restaurant_df.drop(restaurant_df[restaurant_df["Open"] != True].index)  # noqa E712
            # Append the current restaurant DataFrame to the main DF
            restaurants_per_page = pd.concat([restaurants_per_page, restaurant_df], ignore_index=True)
    return restaurants_per_page


# loops trough all available restaurants and stores the data in a DataFrame
def loop_all_pages(headers):
    querystring = {"cacheId": "BUC", "limit": "48", "offset": "0"}
    page_count = 0
    # list of DataFrames
    all_restaurants_list = []
    total_pages = get_total_pages()
    # create function to append restaurants per page to data list due to threads / using barrier to ensure threads dont conflict..
    barrier = threading.Barrier(total_pages + 1)

    def fetch_restaurants(querystring, headers):
        restaurants_per_page = get_restaurants_per_page(querystring, headers)
        all_restaurants_list.append(restaurants_per_page)
        barrier.wait()
    threads: List[threading.Thread] = []

    # for _ in range(1):
    for _ in range(total_pages):
        offset_value = int(querystring["offset"])
        # replace line with threads for each page and use lock
        thread_per_page = threading.Thread(target=fetch_restaurants, args=(querystring, headers))
        thread_per_page.start()
        # increment offset for next page
        offset_value += 48
        page_count += 1
        querystring["offset"] = str(offset_value)
        print(f"\nRestaurants page: {page_count}")
    # Wait for threads to complete
    for thread in threads:
        thread.join()
    barrier.wait()

    complete_restaurant_df = pd.concat(all_restaurants_list, axis=0, ignore_index=True)
    # convert the 'price' column to numeric data type
    complete_restaurant_df['Delivery_fee'] = pd.to_numeric(complete_restaurant_df['Delivery_fee'])
    # sort by delivery fee
    complete_restaurant_df = complete_restaurant_df.sort_values(by='Delivery_fee', ascending=True)
    complete_restaurant_df = complete_restaurant_df.reset_index(drop=True)
    complete_restaurant_df.to_csv('output/stores_sorted.csv', index=True)
    complete_restaurant_df.to_csv('output/complete_restaurant_df.csv', index=False)
    print(complete_restaurant_df)
    return complete_restaurant_df


# returns basket min value and basket surcharge if value not met
def get_basket_data(basket_fee_path):
    headers_basket = {
        "glovo-app-platform": "web",
        "glovo-api-version": "14",
        "glovo-location-city-code": "BUC",
    }
    response = requests.request("GET", basket_fee_path, headers=headers_basket)
    json_basket = response.json()
    try:
        basket_min_value = json_basket['data']['progressBar']['basketValue']
        basket_surcharge = json_basket['data']['tracking']['surcharge']
    except KeyError:
        print(basket_fee_path)
        with open("output/basket_not_present.json", "w") as f:
            json.dump(json_basket, f)
            print("================STORE ISSUE======================")
        return 1
    return basket_min_value, basket_surcharge


# Classes required for find_combination()
class ProductCombo:
    def __init__(self, name, id, addon_name, addon_id, final_price):
        self.name = name
        self.id = id
        self.addon_name = addon_name
        self.addon_id = addon_id
        self.final_price = final_price


class SingleProduct:
    def __init__(self, name, id, price, attributes):
        self.name = name
        self.id = id
        self.price = price
        self.attributes = attributes


# Returns either one product or a combination of products to reach the best possible price
def find_combination(product_object, basket_min_value, basket_surcharge, delivery_fee):
    SERVICE_FEE = 0.99
    product_price = product_object.price
    best_total = product_price + basket_surcharge  # Start with just the current product
    all_addon_results: Dict[int, float] = {}

    for addon_id, product_info in product_object.attributes.items():
        addon_name, addon_price = next(iter(product_info.items()))
        total_product_and_addon = product_price + addon_price

        if total_product_and_addon == basket_min_value and total_product_and_addon <= best_total:
            best_total = total_product_and_addon + delivery_fee + SERVICE_FEE
            all_addon_results[addon_id] = best_total

        elif total_product_and_addon < basket_min_value:
            best_total = total_product_and_addon + basket_surcharge + delivery_fee + SERVICE_FEE
            all_addon_results[addon_id] = best_total

        elif total_product_and_addon > basket_min_value:
            best_total = total_product_and_addon + delivery_fee + SERVICE_FEE
            all_addon_results[addon_id] = best_total

    if not all_addon_results:
        final_price_product = product_price + basket_surcharge + delivery_fee + SERVICE_FEE
        product_object.price = final_price_product
        return product_object

    lowest_value = min(all_addon_results.values())
    final_price_product = product_price + basket_surcharge + delivery_fee + SERVICE_FEE

    if lowest_value <= final_price_product:
        lowest_id = [key for key, value in all_addon_results.items() if value == lowest_value][0]
        data_dict = dict(items2)[lowest_id]
        addon_name, final_price = next(iter(data_dict.items()))
        combo_object = ProductCombo(product_object.name, product_object.id, addon_name, lowest_id, lowest_value)
        return combo_object

    product_object.price = final_price_product
    return product_object



# Takes restaurant object as arg and returns all the products in a pandas DF
def get_product_data(restaurant_instance):
    # Extract data from the restaurant_instance
    restaurant_name = restaurant_instance.store_name
    restaurant_id = restaurant_instance.store_id
    basket_min_value = restaurant_instance.basket_min_value
    basket_surcharge = restaurant_instance.basket_surcharge
    delivery_fee = restaurant_instance.delivery_fee
    products = restaurant_instance.json_menus['data']['body']
    all_final_data = []
    seen_product_ids = set()  # To avoid duplicate product entries

    for individual_menu in products:
        if individual_menu['type'] != "LABEL":
            standalone_product = individual_menu['data']['elements']

            for element in standalone_product:
                try:
                    product = element['data']
                    product_name = product['name']
                except KeyError:
                    continue

                if is_blacklisted(product_name):
                    continue

                product_id = product['id']
                original_product_price = product.get("promotion", {}).get("price", product['price'])

                if original_product_price < basket_min_value:
                    attributes = product.get('attributeGroups', [])
                    existing_options: Dict[int, Dict[str, float]] = {}

                    for option in attributes:
                        options_dictionary = option.get('attributes', [])

                        for addon in options_dictionary:
                            addon_name = addon['name']
                            addon_id = addon['id']
                            addon_price = addon['priceInfo'].get('amount')

                            if addon_id not in existing_options:
                                existing_options[addon_id] = {}
                            existing_options[addon_id][addon_name] = addon_price

                    product_to_pass = SingleProduct(product_name, product_id, original_product_price, existing_options)
                    final_product_combo = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
                    final_product_name = final_product_combo.name
                    final_product_id = final_product_combo.id
                    product_entry = {
                        "Restaurant_Name": restaurant_name,
                        "Restaurant_Id": restaurant_id,
                        "Product_Name": final_product_name,
                        "Product_Id": final_product_id,
                    }

                    if isinstance(final_product_combo, SingleProduct):
                        final_price = round(final_product_combo.price, 2)
                        product_entry["Final_Price"] = final_price
                    elif isinstance(final_product_combo, ProductCombo):
                        final_price = round(final_product_combo.final_price, 2)
                        final_addon_name = final_product_combo.addon_name
                        final_addon_id = final_product_combo.addon_id
                        product_entry["Addon_Name"] = final_addon_name
                        product_entry["Addon_Id"] = final_addon_id
                        product_entry["Final_Price"] = final_price

                    if product_entry["Product_Id"] not in seen_product_ids:
                        seen_product_ids.add(product_entry["Product_Id"])
                        all_final_data.append(product_entry)

                else:
                    final_price = round(original_product_price + delivery_fee + 0.99, 2)
                    product_entry = {
                        "Restaurant_Name": restaurant_name,
                        "Restaurant_Id": restaurant_id,
                        "Product_Name": product_name,
                        "Product_Id": product_id,
                        "Addon_Name": None,
                        "Addon_Id": None,
                        "Final_Price": final_price
                    }
                    all_final_data.append(product_entry)

    final_data = pd.DataFrame(all_final_data)
    final_data.to_csv("output/last_restaurant_df.csv", index=False)
    return final_data


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


def build_trie(words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    return root


def find_partial_matches(node, text, start=0):
    matches = []
    for i in range(start, len(text)):
        char = text[i]
        if char in node.children:
            node = node.children[char]
            if node.is_end_of_word:
                matches.append(text[start:i + 1])
        else:
            break
    return matches


# Build the trie once from the blacklist
blacklist = [
    "gustăr", "sos", "garn", "ketchup", "bere", "drink", "desert", "bauturi", "apa", "aperitive",
    "salat", "baut", "energiz", "alcool", "beverage", "side", "inghetata", "băutur", "tea", "refresh",
    "milk", "starter", "beer", "soda", "juice", "cafea", "răcor", "cprite", "coca-cola", "cola",
    "fanta"
    ]
blacklist_drinks = [
    "dorna", "apa", "suc", "pepsi", "mirinda", "portocale", "7up", "tuborg",
    "heineken", "ayran", "shake", "cafea", "coffe", "espresso", "cappucino", "irish",
    "cocktail", "limonada", "zaganu", "ceai", "apă", "lipton", "vin", "sec", "%", "carlsberg",
    "Alc", "7 up", "ursus"
    ]
blacklist_starters = [
    "crutoane", "covrig", "pate", "cascaval", "corn", "placinta", "croissant", "iaurt",
    "tortilla", "porumb", "baclava", "mamaliga", "salad", "clatite"
    ]
blacklist_addons = [
    "ardei iute", "paine", "lipie crocanta", "bete chopsticks", "chifla", "extra",
    "ambalaj", "ardei", "ghimbir", "bagheta simpla", "taxa", "lamaie", "rosie",
    "Lapte condensat", "topping", "cheddar", "stafide", "ulei", "zucchini",
    "rosii", "masline", "alune"
    ]
blacklist_sauces = [
    "mujdei", "smantana", "home made sweet chilli", "wasabi", "mustar", "maioneza",
    "usturoi", "dulce acrisor", "sos", "teriaky", "tzatziki", "sweet chili", "sesame",
    "ginger", "garlic", "crema", "samurai", "tabasco", "kewpie"
    ]
blacklist_desert = ["panini", "pie", "placinta", "tort", "ecler", "inghetata", "prajitura", "gogosi"]
blacklist_final = blacklist_drinks + blacklist_starters + blacklist_addons + blacklist_sauces + blacklist
blacklist_trie = build_trie(blacklist_final)


def is_blacklisted(input_string):
    input_string_lower = input_string.lower()
    for i in range(len(input_string_lower)):
        partial_matches = find_partial_matches(blacklist_trie, input_string_lower, i)
        if partial_matches:
            print(f"BLACKLISTED {input_string}")
            return True
    print(f"NOT BLACKLISTED {input_string}")
    return False


def get_menu_data(access_path, headers):
    querystring = {"promoListViewWebVariation": "CONTROL"}
    json_response = requests.request("GET", access_path, headers=headers, params=querystring)
    json_menus = json_response.json()
    return json_menus


# Used to determine if restaurant has multiple menus
def type_of_menus(json_menus):
    try:
        path_to_products = json_menus["data"]["body"][0]["data"]["elements"][0]["type"]
        if path_to_products == "IMAGE_PREVIEW_CARD" or path_to_products == "PRODUCT_TILE":
            # Menus present
            raise KeyError("Skip cause there are menus")
        elif path_to_products == "PRODUCT_ROW" or path_to_products == "LIST" or path_to_products == "COLLECTION_TILE":
            # No menus
            return 1
        else:
            raise ValueError("Unkown type of restaurant menu")
    except KeyError:
        return 0


def get_individual_menu(json_menus):
    # Get a list of paths representing every menu per store
    paths = [
        element["data"]["action"]["data"]["path"]
        for item in json_menus["data"]["body"]
        if "elements" in item["data"]
        for element in item["data"]["elements"]
        if "action" in element["data"] and "path" in element["data"]["action"]["data"]
    ]
    # Attempt to store path and query json as key-value
    path_query_product = {}

    for path_to_products in paths:
        query_string = path_to_products.split("?")[1]
        query_params = query_string.split("&")
        querystring_menu = {}

        for param in query_params:
            key, value = param.split("=")
            querystring_menu[key] = value
        path_to_products = 'https://api.glovoapp.com/v3/' + path_to_products
        str_of_dict = json.dumps(querystring_menu)
        path_query_product[path_to_products] = str_of_dict
    return path_query_product


# Generator for individual menu
def fetch_menu_data(request_data, headers):
    for key, value in request_data.items():
        path_to_products = key
        querystring_menu = value
        product_data = requests.request("GET", path_to_products, headers=headers, params=querystring_menu)
        json_products = product_data.json()
        title = json_products["data"]["body"][0]["data"]["title"]
        if not is_blacklisted(title):
            yield json_products


def fetch_products_df(restaurant_instance):
    product_df = get_product_data(restaurant_instance)
    return product_df


def process_final_dataframe(list_to_store_df_per_menu):
    # Concatenate DataFrames, drop duplicates, and perform other operations
    combined_df_final = pd.concat(list_to_store_df_per_menu, ignore_index=True)
    combined_df_final = combined_df_final.drop_duplicates()
    combined_df_final['Final_Price'] = combined_df_final['Final_Price'].astype(float)
    combined_df_final.dropna(subset=['Final_Price'], inplace=True)
    combined_df_final = combined_df_final.sort_values(by='Final_Price', ascending=True)
    
    # Reassign _id 
    combined_df_final['_id'] = combined_df_final.index
    
    combined_df_final.to_csv("output/product_data.csv", index=False)
    return combined_df_final


def access_restaurant_menu(complete_restaurant_df, headers):
    list_to_store_df_per_menu = []

    # Used to call get_product_data for each restaurant
    class RestaurantData:
        def __init__(self, store_name, store_id, basket_min_value, basket_surcharge, delivery_fee, json_menus):
            self.store_name = store_name
            self.store_id = store_id
            self.basket_min_value = basket_min_value
            self.basket_surcharge = basket_surcharge
            self.delivery_fee = delivery_fee
            self.json_menus = json_menus

    # For each restaurant append its products to a dataframe
    # Experimental branch issue with too many requests per second
    for _, row in complete_restaurant_df.iterrows():
        delivery_fee = float(row['Delivery_fee'])
        store_name = row['Store_name']
        store_id = int(row['Store_id'])
        store_address_id = int(row['Address_id'])
        access_path = (
            f'https://api.glovoapp.com/v3/stores/{store_id}/addresses/{store_address_id}/content?promoListViewWebVariation=CONTROL'
        )
        basket_fee_path = (
            f'https://api.glovoapp.com/v3/stores/{store_id}/addresses/{store_address_id}/node/store_mbs'
        )

        basket_data = get_basket_data(basket_fee_path)

        if basket_data != 1:
            basket_min_value, basket_surcharge = basket_data
        else:
            continue
        json_menus = get_menu_data(access_path, headers)
        restaurant_instance = RestaurantData(store_name, store_id, basket_min_value, basket_surcharge, delivery_fee, json_menus)

        if type_of_menus(json_menus) != 0:
            # product_df = get_product_data(store_name, store_id, basket_min_value, basket_surcharge, delivery_fee, json_menus)
            product_df = get_product_data(restaurant_instance)
            list_to_store_df_per_menu.append(product_df)
            print(f"No menus for {store_name}")
        else:
            request_data = get_individual_menu(json_menus)
            lock = threading.Lock()

            def process_product(products, store_name, store_id, basket_min_value, basket_surcharge, delivery_fee):
                restaurant_instance_menu = RestaurantData(store_name, store_id, basket_min_value, basket_surcharge, delivery_fee, products)
                menu_df = get_product_data(restaurant_instance_menu)
                with lock:
                    list_to_store_df_per_menu.append(menu_df)
            threads = []
            for products in fetch_menu_data(request_data, headers):
                thread = threading.Thread(
                    target=process_product,
                    args=(products, store_name, store_id, basket_min_value, basket_surcharge, delivery_fee)
                )
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
    return process_final_dataframe(list_to_store_df_per_menu)
