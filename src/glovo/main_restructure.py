from glovo.restructure_functions import *
from glovo.credentials import *
from pymongo import MongoClient
import time


# define the initial header
headers = {
    "glovo-api-version": "14",
    "glovo-app-platform": "web",
    "glovo-delivery-location-accuracy": "0",
    "glovo-location-city-code": "BUC"
}

# modify the headers to contain the access token
headers["authorization"] = get_access_token()

# modify the headers to contain the user location
headers = header_location(headers)

# modify the headers to contain the local time
headers["glovo-delivery-location-timestamp"] = local_datetime_to_milliseconds()

# df with all restaurants [loop_all_pages in test mode 1 page] !MODIFY
start_time = time.time()
restaurants_dataframe = loop_all_pages(headers)
end_time = time.time()
elapsed = end_time - start_time
print(elapsed) #1.72
#time.sleep(30)

final_df = access_restaurant_menu(restaurants_dataframe,headers)
final_df['_id'] = final_df.index
final_df['Final_Price'] = final_df['Final_Price'].astype(float)
final_df.dropna(subset=['Final_Price'], inplace=True)

final_df = final_df.sort_values(by='Final_Price', ascending=True)
final_df = final_df.to_dict(orient = "records")

connection_string = DB_CONNECTION
database_name = 'Glovo'
collection_name = 'complete_list'
cluster = MongoClient(connection_string)
db = cluster[database_name]
collection = db[collection_name]
collection.delete_many({})
collection.insert_many(final_df)




