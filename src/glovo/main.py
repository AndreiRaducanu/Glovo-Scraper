import time
from pymongo import MongoClient
# Run setup function before main
from glovo.set_env import check_credentials
check_credentials()
# Import Libraries and Modules
from glovo.functions import (  # noqa E402
    get_access_token,
    header_location,
    local_datetime_to_milliseconds,
    loop_all_pages,
    access_restaurant_menu,
    create_directory,
)
from glovo.credentials import DB_CONNECTION  # noqa E402

# define the initial header
headers = {
    "glovo-api-version": "14",
    "glovo-app-platform": "web",
    "glovo-delivery-location-accuracy": "0",
    "glovo-location-city-code": "BUC"
}

# Create output directory to store csv data
create_directory()

# Modify the headers to contain the access token
headers["authorization"] = get_access_token()

# Modify the headers to contain the user location
headers = header_location(headers)

# Modify the headers to contain the local time
headers["glovo-delivery-location-timestamp"] = local_datetime_to_milliseconds()

# DF with all restaurants
start_pages = time.time()
restaurants_dataframe = loop_all_pages(headers)
end_pages = time.time()
elapsed = end_pages - start_pages
print(f"Looping pages took: {elapsed} s")  # Average 6 seconds

start_products = time.time()
final_df = access_restaurant_menu(restaurants_dataframe, headers)
end_products = time.time()
elapsed_products = end_products - start_products
print(f"Looping products took: {elapsed_products} s")  # Average 144 seconds

connect_db = input("Do you want to store the data in MongoDB?[y/N]: ")
if connect_db == "y":
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
    print("Database successfully updated")
