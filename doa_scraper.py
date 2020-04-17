from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import datetime
import shelve
from collections import Counter


def dumbing_scraper():

    sys.stdout.write(f'Scraping initiated, time is now: {datetime.datetime.now()}\n')
    sys.stdout.flush()

    try:
        url = 'http://www.dumbingofage.com/2010/comic/book-1/01-move-in-day/home/'
        last_com = False
        init_url = requests.get(url)
        init_soup = BeautifulSoup(init_url.content, "html5lib")
        last_img = init_soup.find(title = 'Latest')
        last_url = last_img.get('href')

    except Exception as err:
        sys.stdout.write(f'Unable to reach the dumbing of age server. \n \
            Error is: {err} \n\
         Operation aborted. Time is now: {datetime.datetime.now()}\n')
        sys.stdout.flush()
        return 'Error!'

    doa_tracker = shelve.open('doa_tracker', writeback = True)

    if 'url' in doa_tracker:
        url = doa_tracker['url']
        if url == last_url:
            sys.stdout.write(f'No new comics since this was last run. Operation ending. Time: {datetime.datetime.now()}')
            sys.stdout.flush()
            last_com = True

        else: 
            sys.stdout.write('Finding next comic...')
            sys.stdout.flush()
            doa_comic = requests.get(url)
            comic_soup = BeautifulSoup(doa_comic.content, 'html5lib')
            next_img = comic_soup.find(title = 'Next')
            url = next_img.get('href')

    else:
        doa_tracker['url'] = url

    if 'pages' in doa_tracker:
        pages = doa_tracker['pages']
        book = doa_tracker['book']

    else:
        pages = Counter()
        book = 'thisgetsreplacedbelow'

    while last_com == False:

        try:
            doa_comic = requests.get(url)

            if book not in url:
                book = book_finder(url)
                os.makedirs(book, exist_ok = True)

            comic_soup = BeautifulSoup(doa_comic.content, "html5lib")
            imgs = comic_soup.find_all('img',{'src':re.compile('https://www.dumbingofage.com/comics/*')})
            com_down = imgs[0].get('src')

            image = requests.get(com_down)
            pages[book] += 1
            sys.stdout.write(f'\n Downloading {book} {pages[book]}')
            sys.stdout.flush()

            com_name = f'{book} {str(pages[book]).zfill(3)}{com_down[-4:]}'

            image_file = open(os.path.join(book, os.path.basename(com_name)), 'wb')

            for chunk in image.iter_content(100_000):
                image_file.write(chunk)

            image_file.close()


        except Exception as err:
            sys.stdout.write(f'Error downloading {book} {pages[book]}. Stopping download. \n \
                Error is: {err} \
                Time is now: {datetime.datetime.now()}\n')
            sys.stdout.flush()
            doa_tracker['book'] = book
            doa_tracker['url'] = old_url
            doa_tracker['pages'] = pages
            doa_tracker.close()
            return 'done!'

        if url == last_url:
            doa_tracker['book'] = book
            doa_tracker['url'] = url
            doa_tracker['pages'] = pages
            doa_tracker.close()
            sys.stdout.write(f'All done! \n Time is now: {datetime.datetime.now()}\n')
            sys.stdout.flush()
            last_com = True

        else:
            old_url = url
            next_img = comic_soup.find(title = 'Next')
            url = next_img.get('href')



def book_finder(target):
    try:
        book_count = target.find('book-')
        book_end = book_count + 6
        book_str = target[book_count:book_end]
        return book_str
    except:
        sys.stdout.write(f'Error happened at {target}')
        sys.stdout.flush()
        return 'Errors'


def main():
    dumbing_scraper()

if __name__ == '__main__':
    main()