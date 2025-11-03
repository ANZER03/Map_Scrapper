from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_google_maps_selenium(url):
  # Replace with your webdriver path
  driver = webdriver.Chrome()  
  driver.get(url)

  # Wait for page to load
  time.sleep(5)

  # Get scroll height
  last_height = driver.execute_script("return document.body.scrollHeight")

  while True:
    # Scroll down to bottom
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

    # Wait to load page
    time.sleep(2)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
      break
    last_height = new_height

  # Parse the HTML using BeautifulSoup after scrolling
  soup = BeautifulSoup(driver.page_source, 'html.parser')

  results = []
  for business in soup.find_all('div', class_='Nv2PK'):
    name = business.find('div', class_='qBF1Pd fontHeadlineSmall').text.strip()
    
    rating_span = business.find('span', role="img")
    if rating_span:
      rating = rating_span.find('span', class_='MW4etd').text.strip()
      num_reviews = rating_span.find('span', class_='UY7F9').text.strip('()')
    else:
      rating = None
      num_reviews = None

    # Updated category extraction using explicit wait:
    wait = WebDriverWait(driver, 10) 
    category_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'W4Efsd')))
    category = category_element.find_all('span')[0].text.strip()

    address_spans = business.find('div', class_='W4Efsd').find_all('span')
    address = ' '.join([span.text.strip() for span in address_spans[1:]])

    phone_number = business.find('span', class_='UsdlK')
    phone_number = phone_number.text.strip() if phone_number else None

    website = business.find('a', class_='lcr4fd S9kvJb', data_value="Site Web")
    website = website['href'] if website else None

    hours_span = business.find('span', class_='eXlrNe')
    if hours_span:
      hours = hours_span.text.strip()
    else:
      hours_spans = business.find('div', class_='W4Efsd').find_all('span')
      hours = ' '.join([span.text.strip() for span in hours_spans if span.text.strip()])

    results.append({
      'name': name,
      'rating': rating,
      'num_reviews': num_reviews,
      'category': category,
      'address': address,
      'phone_number': phone_number,
      'website': website,
      'hours': hours
    })

  driver.quit()
  return results

# Example usage:
url = "https://www.google.com/maps/search/natural+stone+in+New+York"
results = scrape_google_maps_selenium(url)

print(results)