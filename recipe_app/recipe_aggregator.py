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
import re
from nltk.stem.wordnet import WordNetLemmatizer

class get_ingredients():
    def __init__(self):
        self.metrics = ['tablespoon', 'teaspoon', 'tbsp', 'tsp', 'cup', 'ounce', 'oz', \
                        'quart', 'qt', 'pt', 'pint', 'gallon', 'gal', 'pount', 'lb', 'g', \
                        'gram', 'kilogram', 'kg', 'liter', 'L', 'millileter', 'mL']
        self.basic_ingredient_list = pd.read_csv('ingredient_list.csv')
        self.driver = chrome_driver().setUp()
        self.final_df = pd.DataFrame(columns=['quantity', 'ingredient'])

    def scrape_ingredients(self, link, site):
        self.driver.get(link)
        if site == 'nyt':
            self.driver.find_element_by_xpath('//*[@id="appContainer"]/div/div[2]/div/div/div/div[2]/div/div/div[1]/p/span').click()
            time.sleep(1)
            self.driver.find_element_by_name("userid").send_keys("kyle.m.stanley16@gmail.com")
            self.driver.find_element_by_name("password").send_keys("1Baseball6")
            self.driver.find_element_by_xpath('//*[@id="appContainer"]/div/div[2]/div/div/div/div[2]/div/div/div[3]/div[2]/form/div[2]/span').click()
            nytimes_ingredient_list = {'quantity':[], 'ingredient':[]}
            ingredients = self.driver.find_element_by_class_name("recipe-ingredients")
            for ingredient in ingredients.find_elements_by_tag_name('li'):
                nytimes_ingredient_list['quantity'].append(ingredient.find_element_by_class_name('quantity').text)
                nytimes_ingredient_list['ingredient'].append(ingredient.find_element_by_class_name('ingredient-name').text)
            self.final_df = self.final_df.append(pd.DataFrame(nytimes_ingredient_list), ignore_index=True)
        if site == 'epi':
            epicurious_ingredient_list = {'ingredient':[], 'quantity':[]}
            self.driver.get(link)
            ingredients = self.driver.find_element_by_class_name('ingredients')
            for ingredient in ingredients.find_elements_by_class_name('ingredient'):
                epicurious_ingredient_list['quantity'].append(ingredient.text.split(' ')[0])
                epicurious_ingredient_list['ingredient'].append(' '.join(ingredient.text.split(' ')[1:]))
            self.final_df = self.final_df.append(pd.DataFrame(epicurious_ingredient_list), ignore_index=True)
        if site == 'all':
            allrecipes_ingredient_list = {'ingredient':[], 'quantity':[]}
            self.driver.get(link)
            for ingredient in self.driver.find_elements_by_class_name('checkList__line'):
                allrecipes_ingredient_list['ingredient'].append(' '.join(ingredient.text.split('\n')[0].split(' ')[1:]))
                allrecipes_ingredient_list['quantity'].append(ingredient.text.split('\n')[0].split(' ')[0])
            self.final_df = self.final_df.append(pd.DataFrame(allrecipes_ingredient_list), ignore_index=True)


    def clean_list(self):
        lmtzr = WordNetLemmatizer()
        nltk.data.path.append('./nltk_data/')
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: ', '.join([lmtzr.lemmatize(y).lower() for y in x.split(' ')]).replace(',', ''))
        self.final_df['metric'] = self.final_df['ingredient'].apply(lambda x: self.strip_measurements(x, self.metrics))
        self.final_df['ingredient'] = self.final_df.apply(lambda row: self.strip_word(row), axis=1)
        self.final_df['ingredient'] = self.final_df.apply(lambda row: self.standardize_ingredients(row, self.basic_ingredient_list['ingredients']), axis=1)

    def strip_measurements(self, x, metrics):
        found_word = ''
        for word in x.split(' '):
            if word in metrics:
                found_word = word
        return found_word

    def strip_word(self, row):
        try:
            new_recipe_ingredients = row['ingredient'].replace(row['metric'], '')
            new_recipe_ingredients = re.sub('[^A-Za-z0-9]+', ' ', new_recipe_ingredients)
        except:
            new_recipe_ingredients = re.sub('[^A-Za-z0-9]+', ' ', row['ingredient'])
        return new_recipe_ingredients

    def standardize_ingredients(self, row, ingredients):
        possible_standard = []
        for ingredient in ingredients:
            if ingredient in row['ingredient']:
                possible_standard.append(ingredient)
        if len(possible_standard) == 0:
            return row['ingredient']
        else:
            return max(possible_standard, key=len)

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
