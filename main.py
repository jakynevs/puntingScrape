# import parameters
import time
import csv
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from random import randrange

# specifies the path to the chromedriver.exe
driver = webdriver.Chrome()  
url = "https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2022/07/16&Racecourse=ST&RaceNo=1"

# Load Jockey website   
driver.get(url)
time.sleep(randrange(5, 10))
race_dates = []

# Function to scrape each page
def scrape_page():    
    # Load beatiful soup to find the table
    soup = BeautifulSoup(driver.page_source, 'html.parser')    
    # All table data stored in race variable
    tables = soup.find_all('table')
    html_string_io = StringIO(str(tables))
    
    dfs = pd.read_html(html_string_io)
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
            trackConditions.extend([None] * number_horses)
        
    except Exception as e:
        print(f"Error trying to scrape track condition. Details: {str(e)}")
        pass
        
    # Get tidy horse names
    try:
        horses_messy = race['Horse'].values
    except Exception as e:
        print(f"horses_messy error: {str(e)}")
        
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
    with open('Scraped Data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# open csv file with list of last season race date and add to csv list
with open('Dates to Scrape.csv', newline='') as File:
    reader = csv.DictReader(File)
    for row in reader:
        race_dates.append(row['Dates'])

# Create csv file
with open('Scraped Data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write row headings
        fieldnames = ['Date', 'Horse', 'Jockey', 'Trainer', 'Track Condition', 'LBW']
        writer.writerow(fieldnames)


for d in race_dates:
    dropdown = Select(driver.find_element(By.ID, "selectId"))
    dropdown.select_by_value(d)
    go_button = driver.find_element(By.XPATH, '//*[@id="submitBtn"]/img')
    go_button.click()

    # Scrape the content to csv
    try:
        scrape_page()
    except Exception as e:
        print(f"Error trying to scrape at date: {d}. Details: {str(e)}")

    # Find number of races. We count number of td tags in the racecard class and takeaway 2
    try:
        parentDiv = driver.find_element(By.XPATH, '//*[@id="innerContent"]/div[2]/div[2]/table')
    except NoSuchElementException:
        try:
            parentDiv = driver.find_element(By.XPATH, '//*[@id="innerContent"]/div[2]/div[2]/table/tbody/tr')
        except NoSuchElementException:
            parentDiv = None
    
    if parentDiv == None:
        print(f"Can't find parent race element for {d}")
        count = 0
    else:
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
        
