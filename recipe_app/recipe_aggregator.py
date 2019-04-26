import requests
from bs4 import BeautifulSoup
#from IPython.core.display import HTML
from selenium import webdriver
import time
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from create_driver import chrome_driver

def get_ingredients(link, site):
    driver = chrome_driver().setUp()
    driver.get(link)
    if site == 'nyt':
        driver.find_element_by_xpath('//*[@id="appContainer"]/div/div[2]/div/div/div/div[2]/div/div/div[1]/p/span').click()
        time.sleep(1)
        driver.find_element_by_name("userid").send_keys("kyle.m.stanley16@gmail.com")
        driver.find_element_by_name("password").send_keys("1Baseball6")
        driver.find_element_by_xpath('//*[@id="appContainer"]/div/div[2]/div/div/div/div[2]/div/div/div[3]/div[2]/form/div[2]/span').click()
        nytimes_ingredient_list = {'quantity':[], 'ingredient':[]}
        ingredients = driver.find_element_by_class_name("recipe-ingredients")
        for ingredient in ingredients.find_elements_by_tag_name('li'):
            nytimes_ingredient_list['quantity'].append(ingredient.find_element_by_class_name('quantity').text)
            nytimes_ingredient_list['ingredient'].append(ingredient.find_element_by_class_name('ingredient-name').text)
        df = pd.DataFrame(nytimes_ingredient_list)
    if site == 'epi':
        epicurious_ingredient_list = {'ingredient':[], 'quantity':[]}
        driver.get(link)
        ingredients = driver.find_element_by_class_name('ingredients')
        for ingredient in ingredients.find_elements_by_class_name('ingredient'):
            epicurious_ingredient_list['quantity'].append(ingredient.text.split(' ')[0])
            epicurious_ingredient_list['ingredient'].append(' '.join(ingredient.text.split(' ')[1:]))
        df = pd.DataFrame(epicurious_ingredient_list)
    if site == 'all':
        allrecipes_ingredient_list = {'ingredient':[], 'quantity':[]}
        driver.get(link)
        for ingredient in driver.find_elements_by_class_name('checkList__line'):
            allrecipes_ingredient_list['ingredient'].append(' '.join(ingredient.text.split('\n')[0].split(' ')[1:]))
            allrecipes_ingredient_list['quantity'].append(ingredient.text.split('\n')[0].split(' ')[0])
        df = pd.DataFrame(allrecipes_ingredient_list)
    return df
# df = pd.concat([all_df, epi_df, ny_df], ignore_index=True)
#
# from sklearn.feature_extraction.text import CountVectorizer
# vectorizer = CountVectorizer(stop_words='english', lowercase=True, strip_accents='ascii')
# matrix = vectorizer.fit_transform(df['ingredient'])
#
# top_ingredients = pd.DataFrame({'count': matrix.toarray().sum(axis=0), \
#               'ingredient_word' : vectorizer.get_feature_names()}).sort_values(by=['count'], ascending=False)
#
# print(top_ingredients)
#
#
# def cups_to_oz(x):
#     return x * 8
#
# def oz_to_cups(x):
#     return float(x)/8
#
# def cups_to_ml(x):
#     return x*240
#
# def ml_to_cups(x):
#     return float(x)/240
#
# def cups_to_tbsp(x):
#     return x*16
#
# def tbsp_to_cups(x):
#     return float(x)/16
#
# def oz_to_grams(x):
#     return x*28.350
#
# def grams_to_oz(x):
#     return x/28.350
