import requests
import re
from bs4 import BeautifulSoup


base_url = 'https://aptekanevis.ru/catalog/lekarstva_i_bady/'
page_number = 1
itog = 0

while True: 
    url = f'{base_url}?PAGEN_1={page_number}'

    response = requests.get(url)

    print(response.status_code)

    if response.status_code != 200:
        print(f'Не удалось получить данные со страницы {page_number}')
        break

    html = response.text

    multi_class = "product__card nurik desktop".split(" ")

    soup = BeautifulSoup(html, "html.parser")

    products = soup.find_all("div", {"class":"product__card"})

    for product in products:
        #name = product.find("a", {"class": "catalog-item__name"}).text
        #price = float(re.sub("[^0-9.]", "",product.find("div", {"class": "catalog-item__price"}).text))
        #result = "https://online.gomeofarm.ru" + product.find("a",{"class": "catalog-item__name"}).get('href')
        #image = "https://online.gomeofarm.ru" + re.search(r"url\('([^']+)'\)", (product.find("a", {"class": "catalog-item__image"}).get('style'))).group(1)
        if product.attrs["class"] == multi_class:
            image = "https://aptekanevis.ru" + product.find("a", {"class": "product__main__image"}).find("img")["src"]
            name = product.find("a", {"class": "name_link"}).text
            #price = re.sub("[^0-9.]", "", product.find("div", {"class": "catalog__item-price"}).text)
            result = "https://aptekanevis.ru" + product.find("a", {"class": "product__main__image"}).get('href')
            #itog += 1
            print(name)
    
    page_number += 1

    if page_number > 2:
        print("tut beda")
        break

print("Itogo: ", itog)