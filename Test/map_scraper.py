from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


driver = webdriver.Chrome()  
driver.get('https://www.google.com/maps/search/natural+stone+in+New+York')
driver.implicitly_wait(10)
element = driver.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.JrN27d.SuV3fd.Zjt37e.TGiyyc > div.Ntshyc > div.L1xEbb > h1')
element.click()

def smooth_scroll_to_bottom():
    # driver.implicitly_wait(10)
    # driver.find_element(By.CSS_SELECTOR, '#gen-nav-commerce-header-v2 > div.pre-modal-window.is-active > div > div:nth-child(3) > div > div.ncss-row.mt5-sm.mb7-sm > div:nth-child(2) > button').click()

    # Get the initial page height
    initial_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    n = 0
    while True:
        # Scroll to the bottom
        driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd').send_keys(Keys.END)
        time.sleep(2)  # Adjust this sleep duration if needed
        # driver.implicitly_wait(10)
        n+=1
        if n == 10:
            break
        
smooth_scroll_to_bottom()
data = []
try :
    elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'Nv2PK.tH5CWc.THOPZb'))
            )
    for element in elements:
            try :
                name = element.find_element(By.CLASS_NAME , 'qBF1Pd.fontHeadlineSmall')
                name = (name.text)
            except :
                name = None
            
            try :
                # name = element.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div > div:nth-child(2) > span:nth-child(2) > span.UsdlK')
                phone = element.find_element(By.CLASS_NAME , 'UsdlK')
                phone = (phone.text)
            except :
                phone = None
            try :
                # name = element.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div > div:nth-child(2) > span:nth-child(2) > span.UsdlK')
                category = element.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(1) > span')
                category = (category.text)
            except :
                category = None
            try :
                # name = element.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div > div:nth-child(2) > span:nth-child(2) > span.UsdlK')
                address = element.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(2) > span:nth-child(2)')
                address = (address.text)
            except :
                address = None
            try :
                # name = element.find_element(By.CSS_SELECTOR , '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div > div:nth-child(2) > span:nth-child(2) > span.UsdlK')
                website = element.find_element(By.CLASS_NAME , 'lcr4fd.S9kvJb')
                website = (website.get_attribute('href'))
            except :
                website = None
                
            data.append({
        'name': name,
        'category': category,
        'address': address,
        'phone_number': phone,
        'website': website,
        })
    
except Exception as e:
    print(e)

import pandas as pd
df = pd.DataFrame(data)
df.to_excel('data.xlsx' , index=False)
print('-----------------------')
print('Finally')
driver.close()



















