# import parameters
import time
import csv
from constants import * 
from selenium import webdriver
from random import randrange
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select


# specifies the path to the chromedriver.exe
driver_path = dp
driver = webdriver.Chrome(driver_path)
url = "https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2022/07/16&Racecourse=ST&RaceNo=1"

# Load Jockey website
driver.get(url)
time.sleep(randrange(5, 10))
race_dates = []

# open csv file with list of last season race date and add to csv list
with open('2021 Race Dates.csv', newline='') as File:
    reader = csv.DictReader(File)
    for row in reader:
        race_dates.append(row['Dates'])

# Create csv file
with open('Race.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write row headings
        fieldnames = ['Date', 'Horse', 'Jockey', 'Trainer', 'LBW']
        writer.writerow(fieldnames)

# Function to scrape each page
def scrape_page():    
    # Load beatiful soup to find the table
    soup = BeautifulSoup(driver.page_source, 'lxml')    
    # All table data stored in race variable
    tables = soup.find_all('table')
    dfs = pd.read_html(str(tables))
    race = dfs[2]
    number_horses = (len(race))


    # Get race title and take date
    race_title_element = driver.find_element_by_class_name('f_fl')
    race_title =  (race_title_element.text)
    dates = []
    dates.extend([race_title[15:25]] * number_horses)

    # Get tidy horse names
    horses_messy = race['Horse'].values
    horses = []
    for h in horses_messy:
        horses.append(h[:-6])

    # Get Jockeys, Trainers and lbw result
    jockeys = race['Jockey'].values
    trainers = race['Trainer'].values
    lbws = race['LBW'].values       

    # Combine lists to race rows
    rows = zip(dates, horses, jockeys, trainers, lbws)

    # Write to excel
    with open('Race.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

for d in race_dates:
    dropdown = Select(driver.find_element_by_id("selectId"))
    dropdown.select_by_value(d)
    go_button = driver.find_element_by_xpath('//*[@id="submitBtn"]/img')
    go_button.click()

    # Scrape the content to csv
    scrape_page()
    
    # Find number of races. We count number of td tags in the racecard class and takeaway 2
    parentDiv = driver.find_element_by_xpath('//*[@id="innerContent"]/div[2]/div[2]/table')
    count = len(parentDiv.find_elements_by_tag_name("td"))

    # Cycle through each race
    for c in range(count)[3:14]:
        x_path = '//*[@id="innerContent"]/div[2]/div[2]/table/tbody/tr[1]/td[' + str(c) + ']/a/img'
        try:
            button = driver.find_element_by_xpath(x_path)
            button.click()

        except:
            continue
    
        try:    
            # Scrape the content to csv
            scrape_page()
        
        except:
            driver.back()
            continue

