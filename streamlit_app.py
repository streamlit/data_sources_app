import inspect
import textwrap
import streamlit as st
from pathlib import Path

import data_sources
from data_sources import big_query

from utils import ui, intro

DATA_SOURCES = {
    intro.INTRO_IDENTIFIER: {
        "module": intro,
        "secret_key": None,
        "docs_url": None,
        "get_connector": None,
    },
    "🔎  BigQuery": {
        "module": data_sources.big_query,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/bigquery.html",
        "get_connector": data_sources.big_query.get_connector,
        "tutorial": data_sources.big_query.tutorial,
        "secrets_template": data_sources.big_query.TOML_SERVICE_ACCOUNT,
    },
    #
    # (Currently disregarding other data sources)
    #
    # "❄️ Snowflake": {
    #     "app": ds.snowflake_app.main,
    #     "secret_key": "snowflake",
    #     "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
    #     "get_connector": ds.snowflake_app.get_connector,
    # },
    # "📝 Public Google Sheet": {
    #     "app": google_sheet_app,
    #     "secret_key": "gsheets",
    #     "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
    #     "get_connector": ds.google_sheet_app.get_connector,
    # },
}

ERROR_MESSAGE = """❌ No credentials were found for '`{}`' in your Streamlit Secrets.  
Please follow our [tutorial](#tutorial-connecting-to-bigquery) or make sure that your secrets look like the following:
```toml
{}
```"""


def has_credentials_in_secrets(data_source: str) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def show_success(data_source: str):
    st.success(
        f"""👏 Congrats! You have successfully filled in your Streamlit Secrets for {data_source}.  
    Below, you'll find a [sample app](#big-query-app) and its associated [source code](#code).  
    So go ahead, copy paste the code and kick-off your own app! 🚀 """
    )


def show_error_when_not_connected(data_source: str):

    st.error(
        ERROR_MESSAGE.format(
            DATA_SOURCES[data_source]["secret_key"],
            DATA_SOURCES[data_source]["secrets_template"],
        )
    )

    st.write(f"### Tutorial: connecting to {data_source}")
    ui.load_keyboard_class()
    DATA_SOURCES[data_source]["tutorial"]()


def connect(data_source):
    """Try connecting to data source.
    Print exception should something wrong happen."""

    try:
        get_connector = DATA_SOURCES[data_source]["get_connector"]
        connector = get_connector()
        return connector

    except Exception as e:

        st.error(
            """There has been an error. While we have successfully found your secrets, they seem not to 
            enable connecting to the data source."""
        )

        with st.expander("👇 Read more about the error"):
            st.write(e)

        st.stop()


if __name__ == "__main__":

    st.set_page_config(layout="centered")

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        list(DATA_SOURCES.keys()),
        index=0,
    )

    st.session_state.active_page = data_source
    if "data_sources_already_connected" not in st.session_state:
        st.session_state.data_sources_already_connected = list()

    if data_source == intro.INTRO_IDENTIFIER:
        show_code = False
        show_balloons = False

    else:
        show_code = True
        show_balloons = True

        # First, look for credentials in the secrets
        has_credentials = has_credentials_in_secrets(data_source)

        if has_credentials:
            st.sidebar.success("✔ Connected!")
            show_success(data_source)
        else:
            st.sidebar.error("❌ Could not connect.")
            show_error_when_not_connected(data_source)
            st.stop()

        # Then, check if one can successfully connect using the secrets
        connect(data_source)

    # Release balloons to celebrate
    if (
        show_balloons
        and data_source not in st.session_state.data_sources_already_connected
    ):
        st.session_state.data_sources_already_connected.append(data_source)
        show_balloons = False
        st.balloons()

    # Display data source app
    data_source_app = DATA_SOURCES[st.session_state["active_page"]]["module"].app
    data_source_app()

    # Show source code
    if show_code:
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(data_source_app)
        st.code(textwrap.dedent("".join(sourcelines[1:])), "python")
