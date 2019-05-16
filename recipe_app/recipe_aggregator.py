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
        self.final_df['quantity'] = self.final_df['quantity'].apply(lambda x: self.fix_quantity(x))
        self.final_df['metric'] = self.final_df.apply(lambda row: self.perform_metric_aggregates(row), axis=1)
        # self.final_df.drop('quantity', axis=1, inplace=True)
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.pos(x))
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.lemmatizer(x))
        self.final_df['ingredient'] = self.final_df.apply(lambda row: self.standardize_ingredients(row, self.basic_ingredient_list), axis=1)
        self.final_df['category'] = self.final_df['ingredient'].apply(lambda x: self.add_metrics(x))
        self.final_df['ingredient'] = self.final_df['ingredient'].apply(lambda x: self.remove_metrics(x))
        # self.final_df = self.final_df.groupby(['ingredient', 'category']).agg(lambda x: x.tolist())
#         self.final_df = self.final_df.groupby(['ingredient', 'category']).agg(lambda x: x.tolist()).sort_values(['category']).reset_index()
        self.final_df = self.final_df[['ingredient', 'category', 'metric', 'quantity', 'original_recipe']]


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

    def gallon_to_quart(self, n_gallon):
        n_quarts = n_gallon * 4
        return n_quarts

    def quart_to_pints(self, n_quarts):
        n_pints = n_quarts * 2
        return n_pints

    def pint_to_cups(self, n_pints):
        n_cups = n_pints * 2
        return n_cups

    def cup_to_ounces(self, n_cups):
        n_ounces = n_cups * 8
        return n_ounces

    def tsps_to_tbs(self, n_tsps):
        n_tbs = float(n_tsps)/3
        return n_tbs

    def tbs_to_cups(self, n_tbs):
        n_cups = float(n_tbs)/16
        return n_cups

    def ounces_to_mL(self, n_ounces):
        n_mLs = n_ounces * 29.5735
        return n_mLs

    def mL_to_ounces(self, n_mLs):
        n_ounces = n_mLs / 29.5735
        return n_ounces

    def pounds_to_kilos(self, n_pounds):
        n_kilos = n_pounds / 2.205
        return n_kilos

    def kilos_to_pounds(self, n_kilos):
        n_pounds = n_kilos * 2.205
        return n_pounds

    def ounces_to_grams(self, n_ounces):
        n_grams = n_ounces * 28.35
        return n_grams

    def grams_to_ounces(self, n_grams):
        n_ounces = n_grams / 28.35
        return n_ounces

    def pounds_to_ounces(self, n_pounds):
        n_ounces = n_pounds * 16
        return n_ounces


    def metric_aggregate(self, metric, quantity):
        desired_quantity = []
        desired_metric = []
        quantity = float(quantity)
        metric = metric.strip()
        if metric in ['tablespoon', 'tbsp', 'tablespoons', 'tbsps']:
            desired_quantity.append(self.cup_to_ounces(self.tbs_to_cups(quantity)))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(self.cup_to_ounces(self.tbs_to_cups(quantity))))
            desired_metric.append('mL')
        if metric in ['teaspoon', 'tsp', 'teaspoons', 'tsps']:
            desired_quantity.append(self.cup_to_ounces(self.tbs_to_cups(self.tsps_to_tbs(quantity))))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(self.cup_to_ounces(self.tbs_to_cups(self.tsps_to_tbs(quantity)))))
            desired_metric.append('mL')
        if metric in ['ounce', 'oz', 'ounces', 'oz']:
            desired_quantity.append(quantity)
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(quantity))
            desired_metric.append('mL')
        if metric in ['quart', 'qt', 'qts', 'quarts']:
            desired_quantity.append(self.cups_to_ounces(self.pints_to_cups(self.quart_to_pints(quantity))))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(self.cup_to_ounces(self.pints_to_cups(self.quart_to_pints(quantity)))))
            desired_metric.append('mL')
        if metric in ['pt', 'pint', 'pints', 'pts']:
            desired_quantity.append(self.cups_to_ounces(self.pints_to_cups(quantity)))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(self.cup_to_ounces(self.pints_to_cups(quantity))))
            desired_metric.append('mL')
        if metric in ['gallon', 'gal', 'gallons']:
            desired_quantity.append(self.cups_to_ounces(self.pints_to_cups(self.quart_to_pints(self.qallon_to_quart(quantity)))))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(self.cup_to_ounces(self.pints_to_cups(self.quart_to_pints(self.gallon_quart(quantity))))))
            desired_metric.append('mL')
        if metric in ['pound', 'lb', 'lbs', 'pounds']:
            desired_quantity.append(self.pounds_to_ounces(quantity))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_grams(self.pounds_to_ounces(quantity)))
            desired_metric.append('g')
            desired_quantity.append(self.pounds_to_kilos(quantity))
            desired_metric.append('kg')
        if metric in ['g', 'gram', 'grams']:
            desired_quantity.append(self.grams_to_ounces(quantity))
            desired_metric.append('oz')
            desired_quantity.append(quantity)
            desired_metric.append('g')
            desired_quantity.append(quantity / 1000.0)
            desired_metric.append('kg')
        if metric in ['kg', 'kilogram', 'kilograms', 'kgs']:
            desired_quantity.append(self.pounds_to_ounces(self.kilos_to_pounds(quantity)))
            desired_metric.append('oz')
            desired_quantity.append(quantity / 1000.0)
            desired_metric.append('g')
            desired_quantity.append(quantity)
            desired_metric.append('kg')
        if metric in ['milliliter', 'mL', 'mLs', 'milliliters']:
            desired_quantity.append(self.mL_to_ounces(quantity))
            desired_metric.append('oz')
            desired_quantity.append(quantity)
            desired_metric.append('mL')
        if metric in ['liter', 'L', 'liters']:
            desired_quantity.append(self.mL_to_ounces(quantity / 1000.0))
            desired_metric.append('oz')
            desired_quantity.append(quantity / 1000.0)
            desired_metric.append('mL')
        if metric in ['cup', 'cups']:
            desired_quantity.append(self.cup_to_ounces(quantity))
            desired_metric.append('oz')
            desired_quantity.append(self.ounces_to_mL(self.cup_to_ounces(quantity)))
            desired_metric.append('mL')
        output = dict(zip(desired_metric, desired_quantity))
        return output

    def perform_metric_aggregates(self, row):
        try:
            output = self.metric_aggregate(row['metric'], row['quantity'])
        except:
            try:
                output = {'quantity': row['quantity']}
            except:
                output = {'quantity': None}
        return output

    def fix_quantity(self, x):
        add_list = []
        x = x.split(' ')
        for y in x:
            try:
                z = y.split('/')
                add_list.append(float(z[0]) / float(z[1]))
            except:
                add_list.append(int(y))
        return sum(add_list)
