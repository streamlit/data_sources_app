import streamlit as st

TUTORIAL_URL = "https://docs.streamlit.io/en/latest/tutorial/databases.html"

INTRO_IDENTIFIER = "—"

HOME_PAGE_TEXT = f""" ## Welcome to the 🔌 Data Sources app!

#### Streamlit makes it **super easy** to connect to your own data sources.  

This app is here to help you **connect your Streamlit app to your 
data sources.** In order to do so, you'll need to fill in your data 
source credentials into your Streamlit Secrets first! 

Don't worry, we got you covered!
"""

REST = """
**1. Fork this app**
- [Fork this app's repository](https://github.com/streamlit/data_sources_app/fork)
- Head over to the `/data_sources_app` directory and run `streamlit run streamlit_app.py`
- You should be ab
- 
- Find your credentials and fill them in your Streamlit secrets
      following the given template.
- Congrats, you're connected! Copy paste our starter code
      and start building your own app 🚀 

Follow these steps to discover how:

1. [Fork this app's repository](https://github.com/streamlit/data_sources_app/fork)

"""


def write(text, strike=False):
    if strike:
        text = f"<strike>{text}</strike> {get_done_div()}"
    st.write(text, unsafe_allow_html=True)


def load_keyboard_class():
    st.write(
        """<style>
    .kbdx {
    background-color: #eee;
    border-radius: 3px;
    border: 1px solid #b4b4b4;
    box-shadow: 0 1px 1px rgba(0, 0, 0, .2), 0 2px 0 0 rgba(255, 255, 255, .7) inset;
    color: #333;
    display: inline-block;
    font-size: .85em;
    font-weight: 700;
    line-height: 1;
    padding: 2px 4px;
    white-space: nowrap;
   }
   </style>""",
        unsafe_allow_html=True,
    )


def main():

    load_keyboard_class()

    st.write(HOME_PAGE_TEXT, unsafe_allow_html=True)

    st.markdown(
        "**1. Fork and deploy this app** in your own workspace in Streamlit Cloud 🎈",
    )

    with st.expander("Show instructions", expanded=False):
        st.write(
            """- [Fork the Data Sources app's repository](https://github.com/streamlit/data_sources_app/fork)
    - Visit your [Streamlit dashboard](https://share.streamlit.io/) and click on <span class='kbdx'> New App </span>
    - Fill in the form as follows:  

        - Repository: `{your_github_username}/data_sources_app`  
        - Branch: `main`  
        - Main file path: `main.py`
    - Click on <span class='kbdx'> Deploy! </span>

    Your app should now be running on share.streamlit.io 🎊  
    Close this tab, and switch to your app!
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """**2. Choose a data source!**
    
👈 Choose the data source you want to work with"""
    )
