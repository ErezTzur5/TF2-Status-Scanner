import re
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tf_utils import sorter
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


steam_id_file = sorter("tf2.txt")


def data_patch(bp_data):
    result = []
    if len(bp_data) == 0:
        return None
    for item in bp_data:
        item_str = str(item)
        
        # Replace single quotes with an empty string
        item_str = item_str.replace("'", "")
        
        item_name = item_str.split('=')[1].strip().split(',')[0].strip()
        price = item_str.split('=')[2].strip().split(',')[0].strip()
        img = item_str.split('=')[3].strip().split(',')[0].strip()
        
        result.append((item_name, price, img))
    return result




def start_driver(browser='chrome'):
    """
    Reload the driver and return it for a cleaner way to use.
    Supported browsers: 'chrome', 'firefox', 'edge'
    """
    driver = None

    if browser.lower() == 'chrome':
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--user-agent=YourUserAgentString")
        chrome_options.add_argument("--headless")  # make it run without window
        # chrome_options.add_argument("--disable-features=InterestCohort")
        driver = webdriver.Chrome(options=chrome_options)
    elif browser.lower() == 'firefox':
        firefox_options = FirefoxOptions()
        driver = webdriver.Firefox(options=firefox_options)
    elif browser.lower() == 'edge':
        edge_options = EdgeOptions()
        driver = webdriver.Edge(options=edge_options)
    else:
        raise ValueError(f"Unsupported browser: {browser}. Please choose from 'chrome', 'firefox', or 'edge'.")

    # Remove implicit wait
    # driver.implicitly_wait(20)
    
    return driver

def wait_for_element(driver, by, value, timeout=1):
    print(f"Waiting for element with {by}: {value}")
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.visibility_of_element_located((by, value)))
    print("Element found and visible")
    return element
    


def fetch_bp_data(steam_id_string):
    bp_data = {}
    items_list = []  # Initialize items_list outside the try block
    
    driver = start_driver()

    url = f'https://backpack.tf/profiles/{steam_id_string}'

    driver.get(url)

    pattern = ".*background-image:url\((.*)\).*<span>(.*)<\/span>.*<span[^>]*>(.*)<\/span>"

    ten_items = []
    try:
        print("Getting BP DATA FROM :",steam_id_string)
        sort = wait_for_element(driver,By.XPATH,"//span[@class='current-sort']")
        if sort:
            sort.click()
            group_value = wait_for_element(driver,By.XPATH,"//a[normalize-space()='Group by value']")
            if group_value:
                group_value.click()
                all_item = None
                try:
                    all_item = wait_for_element(driver, By.CLASS_NAME, "item")
                    item_garb = driver.find_elements(By.CLASS_NAME, "item")
                    ten_items = item_garb[:10]
                except Exception as e:
                    print("Error waiting for 'all_item':", str(e))
                
                if not all_item:
                    driver.refresh()
                    print("NO ITEMS - Refreshing page...")
            else:
                driver.refresh()
                print("Refreshing page after Group by value not found...")
        else:
            driver.refresh()
            print("Refreshing page after sort not found...")
        
    
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


                # print(len(image),type(image))dddddddddd
                image = str(image).split(',')[0]
                name = re.sub(r'\d+', '', name).strip()
                if image[-1] == ")":
                    image = image[:-1]
                # print('image:\n',image)

                item_dict = {
                    "image": image,
                    "price": price,
                    "name": name
                }
                items_list.append(item_dict)
            else: #without price
                pass

    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        # You don't need to reassign items_list here
        pass

    # Move the assignment outside the finally block
    bp_data = items_list  # returns steam id as key and all items as values
    return bp_data


def get_items(STEAM_IDS):
    bp_data = {}
    threads = []

    def fetch_and_save_data(steam_id):
        bp_data[steam_id] = fetch_bp_data(steam_id)


    for steamid in STEAM_IDS:
        steam_id_string = str(steamid)
        thread = threading.Thread(target=fetch_and_save_data, args=(steam_id_string,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    return bp_data


a = get_items(steam_id_file)
print(a)