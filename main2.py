import requests
from PIL import Image
import os
import time
import datetime
import random
import hashlib
import json

# Load configuration
with open("config.json") as f:
    config = json.load(f)

cookie = str(config.get("cookie"))
image = str(config.get("image"))
upload_num = int(config.get("upload_num"))

def log(text):
    timestamp = datetime.datetime.utcfromtimestamp(time.time()).strftime("%H:%M:%S")
    print(f"[{timestamp}] {text}")

def welcome(session):
    if not os.path.exists(image):
        log("No image found")
        quit()
    try:
        # Attempt to get user info from a different endpoint
        response = session.get('https://users.roblox.com/v1/users/authenticated')
        response.raise_for_status()
        bot = response.json()["name"]
        log(f"Welcome `{bot}`")
    except requests.exceptions.HTTPError as e:
        log(f"HTTP error occurred: {e}")
        if response.status_code == 403:
            log("Invalid cookie or authentication failed.")
        quit()
    except Exception as e:
        log(f"An error occurred: {e}")
        quit()

def get_token(session):
    try:
        # Attempt to get the CSRF token from the homepage or authenticated endpoint
        response = session.get('https://www.roblox.com/', headers={"Referer": "https://www.roblox.com"})
        response.raise_for_status()

        # Log response details for debugging
        log(f"Response status: {response.status_code}")
        log(f"Response headers: {response.headers}")
        log(f"Response cookies: {response.cookies}")

        # Check for CSRF token in headers and cookies
        if 'x-csrf-token' in response.headers:
            return response.headers['x-csrf-token']
        elif 'x-csrf-token' in response.cookies:
            return response.cookies['x-csrf-token']
        else:
            log('x-csrf-token not found in headers or cookies')
            return None
    except requests.exceptions.RequestException as e:
        log(f"Error getting X-CSRF-TOKEN: {e}")
        return None

def upload_decal(cookie, location, name, session):
    try:
        token = get_token(session)
        if not token:
            log("Failed to retrieve CSRF token. Skipping upload.")
            return

        headers = {"Requester": "Client", "X-CSRF-TOKEN": token}
        with open(location, 'rb') as image_file:
            response = session.post(f"https://data.roblox.com/data/upload/json?assetTypeId=13&name={name}&description=emppu", data=image_file, headers=headers)
        response.raise_for_status()
        log(f"Uploaded `{name}` successfully")
    except requests.exceptions.RequestException as e:
        log(f"Error sending the request: {e}")
        if response.status_code == 429:
            log("Rate limited, waiting 60 seconds")
            time.sleep(60)

def hash_file(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(1024), b""):
            h.update(chunk)
    return h.hexdigest()

# Clean up old files
for root, dirs, files in os.walk("final"):
    for file in files:
        os.remove(os.path.join(root, file))

# Read user agents and words
try:
    with open("useragents.txt", "r") as file:
        useragents = file.read().splitlines()
except FileNotFoundError:
    log("useragents.txt not found")
    quit()

try:
    with open("words.txt", "r") as file:
        word_list = file.read().splitlines()
except FileNotFoundError:
    log("words.txt not found")
    quit()

# Main script execution
with requests.Session() as session:
    session.cookies.update({".ROBLOSECURITY": cookie})
    welcome(session)
    for i in range(upload_num):
        randomnum = random.randrange(0, 99999999999999)
        img = Image.open(image)
        img2 = img.resize((420 + i, 420 + i), Image.LANCZOS)
        img2.save(f"final/{randomnum}.png")
        time.sleep(0.15)
        message = hash_file(f"final/{randomnum}.png")
        log(f"{message} - {randomnum}.png")

    for root, dirs, files in os.walk("final"):
        for file in files:
            useragent = random.choice(useragents)
            session.headers.update({"User-Agent": useragent})
            name = random.choice(word_list)
            upload_decal(cookie, os.path.join("final", file), name, session)
            time.sleep(1.5)
