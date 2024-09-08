import subprocess
import datetime
from record import JobRecord
from web_driver import CustomWebDriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from pytz import timezone
import csv

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

class Bot():

    def __init__(self, url) -> None:
        self.driver = CustomWebDriver()
        self.url = url

    def scrape_data(self):
        
        cards = []

        options = self.driver.get_options()

        browser = webdriver.Chrome(service=self.driver.get_service(), options=options)
        browser.get(url)

        cards.extend(browser.find_elements(by=By.CLASS_NAME, value='resultContent'))

        print(f'Number of cards found {len(cards)}')

        records = list(self.get_jobs(cards))

        with open('vagas_indeed_jr.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["job_url", "job_title", "company", "location", "job_date", "job_id"])
            for record in records:
                writer.writerow([record.job_url, record.job_title, record.company, record.location, record.job_date, record.job_id])

    def get_brasilia_date_time_str(self) -> str:
        return datetime.now(timezone('America/Sao_Paulo')).strftime(DATE_TIME_FORMAT)        

    def convert_to_record(self, card)-> JobRecord:
        record = JobRecord()

        url_template = 'https://br.indeed.com/ver-emprego?jk={}'

        if isinstance(card, WebElement):
            web_element = card 
        else:
            return None

        element = web_element.find_element(by=By.TAG_NAME, value='a') 

        record.job_id = element.get_attribute('data-jk')    
        record.job_title = element.text    

        record.job_url = url_template.format(record.job_id)
 
        try:
            record.company = web_element.find_element(by=By.XPATH, value='.//span[@data-testid="company-name"]').text if (
                not web_element.find_element(by=By.XPATH, value='.//span[@data-testid="company-name"]') == None) else ''
        except NoSuchElementException:
            record.company = ''

        location = web_element.find_element(
            by=By.XPATH, value='.//div[@data-testid="text-location"]') 

        if location is None:
            record.location = ''
        else:
            record.location = location.text            

        record.job_date = self.get_brasilia_date_time_str()    

        return record   

    def get_jobs(self, cards: []) -> []:
        result = []

        for card in cards:
            record = self.convert_to_record(card)

            if not record is None:
                result.append(record)

        return result

if __name__ == '__main__':
    url = 'https://br.indeed.com/jobs?q=junior+desenvolvedor&l=remoto&sort=date'
    bot = Bot(url) 
    bot.scrape_data()