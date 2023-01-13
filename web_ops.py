import urllib
from selenium import webdriver
from selenium.webdriver import FirefoxOptions, Firefox
import json
import traceback
import pathlib
from pywinauto import Application, keyboard

firefox_bin = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
gecko_driver = "C:\\Users\\Kariuki\\Documents\\2022\Projects\\Python\\Projects\\Pdf downloader\\geckodriver.exe"
base_url = 'https://steinerlibrary.org/'
data_file = 'RudolfSteinerData.json'


def set_up_driver():
     # Create a FirefoxOptions object to configure the browser
        options = FirefoxOptions()

        # Set the location of the Firefox executable
        options.binary_location = firefox_bin

        # Configure the browser to download PDF files automatically, without prompting
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/pdf')

        # configure for browserless
        # options.add_argument("--headless")

        # Create a new FirefoxDriver using the specified options
        driver = Firefox(options=options)

        # Delete all cookies to start with a clean session
        driver.delete_all_cookies()

        return driver
    
def download_file(driver: webdriver, pdf_name:str, pdf_url: str):
    pdf_url = urllib.parse.urljoin(base_url, pdf_url)
    download_loc = pathlib.Path.cwd().joinpath('downloads')

    try:
        # got to pdf page
        driver.get(pdf_url)
        print("loading url...")
        
        download_icon = driver.find_element_by_id("download")
        download_icon.click()

        # print("download btn clicked...")
       
        app = Application().connect(title_re=".*Mozilla Firefox")
        app = app.top_window()

        loc = app.Toolbar4
        # file_name = app.Edit.texts().pop()

        # print("setting download path...")
        loc.set_keyboard_focus()
        loc.click(double=True)
    
        # keyboard.send_keys('^a')
        print(loc.get_properties())
        keyboard.send_keys(f"{download_loc}")
        keyboard.send_keys("{ENTER}")

        # print("clicking save...")
        save = app.child_window(title="&Save",class_name="Button")
        save.click_input(double=True)
    
    except Exception :
        print("An error occurred while downloading the file.")
        print(traceback.format_exc())
    else:
        print(f'{pdf_name} downloaded succesfully...')

def close_driver(driver: webdriver):
    driver.close()


def filter_by_key(key: str, data: json) -> list:
    filtered = filter(lambda k: k == key, data)

    return filtered


    
# def check_download(driver: webdriver, **args):
#     options = args['options']
#     options.headless = True
#     driver = webdriver.Firefox(options=options)

#     log = driver.get_log

