import json
import re
from os import system

import requests
from bs4 import BeautifulSoup


def get_reviewer_details(x):
    URL = 'https://www.tripadvisor.in/MemberOverlay?uid=%s' % x
    print(URL)
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'lxml')
    details = soup.select_one("body > div")

    reviewer = {}
    try:
        reviewer['level'] = int(details.select_one('div.badgeinfo').text.split()[1])
    except:
        pass
    try:
        member = details.select_one('ul.memberdescriptionReviewEnhancements')
        reviewer['member_since'] = int(member.select_one('li').text.split()[-1])
    except:
        pass
    try:
        other = details.select_one(' ul.countsReviewEnhancements')
        reviewer['contributions'] = int(other.find(text=re.compile(r'Contributions')).split()[0])
    except:
        pass
    try:
        other = details.select_one(' ul.countsReviewEnhancements')
        reviewer['cities'] = int(other.find(text=re.compile(r'City visited')).split()[0])
    except:
        pass
    try:
        other = details.select_one(' ul.countsReviewEnhancements')
        reviewer['Helpful'] = int(other.find(text=re.compile(r'Helpful vote')).split()[0])
    except:
        pass
    try:
        other = details.select_one(' ul.countsReviewEnhancements')
        reviewer['photos'] = int(other.find(text=re.compile(r'Photos')).split()[0])
    except:
        pass

    print(json.dumps(reviewer, indent=1))
    return reviewer


uid_list = json.load(open('uid_list.json'))

#CHANGE THE UID_LIST FILE NAME ACCORDINGLY FOR DIFFERENT CITIES AFTER SCRAPING THE UID_LIST
#Eg:- Bangalore_uid_list.json etc

reviews = []

i = 0
for uid in uid_list:
    print(i, uid)
    try:
        review = get_reviewer_details(uid)
        reviews.append(review)
    except:
        continue
    i += 1
json.dump(reviews, open('reviewer.json', 'w'), indent=1)
system('curl --upload-file ./reviewer.json https://transfer.sh/')
