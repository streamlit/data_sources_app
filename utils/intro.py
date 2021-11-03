import streamlit as st

TUTORIAL_URL = "https://docs.streamlit.io/en/latest/tutorial/databases.html"

INTRO_IDENTIFIER = "—"

HOME_PAGE_TEXT = f""" ## Welcome to the 🔌 Data Sources app!

Congratulations, you have successfully forked and deployed this app 🎊  

We'll now help you:
- Collect your credentials and safely add them to your 🔑 Streamlit Secrets
- Get started with your own app by providing you with sufficient code 🚀 

**Ready?**

👈 Choose the data source you want to access
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


def app():

    load_keyboard_class()

    st.write(HOME_PAGE_TEXT, unsafe_allow_html=True)