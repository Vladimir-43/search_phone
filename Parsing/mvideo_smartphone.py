from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import pandas as pd
import sqlite3
from Parsing.LoggingForMe import log
from Parsing.find import find_element
from Parsing.find import find_elements
import Data.const as CONST

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, TimeoutException)


def mvideo():
    log('М.Видео', 'старт загрузки')
    records = []
    today_data = datetime.today()
    s = Service("Parsing/chromedriver.exe")
    driver = webdriver.Chrome(service=s)
    driver.get(CONST.URL_MVIDEO + '1')
    try:
        find_element(driver, By.CLASS_NAME, "product-title__text")
        elements = find_elements(driver, By.CLASS_NAME, "page-item.ng-star-inserted")  # количество страниц сайта
        el = [element.text for element in elements]
        print(f'Найдено страниц: {el[-1]}')
        for i in range(1, int(el[-1]) + 1):
            print(f' {i} .', end='')
            if i > 1:
                driver.get(CONST.URL_MVIDEO + str(i))
            elements = find_elements(driver, By.CLASS_NAME, "product-title__text")
            time_end = time.time() + 15  # 15 секунд на загрузку страницы, иначе останов
            while len(elements) < 24 and time_end > time.time():  # прокручивает до конца для загрузки всех js
                time.sleep(0.5)
                elements = find_elements(driver, By.CLASS_NAME, "product-title__text")
                ActionChains(driver).key_down(Keys.PAGE_DOWN).perform()
            elements = find_elements(driver, By.CLASS_NAME, "product-cards-layout__item.ng-star-inserted")
            for element in elements:
                rec = [2, today_data]
                el = find_element(element, By.CLASS_NAME, "product-title__text")
                if 'Смартфон ' in el.text:
                    rec.append(el.text.split('Смартфон ')[1])
                else:
                    rec.append(el.text)
                ref = el.get_attribute('href')
                el = find_element(element, By.CLASS_NAME, "price__main-value")
                rec.append(int(el.text.split(' ')[0] + el.text.split(' ')[1]))
                try:
                    el = element.find_element(By.CLASS_NAME, "label")
                    promo = el.text
                except ignored_exceptions:
                    promo = ''
                rec.append(promo)
                rec.append(ref)
                records.append(rec)
        z = pd.DataFrame(records)
        z.columns = ['id_store', 'date', 'model', 'price', 'promo', 'ref']
        print(f"\nВсего загружено {z.shape[0]} записей")
        conn = sqlite3.connect(r'Data/smartphone.db')
        z.to_sql(name='smartphones', if_exists='append', con=conn, index=False)
        conn.close()
        log('М.Видео', f'загружено {z.shape[0]} записей.')
    except:
        log('М.Видео', 'загрузка неудачна')
        print('\nМ.Видео: что-то было не так')
    finally:
        driver.close()
