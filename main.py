import inspect
import textwrap
import streamlit as st
from pathlib import Path

from big_query_app import (
    main as big_query_app,
    get_connector as get_big_query_connector,
    tutorial as big_query_tutorial,
)

from snowflake_app import (
    main as snowflake_app,
    get_connector as get_snowflake_connector,
)

from google_sheet_app import (
    main as google_sheet_app,
    get_connector as get_google_sheet_connector,
)

from intro import main as intro, INTRO_IDENTIFIER
from ui import load_keyboard_class

DATA_SOURCES = {
    INTRO_IDENTIFIER: {
        "app": intro,
        "secret_key": None,
        "docs_url": None,
        "app_path": "intro.py",
        "get_connector": None,
        "docs_md_file_path": None,
    },
    "🔎 BigQuery": {
        "app": big_query_app,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/bigquery.html",
        "app_path": "big_query_app.py",
        "get_connector": get_big_query_connector,
        "tutorial": big_query_tutorial,
        "secrets_template": """[bigquery]
    type = "service_account"
    project_id = ...
    private_key_id = ...
    private_key = ...
    client_email = ...
    ...""",
    },
    # "❄️ Snowflake": {
    #     "app": snowflake_app,
    #     "secret_key": "snowflake",
    #     "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
    #     "app_path": "snowflake_app.py",
    #     "get_connector": get_snowflake_connector,
    # },
    # "📝 Public Google Sheet": {
    #     "app": google_sheet_app,
    #     "secret_key": "gsheets",
    #     "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
    #     "app_path": "google_sheet_app.py",
    #     "get_connector": get_google_sheet_connector,
    # },
}

ERROR_MESSAGE = """❌ No credentials were found for '`{}`' in your Streamlit Secrets.  
Please follow our [tutorial](#tutorial) or make sure that your secrets look like the following:
```toml
{}
```"""


def has_credentials_in_secrets(data_source) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def has_empty_secrets() -> bool:
    return not bool(st.secrets)


def show_error_when_not_connected(data_source: str):

    st.error(
        ERROR_MESSAGE.format(
            DATA_SOURCES[data_source]["secret_key"],
            DATA_SOURCES[data_source]["secrets_template"],
        )
    )

    st.write("### Tutorial")
    load_keyboard_class()
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

    if data_source == INTRO_IDENTIFIER:
        show_code = False
        show_balloons = False

    else:
        show_code = True
        show_balloons = True

        st.write(
            f"""<h3 style='margin-bottom:.5cm'> Connecting to {data_source}... </h3>""",
            unsafe_allow_html=True,
        )

        # First, look for credentials in the secrets
        has_credentials = has_credentials_in_secrets(data_source)

        if has_credentials:
            st.sidebar.success("✔ Connected!")
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
    data_source_app = DATA_SOURCES[st.session_state["active_page"]]["app"]
    data_source_app()

    # Show source code
    if show_code:
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(data_source_app)
        st.code(textwrap.dedent("".join(sourcelines[1:])), "python")
