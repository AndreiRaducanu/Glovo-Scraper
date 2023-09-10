from glovo.restructure_functions import (
    get_access_token,
    header_location,
    local_datetime_to_milliseconds,
    loop_all_pages,
    create_directory,
    better_access_menu
)
from glovo.credentials import DB_CONNECTION
from pymongo import MongoClient
import time


# define the initial header
headers = {
    "glovo-api-version": "14",
    "glovo-app-platform": "web",
    "glovo-delivery-location-accuracy": "0",
    "glovo-location-city-code": "BUC"
}

# Create dir for results
create_directory()

# modify the headers to contain the access token
headers["authorization"] = get_access_token()

# modify the headers to contain the user location
headers = header_location(headers)

# modify the headers to contain the local time
headers["glovo-delivery-location-timestamp"] = local_datetime_to_milliseconds()

# df with all restaurants [loop_all_pages in test mode 1 page] !MODIFY
start_pages = time.time()
restaurants_dataframe = loop_all_pages(headers)
end_pages = time.time()
elapsed = end_pages - start_pages
print(f"Looping pages took: {elapsed} s")  # Average 6 seconds

start_products = time.time()
final_df = better_access_menu(restaurants_dataframe, headers)
end_products = time.time()
elapsed_products = end_products - start_products
print(f"Looping products took: {elapsed_products} s")  # Average 144s
# Convert df to a list of dictionaries for MongoDB export
final_df = final_df.to_dict(orient="records")

connection_string = DB_CONNECTION
database_name = 'Glovo'
collection_name = 'complete_list'
cluster = MongoClient(connection_string)
db = cluster[database_name]
collection = db[collection_name]
collection.delete_many({})
collection.insert_many(final_df)
