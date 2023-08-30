import requests
from bs4 import BeautifulSoup
from olclient.openlibrary import OpenLibrary
import olclient.common as common
import time


# Initialize OpenLibrary
ol = OpenLibrary()

# read publication dates 
# copy & pasted into file from publisher website
# misses current year
publication_dates = {}

for i in open("publications.csv"):
    if i.strip():
        split_line = i.strip().split("\t")
        if len(split_line) == 3:
            year = split_line[0][-4:]
            author = split_line[1].strip()
            title = split_line[2].strip()
            keying = "{}-{}".format(author, title)
            keying = keying.lower()
            publication_dates[keying] = year


# read CRB page & soup it 
response = requests.get('https://www.caferoyalbooks.com/Shop')
soup = BeautifulSoup(response.content, "html.parser")

# iterate over all product items

for book in soup.find_all("div", {"class":"ProductList-item"}):
    title_author = book.find('h1',{'class': 'ProductList-title'}).string
    # ignore Boxsets etc. 
    if "set" not in title_author and "Set" not in title_author and "ooks" not in title_author:
        # get proper title / author split books:
        if "—" in title_author and title_author != "Whitechapel Bell Foundry — John Claridge":
            author, title = title_author.split("—",1)
            author = author.strip()
            title = title.strip()
            cover = book.find('img',{'class':'ProductList-image--primary'})['data-src']
            search = "{}-{}".format(author, title)
            search = search.lower()
            # print(cover)
            if search in publication_dates.keys():
                year = publication_dates[search]
            else:
                year = "2023"
            if title not in ['Alexandra Road Estate', 'Rush Hour London Underground 1973', 'Along the Thames']:
                print("creating {}\t{}\t{}\t{}".format(
                    author, title, cover, year
                ))
                response = ol.session.post("https://openlibrary.org/books/add",data={
                    'title': title,
                    'author_names--0': author,
                    'authors--0--author--key': '__new__',
                    'publish_date': year,
                    'publisher': 'Café Royal Books',
                    '_save': ''})
                print(response)
                time.sleep(1)