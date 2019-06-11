from bs4 import BeautifulSoup
import requests
import os
import sys
import re


def dumbing_scraper():

    page_count = 1
    url = 'http://www.dumbingofage.com/2010/comic/book-1/01-move-in-day/home/'
    last_com = False
    book = 'thisgetsreplacedbelow'
    init_url = requests.get(url)
    init_soup = BeautifulSoup(init_url.content, "html5lib")
    last_img = init_soup.find(title = 'Latest')
    last_url = last_img.get('href')


    while last_com == False:       

        doa_comic = requests.get(url)


        if book not in url:
            book = book_finder(url)
            os.makedirs(book, exist_ok = True)
            page_count = 1

        comic_soup = BeautifulSoup(doa_comic.content, "html5lib")
        imgs = comic_soup.find_all('img',{'src':re.compile('http://www.dumbingofage.com/comics/*')})
        com_down = imgs[0].get('src')

        image = requests.get(com_down)
        sys.stdout.write(f'\n Downloading {book} {page_count}')
        sys.stdout.flush()

        com_name = f'{book} {str(page_count).zfill(3)}{com_down[-4:]}'

        image_file = open(os.path.join(book, os.path.basename(com_name)), 'wb')

        for chunk in image.iter_content(100_000):
            image_file.write(chunk)

        image_file.close()


        if url == last_url:
            last_com = True
            sys.stdout.write('\nAll done!')
            sys.stdout.flush()

        else:
            next_img = comic_soup.find(title = 'Next')
            url = next_img.get('href')
            page_count += 1

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