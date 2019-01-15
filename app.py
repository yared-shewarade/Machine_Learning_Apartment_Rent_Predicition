# import necessary libraries
import os
from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from jinja2 import Template
from forms import UserInput
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests as req
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from splinter import Browser
import pickle 

# import api_key of google map
from config import gkey

# Flask Setup
app = Flask(__name__)
app.secret_key = "secret_key"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/userinput", methods=['GET', 'POST'])
def userinput():
    global userinput
    form = UserInput(request.form)
    if request.method == "POST":
        userinput = {
            'street': form.street.data,
            'city': form.city.data,
            'state': form.state.data,
            'Bed': form.bed.data,
            'Bath': form.bath.data,
            'SF': form.sf.data,
            "Concessions %": form.free_rent.data/12,
            "Washer/Dryer_0": form.washer_dryer_0.data,
            "Washer/Dryer_1": form.washer_dryer_1.data,
            "Washer/Dryer_2": form.washer_dryer_2.data,
            "Walk in Closet": form.walk_in_closet.data,
            "Hardwood/Vinyl Floor": form.hardwood_vinyl_floor.data
        }
        global Address
        Address = str.title(userinput['street']) + ' ' + str.title(userinput['city']) + ' ' + str.upper(userinput['state'])
        return redirect("/scraping")

    return render_template("userinput.html", form=form)
    
@app.route("/scraping", methods=['GET', 'POST'])
def scraping():
# Scrape miles from Domain and Downtown

    payload = {
        "units": "imperial",
        "origins": Address, 
        "destinations": "11410 Century Oaks Terrace, Austin, TX 78758|1100 Congress Ave, Austin, TX 78701",
        "key": "AIzaSyCQhKXIlYN6TQ3MHT4lujpN0lXAyB1Tvyo"
    }

    response = req.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = payload).json()

    global miles_from_domain
    global miles_from_downtown
    miles_from_domain = response['rows'][0]['elements'][0]['distance']['text']
    miles_from_downtown = response['rows'][0]['elements'][1]['distance']['text']
    miles_from_domain = miles_from_domain.split(' ')[0]
    miles_from_downtown = miles_from_downtown.split(' ')[0]

# Scrape demographic data

    # URL of page to be scraped
    url_income = "http://www.energyjustice.net/justice/index.php"
    url_population = "https://www.freemaptools.com/find-population.htm"
    
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    global median_household_income
    browser.visit(url_income)
    browser.fill('gsLocation', Address)
    browser.find_by_name('gsSubmit_desk').first.click()
    time.sleep(5)
    browser.find_by_id('income_layer_desk').first.click()
    time.sleep(5)
    map_soup = BeautifulSoup(browser.html, 'html.parser')
    income = map_soup.find_all('table')[1].find_all('td')[1].text
    income = income.split(' ')[0]
    income = income.split('$')[1]
    income = income.split(',')[0] + income.split(',')[1]
    median_household_income = float(income)
    
    browser.quit()

    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    
    global population 
    browser.visit(url_population)
    time.sleep(5)
    browser.fill('radiusinputkm', '1.61')
    time.sleep(3)
    browser.find_by_id('tb_searchlocation').fill(Address)
    browser.find_by_id('tb_searchlocation').fill('\n')
    time.sleep(3)
    browser.find_by_tag('p')[3].click()
    population = browser.find_by_id('div_output').text
    population = population.split(' ')[-1]
    if population == "Wait...":
        population = 21658

    browser.quit()

# Scrape the built_year
    # set the chromedriver path
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    costar_url = "https://costar.com/"
    browser.visit(costar_url)

    # login
    browser.click_link_by_id('loginLink')
    browser.fill('username', 'SDong2')
    browser.fill('password', '719111719111')
    browser.click_link_by_id('loginButton')
    time.sleep(20)

    try:
        x_path = '//*[@id="cs-gateway-home-page"]/div[2]/div[1]/div/div/div[2]/div/div[1]/input'
        search_box = browser.find_by_xpath(x_path)
        search_box.fill(Address)
        search_button = browser.find_by_xpath('//*[@id="react-autowhatever-1--item-0"]/div/span[1]')
        search_button.click()
        time.sleep(15)
        global built_year
        built_year = browser.find_by_xpath('//*[@id="Building_YearBuilt"]/span[2]').text
        if len(built_year) > 4:
            built_year = built_year.split(' ')[1]
            built_year = float(built_year)
        else:
            built_year = float(built_year)
    except:
        built_year = 1997

    browser.quit()

# Scrape walk scores
    # set the chromedriver path
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    walk_score_url = 'https://www.walkscore.com/'
    browser.visit(walk_score_url)
    search_entry = browser.find_by_id('gs-street')
    search_entry.fill(Address)
    time.sleep(10)

    browser.find_by_css('.go-btn')[1].click()
    time.sleep(10)

    html = browser.html
    score_soup = BeautifulSoup(html, 'html.parser')

    scores = []
    for i in range(1,len(score_soup.find_all('img'))):
        try: 
            score_path = score_soup.find_all('img')[i]['src']
            split = score_path.split('/')[-1]
            score = split.split('.')[0]
            scores.append(score)
        except:
            print("no src")
            break
    
    global walk_score
    global transit_score
    walk_score = scores[-3]
    transit_score = scores[-2]
    
    browser.quit()

    # redirect to the machine learning page
    return redirect('/ml')


@app.route("/ml", methods=['GET', 'POST'])
def ml():
    rf_model_filepath = 'static/resources/RF999_Model.sav'
    rf_model = pickle.load(open(rf_model_filepath, 'rb'))

    # input the information
    X_new = [userinput["Bed"],
            userinput["Bath"], 
            userinput["SF"], 
            userinput["Concessions %"],
            built_year,
            userinput["Walk in Closet"],
            userinput["Hardwood/Vinyl Floor"],
            userinput["Washer/Dryer_0"],
            userinput["Washer/Dryer_1"],
            userinput["Washer/Dryer_2"],
            median_household_income,
            population,
            walk_score,
            transit_score, 
            miles_from_domain, 
            miles_from_downtown]

    X_new = pd.to_numeric(X_new)
    X_new = np.reshape(X_new, (1, 16))
    print(X_new)
    rent_estimate = round(rf_model.predict(X_new)[0], 2)
    rent_estimate = f"${rent_estimate}"

    return render_template('index.html', rent_estimate=rent_estimate)

@app.route("/visualization", methods=['GET', 'POST'])
def visualization():
    return render_template('visualization.html')


if __name__ == "__main__":
    app.run(debug=True)
