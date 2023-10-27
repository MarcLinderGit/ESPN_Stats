from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import pandas as pd
import re

class PlayerBioScraper:
    def __init__(self, chrome_path='chromedriver.exe'):
        self.chrome_path = chrome_path
        self.driver = None
        self.all_player_info = {}
        self.csv_exported = False

    def initialize_driver(self):
        chrome_service = ChromeService(executable_path=self.chrome_path)
        self.driver = webdriver.Chrome(service=chrome_service)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def scrape_player_info(self, player_links_dict):
        self.initialize_driver()

        # Create a temporary dictionary for this call
        temp_player_info = {}

        for player_name, player_link in player_links_dict.items():
            self.driver.get(player_link)
            self.driver.implicitly_wait(10)
            player_bio_page = self.driver.page_source
            soup = BeautifulSoup(player_bio_page, 'html.parser')
            player_info = self.extract_player_info(soup)
            temp_player_info[player_name] = player_info

        self.close_driver()

        # Merge the data into the main dictionary
        self.all_player_info.update(temp_player_info)

    def extract_player_info(self, soup):
        player_info = {}
        player_info['Team'] = soup.find('a', class_='AnchorLink clr-black').get_text(strip=True)
        player_info['Number'] = soup.find_all('li', class_='')[0].get_text(strip=True)
        player_info['Position'] = soup.find_all('li', class_='')[1].get_text(strip=True)
        player_info['HT/WT'] = soup.find('div', string='HT/WT').find_next('div').get_text(strip=True)
        player_info['Birthdate'] = soup.find('div', string='Birthdate').find_next('div').get_text(strip=True)
        player_info['College'] = self.extract_college(soup)
        player_info['Draft Info'] = self.extract_draft_info(soup)
        return player_info

    def extract_college(self, soup):
        college_elem = soup.find('div', string='College')
        if college_elem:
            college_info = college_elem.find_next('a')
            return college_info.get_text(strip=True) if college_info else "Not Available"
        return "Not Available"

    def extract_draft_info(self, soup):
        try:
            draft_info = soup.find('div', string='Draft Info').find_next('div').get_text(strip=True)
            return draft_info
        except AttributeError:
            return "Not Available"

    def split_draft_info(self):
        for player_name, player_info in self.all_player_info.items():
            draft_info = player_info.get('Draft Info', '')

            if not draft_info or draft_info == 'Not Available':
                self.all_player_info[player_name]['Draft_Year'] = 'undrafted'
                self.all_player_info[player_name]['Draft_Round'] = 'undrafted'
                self.all_player_info[player_name]['Draft_Pick_Overall'] = 'undrafted'
                self.all_player_info[player_name]['Draft_Team'] = 'undrafted'
            else:
                draft_info_parts = [part.strip() if part.strip() else "undrafted" for part in re.split(':|, | \(', draft_info)]
                print(draft_info_parts)
                self.all_player_info[player_name]['Draft_Year'], self.all_player_info[player_name]['Draft_Round'], self.all_player_info[player_name]['Draft_Pick_Overall'], self.all_player_info[player_name]['Draft_Team'] = draft_info_parts
                # self.all_player_info[player_name]['Draft_Year'] = self.all_player_info[player_name]['Draft_Year'].replace('Not Available', 'undrafted') 
                self.all_player_info[player_name]['Draft_Round'] = self.all_player_info[player_name]['Draft_Round'].replace('Rd ', '') # Remove Rd 
                self.all_player_info[player_name]['Draft_Pick_Overall'] = self.all_player_info[player_name]['Draft_Pick_Overall'].replace('Pk ', '') # Remove Pk
                self.all_player_info[player_name]['Draft_Team'] = self.all_player_info[player_name]['Draft_Team'].replace(')', '') # Remove )
                print("this is player info ", self.all_player_info[player_name])
            self.all_player_info[player_name].pop('Draft Info', None)
        print("this is end of split_draft_info: ", self.all_player_info)


    def split_ht_wt(self):
        for player_info in self.all_player_info.values():
            ht_wt = player_info['HT/WT']
            height, weight = [part.strip() for part in ht_wt.split('", ')]
            player_info['Height'] = height
            player_info['Weight'] = weight

    def split_birthdate_age(self):
        for player_info in self.all_player_info.values():
            birthdate = player_info['Birthdate']
            match = re.match(r'^(.*?) \((\d+)', birthdate)
            if match:
                player_info['Birthdate'], player_info['Age'] = match.groups()

    def process_player_info(self):
        self.split_draft_info()
        self.split_ht_wt()
        self.split_birthdate_age()


    def transpose_df(self):
        all_player_info_df = pd.DataFrame(self.all_player_info).T
        print("This is all_player_info", self.all_player_info)
        print("this is the df", all_player_info_df)
        all_player_info_df.drop(columns=['HT/WT'], inplace=True)
        return all_player_info_df

    def export_to_csv(self, file_name='player_bio.csv'):
        self.process_player_info()
        all_player_info_df = self.transpose_df()
        all_player_info_df.to_csv(file_name, index=True)
        self.csv_exported = True

    def get_all_player_info_df(self):
        if not self.csv_exported:
            self.process_player_info()
        all_player_info_df = self.transpose_df()
        return all_player_info_df




# Create an instance of PlayerScraper
#scraper = PlayerBioScraper()

# Call the methods on the instance
#scraper.scrape_player_info(player_links_dict)
# scraper.split_draft_info()
# scraper.split_ht_wt()
# scraper.split_birthdate_age()
# scraper.export_to_csv()