from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
import sqlite3
from Parsing.LoggingForMe import log
from Parsing.find import find_element
from Parsing.find import find_elements
import Data.const as CONST


def dns():
    log('DNS', 'старт загрузки')
    records = []
    today_data = datetime.today()
    s = Service("Parsing/chromedriver.exe")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Opens the browser up in background
    driver = webdriver.Chrome(options=chrome_options, service=s)
    driver.get(CONST.URL_DNS)
    try:
        elements = find_elements(driver, By.CLASS_NAME, "pagination-widget__page")  # количество страниц сайта
        el = elements[-1].get_attribute("data-page-number")
        print(f'Найдено страниц: {el}')
        for i in range(1, int(el) + 1):
            print(f' {i} .', end='')
            if i > 1:
                driver.get(CONST.URL_DNS + '?p=' + str(i))
            elements = find_elements(driver, By.CLASS_NAME, "catalog-product.ui-button-widget")
            for element in elements:
                rec = [3, today_data]
                no_rec = False
                ref = ''
                try:
                    el = find_element(element, By.TAG_NAME, "span")
                    if isinstance(el.text, str) and ' Смартфон ' in el.text:
                        rec.append(el.text.split(' Смартфон ')[1].split(' [')[0])
                        el = find_element(element, By.CLASS_NAME, "product-buy__price")
                        if el.text != '':
                            rec.append(int(el.text.split(' ')[0] + el.text.split(' ')[1]))
                            ref = find_element(element, By.CLASS_NAME, "catalog-product__name").get_attribute('href')
                        else:
                            no_rec = True
                    else:
                        no_rec = True
                except CONST.IGNORED_EXCEPTION:
                    no_rec = True
                try:
                    if not no_rec:
                        el = element.find_element(By.CLASS_NAME, "vobler")
                        rec.append(el.text)
                except CONST.IGNORED_EXCEPTION:
                    rec.append('')
                rec.append(ref)
                if not no_rec:
                    records.append(rec)
        z = pd.DataFrame(records)
        z.columns = ['id_store', 'date', 'model', 'price', 'promo', 'ref']
        print(f"\nВсего загружено {z.shape[0]} записей")
        conn = sqlite3.connect(r'Data/smartphone.db')
        z.to_sql(name='smartphones', if_exists='append', con=conn, index=False)
        conn.close()
        log('DNS', f'загружено {z.shape[0]} записей.')
    #        driver.close()
    except:
        log('DNS', 'загрузка неудачна')
        print('\nDNS: что-то было не так')
    finally:
        driver.close()
