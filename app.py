import concurrent.futures
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
import io
import logging
import requests
import re
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.common.exceptions import WebDriverException
from threading import Lock


# failed_queries_lock = Lock()
if 'failed_queries' not in st.session_state:
    st.session_state.failed_queries = []
# #######################################
import aiohttp
import asyncio




async def extract_email_task(session, url):
    
    async def extract_email_from_webpage(session, url):
        """Extracts email addresses from a webpage using BeautifulSoup."""
        try:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
                                                "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}) as response:
                response.raise_for_status()  # Raise an error for bad status codes

                soup = BeautifulSoup(await response.text(), 'html.parser')
                tag_texts = [tag.text for tag in soup.find_all(
                    string=True) if tag.parent.name != '[document]']

                result = '   '.join(tag_texts)

                # Find email-like text using a regular expression
                emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', result)
                return ';'.join(list(set(emails)))
        except Exception as e:
            logging.error(f"Error extracting email from webpage '{url}': {e}")
            # return []
            return None

    return await extract_email_from_webpage(session, url)

async def extract_emails_async():
    if st.session_state.combined_df is not None:
        with st.spinner("Extracting emails from webpages..."):
            async with aiohttp.ClientSession() as session:
                tasks = [extract_email_task(session, url) for url in st.session_state.combined_df['website']]
                email_lists = await asyncio.gather(*tasks)
            st.session_state.combined_df['emails_from_webpage'] = email_lists
            st.success("Emails extracted!")
            st.dataframe(st.session_state.combined_df)
    else:
        st.warning("No data available yet. Please scrape first.")



#########################################

def get_enterprise_info(soup, soup_head):
    """
    Extracts enterprise information from a Google Maps enterprise card URL with error handling.

    Args:
        soup: The BeautifulSoup object for the enterprise card HTML.
        soup_head: The BeautifulSoup object for the enterprise card HTML head.

    Returns:
        A dictionary containing the enterprise's name, category, website, phone numbers, and address.
        Missing elements will have a value of None.
    """
    # Extract name
    name = None
    try:
        name = soup.find('h1', class_='DUwDvf').text.strip()
    except AttributeError:
        try:
            name = soup.find('meta', itemprop='name')['content']
        except (AttributeError, TypeError):
            name = None

    # Extract category
    category = None
    try:
        category_element = soup.find(
            'button', jsaction='pane.wfvdle11.category')
        if category_element:
            category = category_element.text.strip()
        else:
            category = soup_head.find('meta', itemprop='description')[
                'content'].split('·')[1].strip()

    except:
        category = None

    # Extract website
    website = None
    try:
        website_element = soup.find('a', attrs={'data-item-id': 'authority'})
        if website_element:
            website = website_element['href']
        else:
            # Try finding links in action buttons
            action_buttons = soup.find_all('a', class_='CsEnBe')
            for button in action_buttons:
                if 'website' in button.text.lower():
                    website = button['href']

    except AttributeError:
        website = None

    # Extract phone numbers
    phone_numbers = []
    try:
        phone_elements = soup.find_all('button', attrs={'data-item-id': True})
        for element in phone_elements:
            # Check if the data-item-id contains "phone:"
            if 'phone:' in element['data-item-id']:
                phone_text = element.text.strip()
                # Extract only numbers and "+"
                phone_number = re.sub(r'[^\d+]', '', phone_text)
                phone_numbers.append(phone_number)
    except AttributeError:
        pass  # Leave phone_numbers empty if no elements found

    # Extract address
    address = None
    try:
        address_element = soup.find(
            'button', attrs={'data-item-id': 'address'})
        if address_element:
            address = address_element.find('div', class_='Io6YTe').text.strip()
        else:
            address = soup.find('meta', itemprop='name')[
                'content'].split('·')[1].strip()
    except:
        address = None

    def are_all_elements_null(d):
        return all(value is None for value in d.values())

    d = {
        'name': name,
        'category': category,
        'website': website,
        'phone_numbers': phone_numbers,
        'address': address
    }

    if are_all_elements_null(d):
        return None
    else:
        return d


