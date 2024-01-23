# import parameters
import time
import csv
from constants import * 
from selenium import webdriver
from random import randrange
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# specifies the path to the chromedriver.exe
driver_path = dp
driver = webdriver.Chrome()  
url = "https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2022/07/16&Racecourse=ST&RaceNo=1"

# Load Jockey website   
driver.get(url)
time.sleep(randrange(5, 10))
race_dates = []

# open csv file with list of last season race date and add to csv list
with open('2023 Race Dates.csv', newline='') as File:
    reader = csv.DictReader(File)
    for row in reader:
        race_dates.append(row['Dates'])

# Create csv file
with open('Race.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write row headings
        fieldnames = ['Date', 'Horse', 'Jockey', 'Trainer', 'Track Condition', 'LBW']
        writer.writerow(fieldnames)

# Function to scrape each page
def scrape_page():    
    # Load beatiful soup to find the table
    soup = BeautifulSoup(driver.page_source, 'html.parser')    
    # All table data stored in race variable
    tables = soup.find_all('table')
    dfs = pd.read_html(str(tables))
    race = dfs[2]
    number_horses = (len(race))

    # Get race title, date and track condition
    race_title_element = driver.find_element(By.CLASS_NAME, 'f_fl')
    race_title =  (race_title_element.text)
    dates = []
    dates.extend([race_title[15:25]] * number_horses)
    # track condition (tc)
    trackConditions = []
    try:
        trackCondition = (driver.find_element(By.XPATH, '//*[@id="innerContent"]/div[2]/div[4]/table/tbody/tr[2]/td[3]').text)
        if trackCondition == 'YIELDING' or trackCondition =='YIELDING TO SOFT' or trackCondition == 'SOFT' or trackCondition == 'HEAVY':
            trackConditions.extend([trackCondition] * number_horses)
        else: 
            blank = ''
            trackConditions.extend([None] * number_horses)
        
    except: 
        print("tc error")
        pass
        

# track condition (tc)
    trackConditions = []
    try:
        trackCondition = driver.find_element_by_xpath('//*[@id="innerContent"]/div[2]/div[4]/table/tbody/tr[2]/td[3]')
        if trackCondition == 'YIELDING' or trackCondition =='YIELDING TO SOFT' or trackCondition == 'SOFT' or trackCondition == 'HEAVY':
            trackConditions.extend([trackCondition] * number_horses)
        else: 
            trackConditions.extend([None] * number_horses)

    except: 
        print("tc error")
        pass

    # Get tidy horse names
    try:
        horses_messy = race['Horse'].values
    except:
        print('horses_messy error')
    horses = []
    for h in horses_messy:
        horses.append(h[:-6])

    # Get Jockeys, Trainers and lbw result
    jockeys = race['Jockey'].values
    trainers = race['Trainer'].values
    lbws = race['LBW'].values  

    # Combine lists to race rows
    rows = zip(dates, horses, jockeys, trainers, trackConditions, lbws)

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
    try:
        scrape_page()
    except:
        print("Error trying to scrape at date: ", d)
    # Find number of races. We count number of td tags in the racecard class and takeaway 2
    parentDiv = driver.find_element(By.XPATH, '//*[@id="innerContent"]/div[2]/div[2]/table')
    count = len(parentDiv.find_elements(By.TAG_NAME, "td"))

    # Cycle through each race
    for c in range(count)[3:14]:
        x_path = '//*[@id="innerContent"]/div[2]/div[2]/table/tbody/tr[1]/td[' + str(c) + ']/a/img'
        try:
            button = driver.find_element(By.XPATH, x_path)
            button.click()

        except:
            continue
    
        try:    
            # Scrape the content to csv
            scrape_page()
        
        except:
            driver.back()
            continue

