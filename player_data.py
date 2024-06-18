import requests
import re
import time
from selenium.webdriver.common.by import By
from driver import Mydriver
from tf_utils import sorter , minutes_to_hours
import multiprocessing


API_KEY = '31475B06B733BC05DE0DB5BCFD3FECE0'


driver = None

class Player:
    def __init__(self,steam_id,player_name='',hours_played={"hours":str(0)},items={},inventory_date = '') -> None:
        self.steam_id:str = steam_id
        self.player_name:str = player_name
        self.hours_played:dict = hours_played
        self.items:dict = items
        self.inventory_date:str = inventory_date
        


    def __str__(self) -> str:
        return f'{self.steam_id},{self.player_name},{self.hours_played},{self.items}'

    def get_name(self):
        # Construct the API endpoint URL to get player summaries
        profile_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={self.steam_id}&format=json'

        # Make an HTTP GET request to the API to get profile information
        profile_response = requests.get(profile_url)

        if profile_response.status_code == 200:
            profile_data = profile_response.json()

            if 'response' in profile_data and 'players' in profile_data['response']:
                players_list = profile_data['response']['players']
                if players_list:
                    player = players_list[0]  # Assuming only one player is returned
                    self.player_name = player.get('personaname', 'Unknown')  # Get the display name

                else:
                    print('No player data found for the provided Steam Community ID.')

            else:
                print('Error retrieving profile data.')

        else:
            print('Profile API request failed.')


    def get_hours(self):
        # Set include_played_free_games parameter
        include_played_free_games = 1  # Set to 1 to include played free games

        # Construct the API endpoint URL with the new parameter
        url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={self.steam_id}&format=json&include_played_free_games={include_played_free_games}'

        # Make an HTTP GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()


            if 'response' in data and 'games' in data['response']:
                games = data['response']['games']

                total_playtime = 0

                for game in games:
                    if game['appid'] == 440:
                        total_playtime += game.get('playtime_forever', 0)  # minutes
                        total_playtime_hours = minutes_to_hours(total_playtime)
                        # if float(total_playtime_hours) < 800:
                        self.hours_played = {'hours': total_playtime_hours}
                        # else:
                        #     break  # Exit the loop early if playtime is None or >= 800 hours               
            else:
                print('Error retrieving playtime data.')

        else:       
            print('API request failed.')

        

    def get_items(self,driver):
        items_list = []  #Initialize items_list outside the try block

        url = f'https://backpack.tf/profiles/{self.steam_id}'

        driver.get(url)
        time.sleep(3)
        pattern = ".*background-image:url\((.*)\).*<span>(.*)<\/span>.*<span[^>]*>(.*)<\/span>"

        ten_items = []
        number_of_tries = 0
        while number_of_tries < 2:
            try:
                print("Getting BP DATA FROM :",self.steam_id)
                sort = driver.find_element(By.CSS_SELECTOR,".current-sort")
                if sort:
                    sort.click()
                    group_value = driver.find_element(By.CSS_SELECTOR,"li[data-value='price'] a")
                    if group_value:
                        group_value.click()
                        try:
                            time.sleep(0.5)
                            print('Trying to get items')
                            all_item = driver.find_element(By.CLASS_NAME, "item")
                            inventory_date = driver.find_element(By.ID,"inventory-time-label").text
                            self.inventory_date = {'inventory_date': inventory_date}

                            item_garb = driver.find_elements(By.CLASS_NAME, "item")
                            ten_items = item_garb[:10]
                            number_of_tries = 4
                            print(f"Got Items for:{self.steam_id}")
                        except Exception as e:
                            print(number_of_tries,"Error waiting for all items")
                            number_of_tries += 1
                            driver.refresh()  
                            time.sleep(0.5)    
                    else:
                        print(number_of_tries,"Refreshing page after Group by value not found...")
                else:
                    print(number_of_tries,"Refreshing page after sort not found...")
                
            
                for element in ten_items:
                    # Get the outer HTML of the element
                    element_html = element.get_attribute('innerHTML')

                    text = element_html.replace("\n","")
                    items = re.findall(pattern,text)
                    if len(items) > 0:
                        item = items[0]
                        image = item[0]
                        price = item[1]
                        name = item[2]


                        image = str(image).split(',')[0]
                        name = re.sub(r'\d+', '', name).strip()
                        if image[-1] == ")":
                            image = image[:-1]


                        item_dict = {
                            "image": image,
                            "price": price,
                            "name": name
                        }
                        items_list.append(item_dict)
                    else: #without price
                        pass
            except Exception as e:
                number_of_tries += 1
                print(number_of_tries,"cant find [@class='current-sort']")
            finally:
                print('FINALLY')
        self.items = items_list



def main():
    steam_id_file = sorter("tf.txt")
    num_processes = 5
    

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(data, steam_id_file)
        pool.map(driver_quit,[None]* num_processes)
    

def driver_quit(mylist):
    Mydriver().get_driver().quit()

    

def data(idd):

    player = Player(idd)
    player.get_name()
    player.get_hours()
    driver = Mydriver().get_driver()
    player.get_items(driver)
    print()
    print('Name:', player.player_name, 'Hours:', player.hours_played, '\nItems:\n', player.items)
    print()




if __name__ == '__main__':
    # start_time = time.time()
    # main()
    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print("Elapsed Time:", elapsed_time, "seconds")

    pass