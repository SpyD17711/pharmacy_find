import requests
import re
from bs4 import BeautifulSoup
import mysql.connector

# Установка соединения с базой данных
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="3228",
    database="pharmacy_parser"
)

# Создание курсора для выполнения SQL-запросов
cursor = db.cursor()

# Добавление записи в таблицу Pharmacy
pharmacy_name = "Петербургские аптеки"
# Проверка наличия записи с таким именем в таблице Pharmacy
check_pharmacy_query = "SELECT id FROM Pharmacy WHERE name = %s"
cursor.execute(check_pharmacy_query, (pharmacy_name,))
existing_pharmacy = cursor.fetchone()

if existing_pharmacy:
    # Если запись существует, используем её id
    pharmacy_id = existing_pharmacy[0]
else:
    # Если записи нет, добавляем новую
    insert_pharmacy_query = "INSERT INTO Pharmacy (name) VALUES (%s)"
    cursor.execute(insert_pharmacy_query, (pharmacy_name,))
    pharmacy_id = cursor.lastrowid


base_url = 'https://papteki.ru/catalog/vitaminyi-b-a-dy/'
page_number = 1

while True:
    url = f'{base_url}?p={page_number}'

    response = requests.get(url)

    if response.status_code != 200:
        print(f'Не удалось получить данные со страницы {page_number}')
        break

    html = response.text

    multi_class = "col-xl-4 col-lg-4 col-md-6".split(" ")

    soup = BeautifulSoup(html, "html.parser")

    products = soup.find_all("div", {"class": "col-md-6"})

    for product in products:
        if product.attrs["class"] == multi_class:
            image = "https://papteki.ru" + product.find("img")["src"]
            name = product.find("a", {"class": "catalog__item-title"}).text
            price_text = product.find("div", {"class": "catalog__item-price"}).text
            price_match = re.search(r'\d+\.\d+', price_text)
            price = float(price_match.group()) if price_match else None
            result = "https://papteki.ru" + product.find("a", {"class": "button catalog__item-btn"}).get('href')

            # Проверка существования продукта в базе данных
            check_product_query = "SELECT id FROM Product WHERE name = %s"
            cursor.execute(check_product_query, (name,))
            product_data = cursor.fetchone()

            if product_data:
                product_id = product_data[0]

                # Проверка цены в таблице PharmacyProduct
                check_price_query = "SELECT price FROM PharmacyProduct WHERE product_id = %s AND pharmacy_id = %s"
                cursor.execute(check_price_query, (product_id, pharmacy_id))
                price_data = cursor.fetchone()

                if price_data:
                    existing_price = price_data[0]
                    if price < existing_price:
                        # Обновление записи в таблице PharmacyProduct
                        update_pharmacy_product_query = "UPDATE PharmacyProduct SET price = %s, result_url = %s WHERE product_id = %s AND pharmacy_id = %s"
                        cursor.execute(update_pharmacy_product_query, (price, result, product_id, pharmacy_id))
                        print(f"Обновлена цена для продукта '{name}' с {existing_price} на {price}")
                else:
                    # Добавление записи в таблицу PharmacyProduct
                    insert_pharmacy_product_query = "INSERT INTO PharmacyProduct (pharmacy_id, product_id, price, result_url) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_pharmacy_product_query, (pharmacy_id, product_id, price, result))
            else:
                # Добавление записи в таблицу Product
                insert_product_query = "INSERT INTO Product (image_url, name) VALUES (%s, %s)"
                cursor.execute(insert_product_query, (image, name))
                product_id = cursor.lastrowid

                # Добавление записи в таблицу PharmacyProduct
                insert_pharmacy_product_query = "INSERT INTO PharmacyProduct (pharmacy_id, product_id, price, result_url) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_pharmacy_product_query, (pharmacy_id, product_id, price, result))

    page_number += 1

    if page_number > 25:
        break

# Фиксируем изменения в базе данных
db.commit()

# Закрытие соединения с базе данных
cursor.close()
db.close()