def scrap_urls(driver):
    def smooth_scroll_to_div_bottom_element(container_el, Time_scrooling):
        driver.implicitly_wait(20)

        initial_height = driver.execute_script(
            "return arguments[0].scrollHeight", container_el)
        attempts_without_growth = 0

        while attempts_without_growth < 3:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", container_el)
            time.sleep(Time_scrooling)
            new_height = driver.execute_script(
                "return arguments[0].scrollHeight", container_el)

            if new_height == initial_height:
                attempts_without_growth += 1
            else:
                attempts_without_growth = 0

            initial_height = new_height

    # Navigate to the URL
    driver.get("https://www.google.com/maps/search/Hotel+In+London,+UK/")

    # Wait for all content to be loaded
    try:
        div = WebDriverWait(driver, 9).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )

        smooth_scroll_to_div_bottom_element(div, 3)
        # Get the HTML content
        html = div.get_attribute("innerHTML")
        # html = driver.page_source
        driver.close()
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style tags
        els = soup.find_all(class_='hfpxzc')

        urls = []
        for element in els:
            # print(element['href'])
            urls.append(element['href'])
            # print('################')
        if urls != []:
            return urls
        else:
            return None

    except:
        print("Timeout: Failed to load page")
        # driver.quit()
        try:
            driver.title  # or any other WebDriver operation
            # print("WebDriver is still open.")
        except WebDriverException:
            # print("WebDriver is closed.")
            driver.close()


def scrapper(url):
    options = webdriver.ChromeOptions()
    # options = webdriver.FirefoxOptions()
    # options = webdriver.EdgeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    try:
        element = WebDriverWait(driver, 14).until(
            EC.presence_of_element_located((By.CLASS_NAME, "XltNde"))
        )
        html = element.get_attribute("innerHTML")
        soup_head = BeautifulSoup(
            driver.find_element(By.CSS_SELECTOR, 'head').get_attribute("innerHTML"), "html.parser")
        # html = driver.page_source
        # driver.quit()
    except:
        print("Timeout: Failed to load page")
        # driver.close()
        # exit()
    finally:
        driver.close()

    soup = BeautifulSoup(html, "html.parser")

    res = get_enterprise_info(soup, soup_head)
    if res is not None:
        return res
    else:
        return None


# ###########################################

# st.session_state['not_query'] = []


def process_element(element, search_query):
    """Extracts data from a single element using BeautifulSoup."""
    data = {}
    try:
        data['name'] = element.find(
            class_='qBF1Pd fontHeadlineSmall').text
    except:
        data['name'] = None
    try:
        data['phone_number'] = str(element.find(
            class_='UsdlK').text).replace('+', '')
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
    if st.session_state.combined_df is not None:
        with st.spinner("Extracting emails from webpages..."):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(extract_email_from_webpage, url)
                           for url in st.session_state.combined_df['website']]
                email_lists = [future.result()
                               for future in concurrent.futures.as_completed(futures)]
            st.session_state.combined_df['emails_from_webpage'] = email_lists
            st.success("Emails extracted!")
            st.dataframe(st.session_state.combined_df)
    else:
        st.warning("No data available yet. Please scrape first.")


def main(search_query, Time_scrooling):
# def main(search_query, Time_scrooling, headless_mode : str):
    options = webdriver.ChromeOptions()
    # options = webdriver.FirefoxOptions()
    # options = webdriver.EdgeOptions()
    # if headless_mode == str('Yes'):
    #     options.add_argument('--headless')
        
    # options.add_argument('--headless')

    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Firefox(options=options)
    # driver = webdriver.Edge(options=options)
    driver.get(f'https://www.google.com/maps/search/{search_query}')
    driver.implicitly_wait(20)

    def smooth_scroll_to_div_bottom_element(container_el, Time_scrooling):
        driver.implicitly_wait(20)

        initial_height = driver.execute_script(
            "return arguments[0].scrollHeight", container_el)
        attempts_without_growth = 0

        while attempts_without_growth < 3:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", container_el)
            time.sleep(Time_scrooling)
            new_height = driver.execute_script(
                "return arguments[0].scrollHeight", container_el)

            if new_height == initial_height:
                attempts_without_growth += 1
            else:
                attempts_without_growth = 0

            initial_height = new_height

    el = None
    try:
        # Set a shorter timeout for the explicit wait
        timeout = 2  # seconds
        # Use WebDriverWait with expected_conditions to wait for the element to be present
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".Nv2PK.Q2HXcd.THOPZb, .Nv2PK.tH5CWc.THOPZb"))
        )
        print('Element found (Nv2PK Q2HXcd THOPZb or Nv2PK tH5CWc THOPZb)')
    except Exception as e:
        print(f'Error: {e}')
        driver.close()
        return str(search_query)

