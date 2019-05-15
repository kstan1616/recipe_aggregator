import requests
from bs4 import BeautifulSoup
#from IPython.core.display import HTML
from selenium import webdriver
import time
import random
import os
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
# from create_driver import chrome_driver
import re
import nltk
nltk.data.path.append('./nltk_data/')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.stem.wordnet import WordNetLemmatizer
from difflib import SequenceMatcher
import operator
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import urllib.request

class get_ingredients():
    def __init__(self):
        self.metrics = ['tablespoon', 'tablespoons', 'teaspoon', 'teaspoons', 'tbsp', 'tbsps', 'tsp', \
           'tsps', 'cup', 'cups', 'ounce', 'ounces', 'oz', 'ozs'\
           'quart', 'quarts', 'qt', 'qts', 'pt', 'pts', 'pint', 'pints', 'gallon', 'gallons', \
           'gal', 'gals', 'pound', 'pounds', 'lb', 'lbs', 'g', 'gs',\
           'gram', 'grams', 'kilogram', 'kilograms', 'kg', 'liter', 'liters', 'L', 'millileter', \
           'mL', 'millileters']
        self.basic_ingredient_list = pd.read_csv('data/final_recipe_list_categorized.csv', index_col=0, encoding='latin')
        self.basic_ingredient_list['length'] = self.basic_ingredient_list['ingredient'].apply(lambda x: len(x))
        self.basic_ingredient_list = self.basic_ingredient_list[self.basic_ingredient_list['length'] > 2]
