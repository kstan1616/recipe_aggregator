from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class WebDriver:
    DOWNLOAD_DIR = '/tmp'

    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()

        self.options.add_argument('--disable-extensions')
        if headless:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--no-sandbox')

        self.options.add_experimental_option(
            'prefs', {
                'download.default_directory': self.DOWNLOAD_DIR,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
            }
        )

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def open(self):
        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.driver.implicitly_wait(10)

    def close(self):
        self.driver.quit()

    def login(self):
        # Change this function to your needs and add other functions, etc...
        self.driver.get('http://www.test.com')
        username_field = self.driver.find_element_by_id('username')
        username_field.clear()
        username_field.send_keys('username')
        username_field.send_keys(Keys.RETURN)
        assert 'Login successful' in driver.page_source
        self.driver.close()