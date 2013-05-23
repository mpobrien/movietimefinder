import sys
import requests
from pyquery import PyQuery as pq;
from collections import namedtuple, OrderedDict


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

def get_theaters(body):
    page = pq(body)
    theater_as = page.find('a')
    urls = []
    for th in theater_as:
        th_info = pq(th)
        urls.append(Theater(th_info.text(), th_info.attr('href')))

    return urls


def main(args):
    if len(args) > 0:
        theaters_list = open(args[0],'r').read()
        theaters = get_theaters(theaters_list)
        test = theaters[230]
        print test
        th_data = get_theater_data(test.url, '5/23/13')
        times = extract_movietimes(th_data)
        for k,v, in times.items():
            print k, v


if __name__ == '__main__':
    main(sys.argv[1:])
