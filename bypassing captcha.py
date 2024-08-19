from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import os
import wx
import cv2
import numpy as np
import time
app = wx.App()

def chromedriver():
    try:
        options = webdriver.ChromeOptions()
        options = Options()
        service = Service('C:\\Translation EXE\\chromedriver.exe')
        browser = webdriver.Chrome(service=service, options=options)
        browser.maximize_window()
    except:
        pass
    browser.maximize_window()
    browser.get('https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic?pageSize=5000&firstSearch=true&searchType=basic&level_1=on&dateType=isDate&tenderStartDate=2024/08/01&tenderEndDate=2024/08/14&radProctrgCate=')
    time.sleep(2)
    Navigation(browser)
    
def Navigation(browser):
    collected_link = []
    tr_count = 1
    error = True
    while error == True:
        for tender_url in browser.find_elements(By.XPATH,'//*[@class="tb_01"]/tbody/tr['+str(tr_count)+']/td[3]/a'):
            tender_url_link = tender_url.get_attribute('href')
            print(tender_url_link)
            collected_link.append({'tender url':tender_url_link})
            if(len(collected_link)) == 10:
                scrap_data(collected_link,browser)
            tr_count += 1

def scrap_data(collected_link,browser):
    for url in collected_link:
        error = True
        while error == True:
            browser.get(url['tender url'])
            time.sleep(5)
            if '驗證碼檢核' in browser.page_source:
                a = True
                while a == True:  
                    try:
                        captcha_element = browser.find_element(By.XPATH,'//*[@id="validateForm"]/table[1]/tbody/tr[1]/td/table/tbody/tr/td[2]/img')
                        captcha_screenshot = captcha_element.screenshot_as_png
                        captcha_image = cv2.imdecode(np.frombuffer(captcha_screenshot, np.uint8), cv2.IMREAD_COLOR)
                        images_xpath = '//*[@border="1"]/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/label/img'
                        template_files = []
                        template_elements = browser.find_elements(By.XPATH,images_xpath)
                        for index, element in enumerate(template_elements):
                            template_screenshot = element.screenshot_as_png
                            template_image = cv2.imdecode(np.frombuffer(template_screenshot, np.uint8), cv2.IMREAD_COLOR)
                            template_filename = f"template_card{index+1}.png"
                            cv2.imwrite(template_filename, template_image)
                            template_files.append({'template_filename':template_filename, 'index' : index+1})
                        Clicked_templates = []
                        for template_file in template_files:
                            template = cv2.imread(template_file['template_filename'], cv2.IMREAD_COLOR)
                            result = cv2.matchTemplate(captcha_image, template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            threshold = 0.8
                            if max_val > threshold:
                                Clicked_templates.append(template_file)
                                top_left = max_loc
                                bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
                                cv2.rectangle(captcha_image, top_left, bottom_right, (0, 255, 0), 2)
                                matched_element = browser.find_element(By.XPATH, f'//*[@border="1"]/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td['+str(template_file['index'])+']/label/img')
                                matched_element.click()
                                time.sleep(10)
                        if len(Clicked_templates) > 2:
                            refresh_button = browser.find_element(By.XPATH,'//*[@id="b_refresh"]')
                            refresh_button.click()
                            time.sleep(5)
                            a = True
                        else:
                            searchButton = browser.find_element(By.XPATH,'//*[@id="b_submit"]')
                            searchButton.click()
                            time.sleep(10)
                        for template_file in template_files:
                            os.remove(template_file['template_filename'])
                        a = False
                    except Exception as e:
                        print(e)
                        a = True
chromedriver()