from bs4 import BeautifulSoup
import requests
from twilio.rest import Client
import json

ENDPOINT = "https://quietlight.com/listings/"


def send_text(body_text):
    account_sid = 'AC9d23df78447da22746a5bc9f996e078b'
    auth_token = 'd1bf0534a66c01f48151bf4099ce841f'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+12562738295',
        body=body_text,
        to='+16399162221'
    )
    print(message.sid)

# QUIETLIGHT_DATA = {
#     "title": {
#         "title": "",
#         "url": "",
#         "price": 0.00,
#         "revenue": 0.00,
#         "earnings": 0.00,
#         "status": ""
#     },
# }


with open('quietlight_data.json') as json1_file:
    json1_str = json1_file.read()
    QUIETLIGHT_DATA = json.loads(json1_str)
print(QUIETLIGHT_DATA)
# 1 - scrape data from Quiet Light Website (use headers w/ BeautifulSoup)
headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36",
        "Accept-Language": "en-CA,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-GB;q=0.6,en-US;q=0.5"
}

resp = requests.get(ENDPOINT, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')
listings = soup.findAll('div', class_="single-content")
print("Running through each listing on QuietLight")
for listing in listings:
    if 'interruption-card' in listing.get('class', []):
        print("Interruption Card")
        pass
    else:
        listing_title = listing.find('div').find('h5').getText().strip()
        listing_status = "available"
        try:
            listing_website = listing.find('div').find('a').get('href')
        except AttributeError:
            listing_website = ""
        try:
            listing_price = listing.find('div').find('div', class_="price").getText().strip()[1:]
        except AttributeError:
            listing_price = 0.00
        try:
            listing_revenue = listing.find('div').find('div', class_="revenu_sec").select('p')[0].get_text().split("$")[1].strip()
            listing_earnings = listing.find('div').find('div', class_="revenu_sec").select('p')[1].get_text().split("$")[1].strip()
        except IndexError:
            listing_revenue = ""
            listing_earnings = ""
        except AttributeError:
            listing_revenue = ""
            listing_earnings = ""
        if 'sold' in listing.get('class', []):
            listing_status = "sold"
        if 'under-loi' in listing.get('class', []):
            listing_status = "under LOI"

        # Check if listing title exists in db

        if listing_title in QUIETLIGHT_DATA:

            # If listing title does exist, check if price or status has changed
            if QUIETLIGHT_DATA[listing_title]["price"] != listing_price:
                # price change!
                if QUIETLIGHT_DATA[listing_title]["price"] > listing_price:
                    body_text = f"QUIET LIGHT PRICE CHANGE!!\n\nListing: {listing_title}\n\nNew Price: ${listing_price}\nOriginal Price: ${QUIETLIGHT_DATA[listing_title]['price']}"
                    send_text(body_text)
                QUIETLIGHT_DATA[listing_title]["price"] = listing_price
            if QUIETLIGHT_DATA[listing_title]["status"] != listing_status:
                # change status
                if listing_status == "available":
                    body_text = f"QUIET LIGHT STATUS CHANGE!!\n\nListing: {listing_title}\n\nNew Status: {listing_status}\nOld Status: {QUIETLIGHT_DATA[listing_title]['status']}"
                    send_text(body_text)
                QUIETLIGHT_DATA[listing_title]['status'] = listing_status

        # If listing title does not exist, add to the dict
        else:
            body_text = f"NEW QUIET LIGHT LISTING\n\n{listing_title}\n\nLink: {listing_website}\n\nPrice: ${listing_price}\nRevenue: ${listing_revenue}\nSDE: ${listing_earnings}"
            send_text(body_text)

            print("adding listing to Quiet Light DB")
            QUIETLIGHT_DATA[listing_title] = {
                "title": listing_title,
                "url": listing_website,
                "price": listing_price,
                "revenue": listing_revenue,
                "earnings": listing_earnings,
                "status": listing_status
            }

        # create message of a new listing

print("dumping revised data into json file")
with open('quietlight_data.json', 'w') as fp:
    json.dump(QUIETLIGHT_DATA, fp)