#     try:
#         el = driver.find_element(By.CLASS_NAME, "Nv2PK.Q2HXcd.THOPZb, Nv2PK.tH5CWc.THOPZb")
#         print('el find (Nv2PK tH5CWc THOPZb )')
#     except:
#         # with failed_queries_lock:
#         #     st.session_state.failed_queries.append(search_query)
#         driver.close()
#         return None  # Return None if the element is not found
#         # st.error("The element (Nv2PK tH5CWc THOPZb) not found")
#         el = None

    # element = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.JrN27d.SuV3fd.Zjt37e.TGiyyc > div.Ntshyc > div.L1xEbb > h1')
    # element.click()

    if el is not None:
        try:
            results_feed = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
        except Exception:
            # Fallback: try older container class
            results_feed = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#QA0Szd div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd"))
            )

        smooth_scroll_to_div_bottom_element(results_feed, Time_scrooling)

        data = []
        try:
            page_source = driver.page_source
            # driver.quit()
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            # elements = soup.find_all(class_='Nv2PK Q2HXcd THOPZb') #Nv2PK Q2HXcd THOPZb  #Nv2PK tH5CWc THOPZb
            elements = soup.find_all(attrs={'class': ['Nv2PK', 'Q2HXcd', 'THOPZb'], 'class': [
                                     'Nv2PK', 'tH5CWc', 'THOPZb']})

            print(f'length of elements : {len(elements)}')

            if elements != []:
                # Get the page source and close the driver
                # page_source = driver.page_source
                # driver.quit()

                # # Parse the page source with BeautifulSoup
                # soup = BeautifulSoup(page_source, 'html.parser')

                # Extract data using BeautifulSoup
                data = [process_element(element, search_query)
                        for element in elements]

                if data != []:
                    # driver.close()
                    df = pd.DataFrame(data)
                    search_query_list = [search_query] * len(df)
                    df = df.assign(search_query=search_query_list)
                    df.insert(0, 'search_query', df.pop('search_query'))
                    print(len(data))
                    return df
                else:
                    # driver.close()
                    return str(search_query)
            # else:
            #     driver.close()
        except Exception as e:
            # driver.close()
            print(e)
            st.error(e)
            return str(search_query)
        finally:
            driver.close()
    else:
        return str(search_query)


# def scrape_data(Time_scrooling,nb_threads,search_queries ,headless_mode : str):
#     with st.spinner("Scraping..."):
#         # with concurrent.futures.ThreadPoolExecutor() as executor:
#         with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#             dataframes = list(executor.map(main, search_queries, [Time_scrooling] * len(search_queries), headless_mode))
#             dataframes = list(filter(lambda x: x is not None, dataframes))

#             if dataframes != []:
#                 st.session_state.combined_df = pd.concat(
#                     dataframes, ignore_index=True)
#                 st.success("Scraping completed!")
#                 st.dataframe(st.session_state.combined_df)
#             else:
#                 st.warning("No results found. Please try a different query.")

