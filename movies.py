from datetime import datetime
import sys
import requests
from pymongo import MongoClient
from pyquery import PyQuery as pq;
from collections import namedtuple, OrderedDict
import argparse

db = MongoClient().movies


Theater = namedtuple('Theater', ['name', 'url'])

def get_theater_data(url, date):
    page = requests.get(url, params={'date':date})
    content = page.content
    return content

def extract_movietimes(theaterpage_content):
    retval = OrderedDict()
    page = pq(theaterpage_content)
    showtimes_lists = page('#showtimes ul.showtimes')
    for movie_elem in showtimes_lists:
        movie_pq = page(movie_elem)
        movie_name = movie_pq.find('a.image').text()
        times_elems = movie_pq.find('div.times ul li')
        times = [pq(x).text() for x in times_elems]
        times = [x.split()[0] for x in times]
        retval[movie_name] = times

    return retval

def parse_theaters(body):
    page = pq(body)
    theater_as = page.find('a')
    urls = []
    for th in theater_as:
        th_info = pq(th)
        urls.append(Theater(th_info.text(), th_info.attr('href')))

    return urls

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Movie Time Scraper")
    parser.add_argument("-r", dest="theatersfile", help="update theater info from .html file")
    parser.add_argument("-d", dest="date", help="select a date to get movie times for (M/D/YY)")
    parser.add_argument("-s", dest="sync", action="store_true", default=None, help="resync showtimes for theaters")
    results = parser.parse_args()

    theaters_to_use = []
    if results.theatersfile:
        for theater in parse_theaters(open(results.theatersfile,'r').read()):
            db.theaters.update({"_id":theater.name},{"$set":{"url":theater.url}}, upsert=True)
            theaters_to_use.append(theater.name)

    querydate = datetime.now().strftime('%m/%d/%y')
    if results.date:
        querydate = results.date
    store_date = datetime.strptime(querydate,'%m/%d/%y')

    if results.sync:
        if not theaters_to_use:
            theaters_to_use = [Theater(x['_id'],x['url']) for x in  list(db.theaters.find({}))]
        for theater in theaters_to_use:
            theater_data = get_theater_data(theater.url, querydate)
            times = extract_movietimes(theater_data)
            print times
            db.showtimes.update({'_id' : theater.name + '|' + querydate}, {"$set":{'movies':times, '_date':store_date, '_theater':theater.name}}, upsert=True)


