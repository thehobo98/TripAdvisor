import json
import re
from os import system

import requests
from bs4 import BeautifulSoup


def get_restaurant_details(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    details = soup.select_one("div#RESTAURANT_DETAILS")
    reviews_div = soup.select(".review-container")

    restaurant = {}
    restaurant_id = url.split('-')[1] + '-' + url.split('-')[2]

    restaurant['id'] = restaurant_id
    restaurant['name'] = soup.select_one('h1.heading_title').text
    try:
        restaurant['rank'] = int(soup.select_one('span.header_popularity').text.split()[0].replace('#', ''))
        print("Rank", restaurant['rank'])
    except:
        restaurant['rank'] = -1

    restaurant['reviewCount'] = int(soup.select_one('span.reviews_header_count').text.split('(')[1].split(')')[0])

    try:
        restaurant['overallRating'] = float(soup.select_one('span.overallRating').text)
    except:
        restaurant['overallRating'] = -1

    try:
        ratingsdiv = details.select_one("div.ratingSummary")
        restaurant['ratings'] = {}
        for rating in ratingsdiv.select("span.text"):
            type = rating.text
            rating = float(
                rating.parent.find_next_sibling().select_one("span.ui_bubble_rating").attrs['alt'].split()[0])
            restaurant['ratings'][type] = rating
    except:
        pass

    try:
        pricediv = details.find(text=re.compile(r'Average prices')).parent.find_next_sibling()
        pricetext = [x for x in pricediv.stripped_strings][0]
        pricetexts = pricetext.replace('\xa0', '').replace('\n', '').replace('₹', '').replace(',', '').split(' -')
        restaurant['prices'] = {"min": int(pricetexts[0]), "max": int(pricetexts[1])}
    except:
        restaurant['prices'] = {"min": 0, "max": 0}

    try:
        cuisine_div = details.find(text=re.compile(r'Cuisine')).parent.find_next_sibling()
        restaurant['cuisines'] = [x for x in cuisine_div.stripped_strings if x != ',']
    except:
        restaurant['cuisines'] = []

    try:
        goodfor_div = details.find(text=re.compile(r'Good for')).parent.find_next_sibling()
        goodfortext = [x for x in goodfor_div.stripped_strings][0]
        restaurant['goodfor'] = goodfortext.split(',')
    except:
        restaurant['goodfor'] = []

    try:
        features_div = details.find(text=re.compile(r'Restaurant features')).parent.find_next_sibling()
        featurestext = [x for x in features_div.stripped_strings][0]
        restaurant['features'] = featurestext.split(',')
    except:
        restaurant['features'] = []

    try:
        meals_div = details.find(text=re.compile(r'Meals')).parent.find_next_sibling()
        mealstext = [x for x in meals_div.stripped_strings][0]
        restaurant['meals'] = mealstext.split(',')
    except:
        restaurant['meals'] = []

    try:
        last_offset = int(soup.select_one("a.pageNum.last.taLnk").attrs['data-offset'])
    except:
        last_offset = 0

    restaurant['reviews'] = getReviews(reviews_div)
    offset = 10
    while offset <= last_offset:
        print("offset:", offset)
        urlparts = url.split('-')
        urlparts.insert(4, 'or' + str(offset))
        newurl = '-'.join(urlparts)
        try:
            new_r = requests.get(newurl)
            new_soup = BeautifulSoup(new_r.text, 'lxml')
            reviews_div = new_soup.select(".review-container")
            restaurant['reviews'] += getReviews(reviews_div)
        except:
            pass
        offset += 10

    return restaurant


def getReviews(reviews_div):
    reviews = []
    for review_div in reviews_div:
        review = {}
        try:
            review['uid'] = review_div.select_one('.memberOverlayLink').attrs['id'].split('_')[1].split('-')[0]
        except:
            continue
        try:
            review['rating'] = int(review_div.select_one('.ui_bubble_rating').attrs['class'][1].split('_')[1]) / 10
        except:
            review['rating'] = 0

        try:
            review['title'] = review_div.select_one('span.noQuotes').text
        except:
            review['title'] = ""
        try:
            review['text'] = review_div.select_one('div.entry').text
        except:
            review['text'] = ""

        uid_set.add(review['uid'])
        reviews.append(review)
    return reviews


# url = 'https://www.tripadvisor.in/Restaurant_Review-g297628-d10318504-Reviews-Whitefield_Baking_Company-Bengaluru_Bangalore_District_Karnataka.html'

# uid_set = set(json.load(open('uid_list.json')))
uid_set = set()
links = json.load(open('links.json'))

#CHANGE THE LINKS FILE NAME ACCORDINGLY FOR DIFFERENT CITIES AFTER SCRAPING THE LINKS
#Eg:- Bangalore_links.json etc

restaurants = []
i = 0
for url in links:
    print(i, url)
    try:
        restaurant = get_restaurant_details(url)
        restaurants.append(restaurant)
    except:
        continue
    i += 1

json.dump(restaurants, open('restaurants.json', 'w'), indent=1)

json.dump(list(uid_set), open('uid_list.json', 'w'), indent=1)

system('curl --upload-file ./restaurants.json https://transfer.sh/')
system('curl --upload-file ./uid_list.json https://transfer.sh/')
