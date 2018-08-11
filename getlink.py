import json
import re
from os import system

import requests
from bs4 import BeautifulSoup as soup


def scrape(geoID):
    offset = 0
    links = []
    URL = 'https://www.tripadvisor.in/RestaurantSearch'

    while True:
        payload = {'geo': geoID, 'ajax': '1', 'sortOrder': 'relevance', 'o': 'a' + str(offset)}
        r = requests.get(URL, params=payload)
        s = soup(r.text, 'lxml')
        pgno = s.select_one('span.current').attrs['data-page-number']
        maxpgno = s.select('.pageNum')[-1].attrs['data-page-number']
        print('*' * 10)
        print("Scraping page number", pgno)
        print('Max pgno', maxpgno)
        print('*' * 10)
        for i in s.select('div.listing'):
            print('\t', '_' * 10)
            l = dict()
            # l['id']=i.attrs['id']
            try:
                link = 'https://www.tripadvisor.in' + i.select_one('div.title > a').attrs['href']
            except:
                continue

            try:
                review_count = re.match(r'\d+', i.select_one('span.reviewCount > a').text.strip()).group(0)
            except:
                review_count = '0'

            if review_count == '0':
                continue

            links.append(link)

            for key, value in l.items():
                if value != '' and len(value) != 0:
                    print('\t\t', key, '=', value)
            print('(' + pgno + '/' + maxpgno + ')')

        if (pgno == maxpgno):
            break
        else:
            offset += 30

    json.dump(links, open(geoID + '.json', 'w'), indent=4)
    system('curl --upload-file ./1236165.json https://transfer.sh/')


scrape('1236165')