#         self.driver = chrome_driver().setUp()
        self.final_df = pd.DataFrame(columns=['quantity', 'ingredient'])

    def scrape_ingredients(self, link, site):
        # NYT
        if site == 'nyt':
            response = requests.get(link)
            soup = BeautifulSoup(response.text)
            nytimes_ingredient_list = {'quantity':[], 'ingredient':[]}
            ul = soup.find("ul", {"class": "recipe-ingredients"})
            for li in ul.findAll("li"):
                try:
                    nytimes_ingredient_list['quantity'].append(li.find("span", {"class": "quantity"}).text.replace('\n', '').strip())
                except:
                    nytimes_ingredient_list['quantity'].append(None)
                    nytimes_ingredient_list['ingredient'].append(li.find("span", {"class": "ingredient-name"}).text.replace('\n', '').strip())
            self.final_df = self.final_df.append(pd.DataFrame(nytimes_ingredient_list), ignore_index=True)
        # EPI
        if site == 'epi':
            response = requests.get(link)
            soup = BeautifulSoup(response.text)
            epicurious_ingredient_list = {'quantity':[], 'ingredient':[]}
            ul = soup.find("ul", {"class": "ingredients"})
            for li in ul.findAll("li"):
                epicurious_ingredient_list['ingredient'].append(li.text)
                epicurious_ingredient_list['quantity'].append(None)
            df = pd.DataFrame(epicurious_ingredient_list)
            df['quantity'] = df['ingredient'].apply(lambda x: self.strip_quantity(x))
            self.final_df = self.final_df.append(df, ignore_index=True)
        # All
        if site == 'all':
            response = requests.get(link)
            soup = BeautifulSoup(response.text)
            all_ingredient_list = {'quantity':[], 'ingredient':[]}
            for li in soup.findAll("li" , {"class":"checkList__line"}):
                all_ingredient_list['ingredient'].append(li.text.replace('\n', ''))
                try:
                    quantity = li.text.replace('\n', '').split(' ')[0]
                    all_ingredient_list['quantity'].append(quantity)
                except:
                    all_ingredient_list['quantity'].append(quantity)
            df = pd.DataFrame(all_ingredient_list)
            df['ingredient'] = df['ingredient'].apply(lambda x: self.clean_all_ingredients(x))
            df = df[df['ingredient'] != '']
            df = df[df['quantity'] != 'Add']
            self.final_df = self.final_df.append(df, ignore_index=True)

    def clean_all_ingredients(self, x):
        x = x.split(' ')
        try:
            y = x[0]
            test = int(y.split('/')[0])
            final_string = ' '.join(x[1:])
        except:
            try:
                test = int(x[0])
                final_string = ' '.join(x[1:])
            except:
                final_string = ' '.join(x)
        return final_string

    def strip_quantity(self, x):
        x = x.split(' ')
        quantity = ''
        try:
            quantity = quantity + str(int(x[0].split('/')[0]) / int(x[0].split('/')[1]))
        except:
            try:
                quantity = quantity + str(int(x[0]))
                try:
                    quantity = quantity + '.' + str(int(x[1].split('/')[0]) / int(x[1].split('/')[1])).split('.')[1]
                except:
                    pass
            except:
                pass
        return quantity

    def clean_list(self):
        lmtzr = WordNetLemmatizer()
        self.final_df['original_recipe'] = self.final_df['ingredient']
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.strip_measurements(x, self.metrics))
        self.final_df['metric'] = self.final_df['ingredient'].apply(lambda x: self.add_metrics(x))
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.remove_metrics(x))
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.pos(x))
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.lemmatizer(x))
        self.final_df['ingredient'] = self.final_df.apply(lambda row: self.standardize_ingredients(row, self.basic_ingredient_list), axis=1)
        self.final_df['category'] = self.final_df['ingredient'].apply(lambda x: self.add_metrics(x))
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.remove_metrics(x))
        self.final_df = self.final_df.groupby(['ingredient', 'category']).agg(lambda x: x.tolist())
        self.final_df = self.final_df.groupby(['ingredient', 'category']).agg(lambda x: x.tolist()).sort_values(['category']).reset_index()
        self.final_df = self.final_df[['ingredient', 'category', 'quantity', 'metric', 'original_recipe']]


    #Find words in metrics list for recipe list generation

    def strip_measurements(self, x, metrics):
        found_metrics = ''
        keep_words = ''
        for word in x.split(' '):
            if word in metrics:
                found_metrics = found_metrics + ' ' + word
            else:
                keep_words = keep_words + ' ' + word
        return keep_words + '|' + found_metrics

    def add_metrics(self, x):
        x = x.split('|')
        return x[1]

    def remove_metrics(self, x):
        x = x.split('|')
        return x[0]

    def pos(self, x):
        tokens = nltk.word_tokenize(x)
        tagged_list = nltk.pos_tag(tokens)
        new_string = ''
        for tup in tagged_list:
            if tup[1] in ['NN', 'JJ', 'NNS', 'NNP', 'VBP', 'VBG']:
                new_string += tup[0] + ' '
            else:
                pass
        return new_string.lower()

    def try_lemmatize(self, x):
        try:
            return_string = lmtzr.lemmatize(x).lower().encode('ascii')
        except:
            return_string = x.lower()
        return return_string

    def lemmatizer(self, x):
        lmtzr = WordNetLemmatizer()
        return ' '.join([self.try_lemmatize(y) for y in x.split(' ')])

    #create list of ngrms turned into individual strings
    #['I', 'am', 'I am']

    def get_ngrams(self, text):
        final = []
        length = text.split(' ')
        length = len(length)
        for n in range(1, (length+1)):
            n_grams = ngrams(word_tokenize(text), n)
            final.append([ ' '.join(grams) for grams in n_grams])
        return [item for sublist in final for item in sublist]

    #Find longest matching string in 'ingredient' field in database

    def standardize_ingredients(self, row, ingredients):
        possible_standard = []
        for gram in self.get_ngrams(row['ingredient']):
            try:
                possible_standard.append(ingredients[ingredients['ingredient'] == gram]['ingredient'].iloc[0])
            except:
                pass
        if len(possible_standard) == 0:
            return row['ingredient'] + '|' + 'not categorized'
        else:
            return max(possible_standard, key=len) + '|' + ingredients['category'][ingredients['ingredient'] == max(possible_standard, key=len)].iloc[0]


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
