from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
#import requests
from datetime import datetime
import pandas as pd
import sqlite3
from Parsing.LoggingForMe import log
from Data.const import URL_CITILINK



def citilink():
    log('Ситилинк', 'старт загрузки')
    records = []
    today_data = datetime.today()
    s = Service("Parsing/chromedriver.exe")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Opens the browser up in background
    driver = webdriver.Chrome(options=chrome_options, service=s)
    try:
        # page = requests.get(URL_CITILINK + '1')
        # soup = BeautifulSoup(page.text, "html.parser")
        driver.get(URL_CITILINK)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        pages = soup.find('a', class_='PaginationWidget__page_last')
        print(f'Найдено страниц: {int(pages.text)}.')
        for i in range(1, int(pages.text) + 1):
            if i > 1:
                driver.get(URL_CITILINK + str(i))
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                #page = requests.get(URL_CITILINK + str(i))
                # #soup = BeautifulSoup(page.text, "html.parser")
            print(f' {i} .', end='')
            all_rec = soup.findAll('div', class_='product_data__gtm-js')
            for rec in all_rec:
                no_rec = False
                record = [1, today_data,
                          rec.find('a', class_='ProductCardHorizontal__title').text.split('Смартфон ')[1]]
                price = rec.find('span', class_='ProductCardHorizontal__price_current-price')
                if price:
                    record.append(int("".join(price.text.split())))
                else:
                    no_rec = True
                all_promo = rec.findAll('span', class_='ColorBadge')
                pr = ''
                for promo in all_promo:
                    pr += " ".join(promo.text.split()) + ' / '
                record.append(pr[:-3])
                record.append('https://www.citilink.ru' + rec.find('a', class_='ProductCardHorizontal__title')['href'])
                if not no_rec:
                    records.append(record)
        z = pd.DataFrame(records)
        z.columns = ['id_store', 'date', 'model', 'price', 'promo', 'ref']
        conn = sqlite3.connect(r'Data/smartphone.db')
        z.to_sql(name='smartphones', if_exists='append', con=conn, index=False)
        conn.close()
        log('Ситилинк', f'загружено {z.shape[0]} записей.')
        print(f"\nВсего загружено {z.shape[0]} записей")
    except Exception as e:
        print(e)
        print('\nCitilink: что-то было не так')
        log('Ситилинк', 'загрузка неудачна')
    finally:
        driver.close()

