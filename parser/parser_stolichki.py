import requests
import re
from bs4 import BeautifulSoup


base_url = 'https://stolichki.ru/catalog/lekarstvennie-sredstva-22'
page_number = 2
itog = 0

while True: 
    url = f'{base_url}?page={page_number}'

    response = requests.get(url)

    print(response.status_code)

    if response.status_code != 200:
        print(f'Не удалось получить данные со страницы {page_number}')
        break

    html = response.text

    #multi_class = "js--product-card product-card product-card_l".split(" ")

    #soup = BeautifulSoup(html, "html.parser")

    # Создаем объект BeautifulSoup с использованием парсера 'lxml'
    soup = BeautifulSoup(html, 'lxml')

    # Находим все элементы с классом 'js--product-card product-card product-card_l'
    product_cards = soup.find_all('div', class_='js--product-card product-card product-card_l')

    # Проверяем, найдены ли элементы
    if not product_cards:
        print("Элементы не найдены")
    else:
        # Печатаем найденные элементы
        for product_card in product_cards:
            product_id = product_card['data-product-id']
            print(f"Product ID: {product_id}")

    #products = soup.find_all("div", {"class":"js--product-card product-card product-card_l"})
    #for product in products:
        #print(product['data-product-id'])
        #if product.attrs["class"] == multi_class:
            #image = "https://papteki.ru" + product.find("img")["src"]
            #name = product.find("a", {"class": "catalog__item-title"}).text
            #price = re.sub("[^0-9.]", "", product.find("div", {"class": "catalog__item-price"}).text)
            #result =  product.find("a", {"class": "product-card__link"})['href'] #"https://papteki.ru" +
            #itog += 1
            #print(result)
    
    page_number += 1

    if page_number > 2:
        print("tut beda")
        break

print("Itogo: ", itog)