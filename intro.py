import streamlit as st

TUTORIAL_URL = "https://docs.streamlit.io/en/latest/tutorial/databases.html"

INTRO_IDENTIFIER = "—"

HOME_PAGE_TEXT = f""" ## Welcome to the 🔌 Data Sources app!
        
<img src="https://i.ibb.co/LzQPsLC/illustration.png" width="500px">


#### Streamlit makes it **super easy** to connect to your own data sources.  
Follow these steps to discover how:

1. [Fork this app's repository](https://github.com/streamlit/data_sources_app/fork)

2. 👈 Choose your preferred data source in the panel on your left
- If you have already set up your secrets, the app will successfully connect 🎉 
- Otherwise, don't worry, we have you covered! 😎 We'll guide you through our docs to learn how to fill in your data source credentials into Streamlit secrets!
"""


def main():
    st.write(HOME_PAGE_TEXT, unsafe_allow_html=True)
    st.sidebar.success("Select a data source above.")
    st.session_state["active_page"] = INTRO_IDENTIFIER