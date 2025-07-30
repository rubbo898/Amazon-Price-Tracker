import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4
import pygame #pip install  pygame
import os
import time
import json
from colored import fg, attr

#Opening The Settings.json file
with open('settings.json','r') as file:
    settings = json.load(file)

# To play a ding if the product is in our budget 
pygame.mixer.init()
pygame.mixer.music.load(settings["remind-sound-path"])

# Set your budjet
my_price = settings['budget']

# initializing Currency Symbols to substract it from our string
currency_symbols = ['€', '	£', '$', "¥", "HK$", "₹", "¥", "," ] 

# the URL we are going to use
URL = settings['url']

# Google "My User Agent" And Replace It
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'} 

#Checking the price
def checking_price():
    page = requests.get(URL, headers=headers)
    # Always save the HTML page for debug
    with open('debug_amazon_response.html', 'w', encoding='utf-8') as f:
        f.write(page.text)
    soup  = BeautifulSoup(page.text, 'html.parser')

    #Finding the elements
    product_title_elem = soup.find('span', id='productTitle')
    product_price_elem = soup.find('span', class_ = "a-offscreen")
    if not product_title_elem or not product_price_elem:
        print(f"{fg('red_1')}Could not find product title or price on the page. The page structure may have changed or you are being blocked.{attr('reset')}")
        print(f"{fg('yellow_1')}Saved the HTML response to debug_amazon_response.html for inspection.{attr('reset')}")
        return
    product_title = product_title_elem.getText()
    product_price = product_price_elem.getText()

    # using replace() to remove currency symbols
    for i in currency_symbols : 
        product_price = product_price.replace(i, '')



    # Convert the string to cents, then to euros as integer
    price_cents = int(float(product_price))
    price_euros = price_cents // 100


    # Check for coupon presence and value (only if product found)
    coupon_keywords = ['coupon', 'buono sconto', 'save', 'risparmia', 'applica coupon']
    coupon_found = False
    coupon_value = None
    import re
    # Robust coupon extraction: look for couponLabelText class and extract value from all text
    coupon_elem = soup.find(class_="couponLabelText")
    if coupon_elem:
        coupon_found = True
        text_to_search = coupon_elem.get_text(" ", strip=True)
        value_match = re.search(r'(\d+[\.,]?\d*)\s*[%€]', text_to_search)
        if not value_match:
            value_match = re.search(r'coupon\s*(\d+[\.,]?\d*)\s*[%€]', text_to_search, re.IGNORECASE)
        if not value_match:
            value_match = re.search(r'(\d+[\.,]?\d*)\s*[%€]\s*coupon', text_to_search, re.IGNORECASE)
        if value_match:
            coupon_value = value_match.group(1) + '€' if '€' in value_match.group(0) else value_match.group(0)
    else:
        # fallback: old keyword-based search
        for keyword in coupon_keywords:
            coupon_str = soup.find(string=lambda text: text and keyword.lower() in text.lower())
            if coupon_str:
                coupon_found = True
                text_to_search = coupon_str.strip()
                value_match = re.search(r'(\d+[\.,]?\d*)\s*[%€]', text_to_search)
                if not value_match:
                    value_match = re.search(r'coupon\s*(\d+[\.,]?\d*)\s*[%€]', text_to_search, re.IGNORECASE)
                if not value_match:
                    value_match = re.search(r'(\d+[\.,]?\d*)\s*[%€]\s*coupon', text_to_search, re.IGNORECASE)
                if value_match:
                    coupon_value = value_match.group(1) + '€' if '€' in value_match.group(0) else value_match.group(0)
                break
    if coupon_found:
        if coupon_value:
            print(f"{fg('yellow_1')}Coupon available: {coupon_value} off! Check the page for details.{attr('reset')}")
        else:
            print(f"{fg('yellow_1')}Coupon available for this product! Check the page for details.{attr('reset')}")

    ProductTitleStrip = product_title.strip()
    print(f"{fg('green_1')}The Product Name is:{attr('reset')}{fg('dark_slate_gray_2')} {ProductTitleStrip}{attr('reset')}")
    print(f"{fg('green_1')}The Price is:{attr('reset')}{fg('orange_red_1')} {price_euros:d}€{attr('reset')}")



    # checking the price
    if(price_euros < my_price):
        pygame.mixer.music.play()
        print(f"{fg('medium_orchid_1b')}You Can Buy This Now!{attr('reset')}")
        time.sleep(3) # audio will be played first then exit the program. This time for audio playing.
        exit()
    else:
        print(f"{fg('red_1')}The Price Is Too High!{attr('reset')}")

while True:
    checking_price()
    time.sleep(settings['remind-time']) #It is set to run the program once in an hour! You can change by changing the value in seconds!