def scrape_data(Time_scrooling):
    with st.spinner("Scraping..."):
        with concurrent.futures.ThreadPoolExecutor(max_workers=nb_threads) as executor:
            futures = [executor.submit(main, query , Time_scrooling)
                       for query in search_queries]
            futures = list(filter(lambda x: x is not None, futures))
            if futures != []:
                dataframes = [future.result()
                            for future in concurrent.futures.as_completed(futures)]

                dataframes = list(filter(lambda x: x is not None, dataframes))
                st.session_state.failed_queries = [x for x in dataframes if isinstance(x, str)]
                dataframes = [obj for obj in dataframes if isinstance(obj, pd.DataFrame)]

                if dataframes != []:
                    st.session_state.combined_df = pd.concat(
                        dataframes, ignore_index=True)
                    st.success("Scraping completed!")
                    st.dataframe(st.session_state.combined_df)
                else:
                    st.warning("No results found. Please try a different query.")
            else:
                st.warning("No results found. Please try a different query. and Futures is empty")


def extract_emails():
    if st.session_state.combined_df is not None:
        with st.spinner("Extracting emails from webpages..."):
            st.session_state.combined_df['emails_from_webpage'] = st.session_state.combined_df['website'].apply(
                extract_email_from_webpage)
            st.success("Emails extracted!")
            # Update displayed DataFrame
            st.dataframe(st.session_state.combined_df)
    else:
        st.warning("No data available yet. Please scrape first.")


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
    # df = df.applymap(lambda x: x.encode('utf-8') if isinstance(x, str) else x)
    df = df.applymap(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
    try:
        gc = gspread.service_account(
            filename='scrapper-421600-b8486ed62c07.json')
        sheet = gc.open('list_enterprises').sheet1
        if not sheet.row_values(1):
            # df = pd.DataFrame(data)
            sheet.append_rows([df.columns.values.tolist()] +
                              df.values.tolist(), value_input_option='USER_ENTERED')
        else:
            sheet.append_rows(df.values.tolist())

        st.success("Data inserted successfully!")
    except Exception as e:
        st.error(e)


# Streamlit UI
st.set_page_config(
    page_title="Map Scrapper",
    # layout="wide"
)
st.title("Web Scraping App")
# st.set_page_config(

#     layout="wide",)
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
nb_threads = int(st.number_input("Insert a number of threads", placeholder="Type a number...", value=4))
Time_scrooling = float(st.number_input("Insert Time of scrolling",
                                       value=5, placeholder="Type a number..."))

headless_mode = str(st.radio(
    "Headless Mode",
    ['Yes', 'No']))


if st.button("Start Scraping"):
    scrape_data(Time_scrooling)
    # scrape_data(Time_scrooling, nb_threads ,search_queries,str(headless_mode))
 
if st.button("Extract Emails from Webpages"):
    # extract_emails()
    asyncio.run(extract_emails_async())

if st.button("Send Data To Sheets"):
    # extract_emails()
    # extract_emails_threaded()
    insert_into_sheet(st.session_state.combined_df)

if st.button('Dispaly Data'):
    st.dataframe(st.session_state.combined_df)

if st.button('Dispaly Query Not Work'):
    st.write(st.session_state.failed_queries)
    with st.expander("Failed Queries"):
        st.write(" \n\n ".join(st.session_state.failed_queries))

if st.button("Download CSV"):
    download_csv()

if st.button("Download XLSX"):
    download_xlsx()


#################################################################
# import aiohttp
# import asyncio
# import nest_asyncio
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import itertools


# async def fetch(session, url):
#   try:
#     async with session.get(url) as response:
#         return await response.text()
#   except :
#     return None
# async def extract_links(url, keywords):
#     async with aiohttp.ClientSession() as session:
#         html = await fetch(session, url)
#         try:
#           soup = BeautifulSoup(html, 'html.parser')
#           links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) if any(keyword in a['href'] for keyword in keywords)]
#           return links
#         except :
#           return []


# async def main(url):
#     # url = 'https://www.emiratesmarbleuae.com/'  # replace with your url
#     keywords = [
#     "contact-us",
#     "contact",
#     "get-in-touch",
#     "reach-out",
#     "about-us",
#     "faq",
#     "support",
#     "customer-service",
#     "careers",
# ]  # replace with your keywords
#     links = await extract_links(url, keywords)
#     # links = list(filter(lambda x: x is not None, links))
#     return list(set(links))


# nest_asyncio.apply()
# tasks = [main(url) for url in urls]
# results = asyncio.run(asyncio.gather(*tasks))
#################################################################