from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    


#Python3
class Mydriver(metaclass=Singleton):
    def __init__(self) -> None:
        self.driver = self.start_driver()
        print("init")

    def start_driver(self,browser='firefox'):
        """
        Reload the driver and return it for a cleaner way to use.
        Supported browsers: 'chrome', 'firefox', 'edge'
        """

        driver = None

        if browser.lower() == 'chrome':
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--user-agent=YourUserAgentString")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)
        elif browser.lower() == 'firefox':
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--user-agent=YourUserAgentString")
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--disable-gpu")
            firefox_options.add_argument("--disable-software-rasterizer")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--disable-extensions")
            firefox_options.add_argument("--disable-web-security")
            firefox_options.add_argument("--dns-prefetch-disable")
            firefox_options.add_argument("--no-sandbox")
            driver = webdriver.Firefox(options=firefox_options)
        elif browser.lower() == 'edge':
            edge_options = EdgeOptions()
            edge_options.add_argument("--user-agent=YourUserAgentString")
            edge_options.add_argument("--headless")  # make it run without window
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--disable-software-rasterizer")
            driver = webdriver.Edge(options=edge_options)
        else:
            raise ValueError(f"Unsupported browser: {browser}. Please choose from 'chrome', 'firefox', or 'edge'.")

        # Remove implicit wait
        driver.implicitly_wait(5)
        return driver

    def get_driver(self):
        return self.driver
