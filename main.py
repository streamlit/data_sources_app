import streamlit as st
from big_query_app import main as big_query_app
from snowflake_app import main as snowflake_app
from google_sheet_app import main as google_sheet_app
import time

HOME_PAGE_IDENTIFIER = "None"

DATA_SOURCES = {
    "🔎 BigQuery": {
        "app": big_query_app,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/bigquery.html",
        "docs_md_path": "tutorials/bigquery.md",
    },
    "❄️ Snowflake": {
        "app": snowflake_app,
        "secret_key": "snowflake",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
        "docs_md_path": "tutorials/snowflake.md",
    },
    "📝 Public Google Sheet": {
        "app": google_sheet_app,
        "secret_key": "gsheets",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
        "docs_md_path": "tutorials/public-gsheet.md",
    },
}

TUTORIAL_URL = "https://docs.streamlit.io/en/latest/tutorial/databases.html"

HOME_PAGE_TEXT = f""" ## Welcome to the 🔌 Data Sources app!
        
This app is intended to show you how you can quickly connect Streamlit to your own data sources!  

Simply follow these steps:

1. Fork this app 

2. Check out our [tutorial on connecting Streamlit to data sources]({TUTORIAL_URL}) and 
fill in your Streamlit secrets with your data sources credentials.

3. Choose one data source in the 🎛 Config panel on your left

4. Uncover what Streamlit can make out of your data!
"""


def has_credentials_for(data_source) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def home():
    st.write(HOME_PAGE_TEXT)
    st.session_state["active_page"] = HOME_PAGE_IDENTIFIER


def init_balloons():
    if any(data_source not in st.session_state.keys() for data_source in DATA_SOURCES):
        for data_source in DATA_SOURCES.keys():
            st.session_state[data_source] = dict(had_balloons=False)


def _dev_load_secrets():
    import toml

    with open(".streamlit/secrets.toml", encoding="utf-8") as f:
        secrets_file_str = f.read()
    secrets = toml.loads(secrets_file_str)
    return secrets


if __name__ == "__main__":

    # ---- DEV ----
    secrets = st.sidebar.selectbox("(Dev) Secrets are...", ["Full", "Empty"])
    if secrets == "Full":
        st.secrets = _dev_load_secrets()
        init_balloons()
    else:
        st.secrets = dict()

    # -------------

    st.sidebar.title("🔌  Data Sources app")
    st.sidebar.write("## 🎛 Config")

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        [HOME_PAGE_IDENTIFIER] + list(DATA_SOURCES.keys()),
        index=0,
    )

    st.session_state["active_page"] = data_source
    init_balloons()

    if data_source == HOME_PAGE_IDENTIFIER:
        home()

    else:

        st.title(f"{data_source} dashboard")

        with st.spinner("Looking for credentials..."):
            time.sleep(0.5)
            has_credentials = has_credentials_for(data_source)

        if has_credentials:
            st.sidebar.success("✔ Connected.")
            DATA_SOURCES[st.session_state["active_page"]]["app"]()

            # Upon first success for a data source, release balloons!
            if not st.session_state.get(data_source, {}).get("had_balloons", True):
                st.balloons()
                st.session_state[data_source]["had_balloons"] = True

        else:
            st.sidebar.error("Not connected.")

            st.error(
                f"""Unfortunately, no credentials were found for data source: `{data_source}` in your Streamlit secrets.  
            You can have a look at our [documentation]({DATA_SOURCES[data_source]["docs_url"]}) 
            to read more about how to connect to databases.  
            We also optionally display it just below:"""
            )

            # Show docs in an iframe
            with st.expander("Open the documentation ⬇️"):
                st.components.v1.iframe(
                    DATA_SOURCES[data_source]["docs_url"], height=600, scrolling=True
                )
