import streamlit as st

TUTORIAL_URL = "https://docs.streamlit.io/en/latest/tutorial/databases.html"

INTRO_IDENTIFIER = "—"

HOME_PAGE_TEXT = f""" ## Welcome to the 🔌 Data Sources app!
        
This app is intended to show you how you can quickly connect Streamlit to your own data sources!  

Simply follow these steps:

1. Fork this app 

2. Check out our [tutorial on connecting Streamlit to data sources]({TUTORIAL_URL}) and 
fill in your Streamlit secrets with your data sources credentials.

3. Choose one data source in the panel on your left

4. Uncover what Streamlit can make out of your data!
"""


def main():
    st.write(HOME_PAGE_TEXT)
    st.sidebar.success("Select a data source above.")
    st.session_state["active_page"] = INTRO_IDENTIFIER