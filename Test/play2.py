import asyncio
import aiohttp
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import streamlit as st
import io
import logging
import requests
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import concurrent.futures


async def process_element_async(element, session, search_query):
    """Extracts data from a single element using BeautifulSoup asynchronously."""
    data = {}
    try:
        data['name'] = element.find(
            class_='qBF1Pd fontHeadlineSmall').text
    except:
        data['name'] = None
    try:
        data['phone_number'] = element.find(
            class_='UsdlK').text
    except:
        data['phone_number'] = None
    try:
        category_element = element.select_one(
            '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(1) > span')
        data['category'] = category_element.text if category_element else None
    except:
        data['category'] = None
    try:
        address_element = element.select_one(
            '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(2) > span:nth-child(2)')
        data['address'] = address_element.text if address_element else None
    except:
        data['address'] = None
    try:
        website_element = element.find(
            class_='lcr4fd S9kvJb')
        data['website'] = website_element['href'] if website_element else None
    except:
        data['website'] = None
    return data

async def scrape_page(url, search_query, session):
    """Scrapes data from a single page asynchronously."""
    async with session.get(url) as response:
        page_source = await response.text()
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all(class_='Nv2PK tH5CWc THOPZb')
        tasks = [process_element_async(element, session, search_query) for element in elements]
        data = await asyncio.gather(*tasks)
        return data

async def main_async(search_query, time_scrolling):
    """Main asynchronous function for scraping and scrolling."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://www.google.com/maps/search/{search_query}')

    all_data = []  # Store extracted data

    async with aiohttp.ClientSession() as session:
        while True:
            # Extract elements and scrape concurrently
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            elements = soup.find_all(class_='Nv2PK tH5CWc THOPZb')
            tasks = [scrape_page(element.find('a')['href'], search_query, session) for element in elements if element.find('a')]
            data = await asyncio.gather(*tasks)
            all_data.extend(data) 

            # Scroll down
            driver.execute_script("window.scrollBy(0, 500)")
            await asyncio.sleep(time_scrolling)

            # Check for end of results (example logic, adjust as needed)
            end_of_results = driver.find_elements(By.XPATH, "//span[text()='No more results']")
            if end_of_results:
                break

    driver.quit()
    return all_data


def extract_email_from_webpage(url):
    """Extracts email addresses from a webpage using BeautifulSoup."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
                                              "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"})
        response.raise_for_status()  # Raise an error for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')
        tag_texts = [tag.text for tag in soup.find_all(
            string=True) if tag.parent.name != '[document]']

        result = '   '.join(tag_texts)

        # Find email-like text using a regular expression
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', result)
        return list(set(emails))
    except Exception as e:
        logging.error(f"Error extracting email from webpage '{url}': {e}")
        return []

def extract_emails_threaded():
    """Extracts emails from webpages using threading for efficiency."""
    if st.session_state.combined_df is not None:
        with st.spinner("Extracting emails from webpages..."):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(extract_email_from_webpage, url): idx for idx, url in enumerate(
                    st.session_state.combined_df['website'])}
                for future in concurrent.futures.as_completed(futures):
                    idx = list(futures.keys()).index(future)
                    emails = future.result()
                    st.session_state.combined_df.at[idx, 'emails_from_webpage'] = ', '.join(
                        emails)
            st.success("Emails extracted!")
            st.dataframe(st.session_state.combined_df)
    else:
        st.warning("No data available yet. Please scrape first.")

# ... (other helper functions: smooth_scroll_to_div_bottom, convert_df, download_csv, download_xlsx, insert_into_sheet)

def scrape_data(time_scrolling):
    """Initiates the scraping process using asynchronous tasks."""
    with st.spinner("Scraping..."):
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(main_async(query, time_scrolling)) for query in search_queries]
        all_data = loop.run_until_complete(asyncio.gather(*tasks))

        # Flatten the list of lists 
        flattened_data = [item for sublist in all_data for item in sublist] 

        if flattened_data:
            st.session_state.combined_df = pd.DataFrame(flattened_data)
            st.success("Scraping completed!")
            st.dataframe(st.session_state.combined_df)
        else:
            st.warning("No results found. Please try a different query.")



def convert_df(df):
    return df.to_csv().encode('utf-8')


def download_csv():
    if st.session_state.combined_df is not None:
        csv = convert_df(st.session_state.combined_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='scraped_data.csv',
            mime='text/csv',
        )
    else:
        st.warning("No data available yet. Please scrape first.")


def download_xlsx():
    if st.session_state.combined_df is not None:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.combined_df.to_excel(writer, sheet_name='Sheet1')
        xlsx_data = output.getvalue()
        st.download_button(
            label='Download XLSX file',
            data=xlsx_data,
            file_name='scraped_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning("No data available yet. Please scrape first.")

def insert_into_sheet(df):
    gc = gspread.service_account(filename='scrapper-421600-d12f6bae2fac.json')
    sheet = gc.open('Scrapping').sheet1

    if not sheet.row_values(1):
        # df = pd.DataFrame(data)
        sheet.append_rows([df.columns.values.tolist()] + df.values.tolist(), value_input_option='USER_ENTERED')
    else :
        sheet.append_rows(df.values.tolist())

# Streamlit UI 

st.title("Web Scraping App")

col1, col2 = st.columns(2)
with col1:
    keywords_text_area = st.text_area(
        "Enter keywords (one per line):", height=10)
with col2:
    locations_text_area = st.text_area(
        "Enter locations (one per line):", height=10)

if (keywords_text_area is not None) or (locations_text_area is not None):
    keywords_list = [line.strip()
                     for line in keywords_text_area.splitlines() if line.strip()]
    locations_list = [line.strip()
                      for line in locations_text_area.splitlines() if line.strip()]
    if locations_list == []:
        search_queries = keywords_list
        st.write(len(keywords_list))
    else:
        search_queries = [
            f"{keyword} ({location})" for keyword in keywords_list for location in locations_list]
        st.write(len(search_queries))

st.write(search_queries)
nb_threads = int(st.number_input("Insert a number of threads",
                 value=3, placeholder="Type a number..."))
time_scrolling = float(st.number_input("Insert Time of scrolling",
                                       value=5, placeholder="Type a number..."))

if st.button("Start Scraping"):
    scrape_data(time_scrolling)

if st.button("Extract Emails from Webpages"):
    extract_emails_threaded()
    
if st.button("Send Data To Sheets"):
    insert_into_sheet(st.session_state.combined_df)
    st.success("Data Sent To Sheets")
    

if st.button("Download CSV"):
    download_csv()

if st.button("Download XLSX"):
    download_xlsx()