import streamlit as st


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


# Split the text by line
# keywords_list = [line.strip() for line in keywords_text_area.splitlines() if line.strip()]
# locations_list = [line.strip() for line in locations_text_area.splitlines() if line.strip()]

# Combine the keywords and locations to generate search queries
# search_queries = [f"{keyword} ({location})" for keyword in keywords_list for location in locations_list]

if st.button("Search"):
    # Perform the search
    st.write(search_queries)