import concurrent.futures
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st

# ... (Scraping Functions: process_element and smooth_scroll_to_bottom remain the same) ...

def process_element(element , search_query ):
    """Extracts data from a single element."""
    data = {}
    # data['search_query'] = str(search_query)
    try:
        # data['search_query'] = str(search_query)
        data['name'] = element.find_element(By.CLASS_NAME, 'qBF1Pd.fontHeadlineSmall').text
    except:
        # data['search_query'] = str(search_query)
        data['name'] = None
    try:
        data['phone_number'] = element.find_element(By.CLASS_NAME, 'UsdlK').text
    except:
        data['phone_number'] = None
    try:
        data['category'] = element.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(1) > span').text
    except:
        data['category'] = None
    try:
        data['address'] = element.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(2) > span:nth-child(2)').text
    except:
        data['address'] = None
    try:
        data['website'] = element.find_element(By.CLASS_NAME, 'lcr4fd.S9kvJb').get_attribute('href')
    except:
        data['website'] = None
    return data

def main(nb , search_query):
    driver = webdriver.Chrome()
    driver.get(f'https://www.google.com/maps/search/{search_query}')
    driver.implicitly_wait(10)

    element = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.JrN27d.SuV3fd.Zjt37e.TGiyyc > div.Ntshyc > div.L1xEbb > h1')
    element.click()

    def smooth_scroll_to_bottom():
        initial_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        n = 0
        while True:
            driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd').send_keys(Keys.END)
            time.sleep(2)  # Adjust this sleep duration if needed
            n += 1
            if n == nb:
                break
    smooth_scroll_to_bottom()

    data = []
    try:
        elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'Nv2PK.tH5CWc.THOPZb'))
        )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(process_element, elements , search_query)
            data.extend(results)

    except Exception as e:
        print(e)

    df = pd.DataFrame(data)
    # df.to_excel('data.xlsx', index=False)
    driver.close()
    return df


# Streamlit UI
st.title("Web Scraping App")

# search_query = st.text_input("Enter search query (e.g., natural stone in New York):")

col1, col2 = st.columns(2)
# Create two text area widgets
with col1:
    keywords_text_area = st.text_area("Enter keywords (one per line):", height=10)
    
with col2:
    locations_text_area = st.text_area("Enter locations (one per line):", height=10)


if (keywords_text_area is not None) or (locations_text_area is not None):
    keywords_list = [line.strip() for line in keywords_text_area.splitlines() if line.strip()]
    locations_list = [line.strip() for line in locations_text_area.splitlines() if line.strip()]
    # search_queries = [f"{keyword} ({location})" for keyword in keywords_list for location in locations_list]
    
    if locations_list == []:
        search_queries = keywords_list
        st.write(len(keywords_list))
    else:
        search_queries = [f"{keyword} ({location})" for keyword in keywords_list for location in locations_list]
        st.write(len(search_queries))
    
if st.button("Search"):
    # Perform the search
    st.write(search_queries)


num_results = st.slider("Number of results:", 1, 100 , 10)

if st.button("Start Scraping"):
    with st.spinner("Scraping..."):
        dataframes = []
        with st.empty():
            for search_query in search_queries:
                st.info(str(search_query))
                data = None
                data = main(num_results, search_query)
                print(len(data))
                dataframes.append(data)
            combined_df = pd.concat(dataframes, ignore_index=True)
        if not combined_df.empty:
            st.success("Scraping completed!")
            st.dataframe(combined_df)
            # dataframes = pd.DataFrame
            # @st.cache
            def convert_df(df):
                return df.to_csv().encode('utf-8')

            csv = convert_df(combined_df)

            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='scraped_data.csv',
                mime='text/csv',
            )
        else:
            st.warning("No results found. Please try a different query.")