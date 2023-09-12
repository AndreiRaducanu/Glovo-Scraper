import os


def check_credentials():
    file_path = "Glovo-Scraper/src/glovo/credentials.py"
    if os.path.isfile(file_path):
        print("Credentials.py already exists")
    else:
        try:
            with open(file_path, "w") as file:
                print("The account used must not have a phone number assosiacted with it")
                username = input("Insert glovo account email: ")
                password = input("Insert glovo account password: ")
                latitude = input("Insert the location latitude (Bucharest only): ")
                longitude = input("Insert the location longitude (Bucharest only): ")
                file.write(f"GLOVO_USERNAME = '{username}'\n")
                file.write(f"GLOVO_PASSWORD = '{password}'\n")
                file.write("DB_CONNECTION = ''\n")
                file.write(f"GLOVO_LAT = '{latitude}'\n")
                file.write(f"GLOVO_LONG = '{longitude}'\n")
            print("Created credentials.py")
        except IOError as e:
            print(f"Error creating file '{file_path}': {e}")
