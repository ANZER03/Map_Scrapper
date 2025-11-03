import concurrent.futures
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
from selenium import webdriver

# ... (Scraping Functions: process_element and smooth_scroll_to_bottom remain the same) ...


def process_element(element, search_query):
    """Extracts data from a single element."""
    data = {}
    # data['search_query'] = str(search_query)
    try:
        # data['search_query'] = str(search_query)
        data['name'] = element.find_element(
            By.CLASS_NAME, 'qBF1Pd.fontHeadlineSmall').text
    except:
        # data['search_query'] = str(search_query)
        data['name'] = None
    try:
        data['phone_number'] = element.find_element(
            By.CLASS_NAME, 'UsdlK').text
    except:
        data['phone_number'] = None
    try:
        data['category'] = element.find_element(
            By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(1) > span').text
    except:
        data['category'] = None
    try:
        data['address'] = element.find_element(
            By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div > div > div.bfdHYd.Ppzolf.OFBs3e > div.lI9IFe > div.y7PRA > div > div > div.UaQhfb.fontBodyMedium > div:nth-child(4) > div:nth-child(1) > span:nth-child(2) > span:nth-child(2)').text
    except:
        data['address'] = None
    try:
        data['website'] = element.find_element(
            By.CLASS_NAME, 'lcr4fd.S9kvJb').get_attribute('href')
    except:
        data['website'] = None
    return data


def main(search_query):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    driver.get(f'https://www.google.com/maps/search/{search_query}')
    driver.implicitly_wait(20)

    # element = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.JrN27d.SuV3fd.Zjt37e.TGiyyc > div.Ntshyc > div.L1xEbb > h1')
    # element.click()

    def smooth_scroll_to_div_bottom(div_xpath):
        driver.implicitly_wait(20)

        # Get the initial div height
        initial_height = driver.execute_script(
            "return arguments[0].scrollHeight", driver.find_element(By.XPATH, div_xpath))

        while True:
            # Scroll to the bottom of the div
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", driver.find_element(By.XPATH, div_xpath))
            time.sleep(2)  # Adjust this sleep duration if needed
            # driver.implicitly_wait(10)
            # Get the new div height
            new_height = driver.execute_script(
                "return arguments[0].scrollHeight", driver.find_element(By.XPATH, div_xpath))

            # Check if the height remains the same (indicating that we've reached the bottom)
            if new_height == initial_height:
                break

            # Update the initial height for the next iteration
            initial_height = new_height
    smooth_scroll_to_div_bottom(
        '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')

    data = []
    try:
        elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'Nv2PK.tH5CWc.THOPZb'))
        )

        if elements != []:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(process_element, elements, search_query)
                data.extend(results)

            if data != []:
                df = pd.DataFrame(data)
                search_query_list = [search_query] * len(df)
                df = df.assign(search_query=search_query_list)
                df.insert(0, 'search_query', df.pop('search_query'))
                # df.to_excel('data.xlsx', index=False)
                driver.close()
                print(len(data))
                return df
            else:
                return []

    except Exception as e:
        print(e)
        st.error(e)
        return None

    # df = pd.DataFrame(data)
    # search_query_list = [search_query] * len(df)
    # df = df.assign(search_query=search_query_list)
    # df.insert(0, 'search_query', df.pop('search_query'))
    # # df.to_excel('data.xlsx', index=False)
    # driver.close()
    # print(len(data))
    # return df


# Streamlit UI
st.title("Web Scraping App")

# search_query = st.text_input("Enter search query (e.g., natural stone in New York):")

col1, col2 = st.columns(2)
# Create two text area widgets
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
    # search_queries = [f"{keyword} ({location})" for keyword in keywords_list for location in locations_list]

    if locations_list == []:
        search_queries = keywords_list
        st.write(len(keywords_list))
    else:
        search_queries = [
            f"{keyword} ({location})" for keyword in keywords_list for location in locations_list]
        st.write(len(search_queries))

if st.button("Search"):
    # Perform the search
    st.write(search_queries)


# num_results = st.slider("Number of results:", 1, 100 , 10)

if st.button("Start Scraping"):
    with st.spinner("Scraping..."):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(main, query)
                       for query in search_queries]
            dataframes = [future.result()
                          for future in concurrent.futures.as_completed(futures)]

        dataframes = list(filter(lambda x: x is not None, dataframes))

        if dataframes != []:
            combined_df = pd.concat(dataframes, ignore_index=True)
            # dataframes = []
            # with st.empty():
            #     for search_query in search_queries:
            #         st.info(str(search_query))
            #         data = None
            #         data = main(num_results, search_query)
            #         print(len(data))
            #         dataframes.append(data)
            #     combined_df = pd.concat(dataframes, ignore_index=True)
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
        else:
            st.warning("No results found. Please try a different query.")
