import inspect
import textwrap
import streamlit as st
from pathlib import Path

import data_sources
from data_sources import big_query, snowflake, aws_s3, aws_s3_boto, google_sheet

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
        "docs_url": "https://docs.streamlit.io/knowledge-base/tutorials/databases/bigquery",
        "get_connector": data_sources.big_query.get_connector,
        "tutorial": data_sources.big_query.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-bigquery",
        "secrets_template": data_sources.big_query.TOML_SERVICE_ACCOUNT,
    },
    "❄️ Snowflake": {
        "module": data_sources.snowflake,
        "secret_key": "snowflake",
        "docs_url": "https://docs.streamlit.io/knowledge-base/tutorials/databases/snowflake",
        "get_connector": data_sources.snowflake.get_connector,
        "tutorial": data_sources.snowflake.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-snowflake",
        "secrets_template": data_sources.snowflake.TOML_SERVICE_ACCOUNT,
    },
    "📦 AWS S3 (boto3)": {
        "module": data_sources.aws_s3_boto,
        "secret_key": "aws_s3",
        "docs_url": "https://docs.streamlit.io/knowledge-base/tutorials/databases/aws-s3",
        "get_connector": data_sources.aws_s3_boto.app.get_connector,
        "tutorial": data_sources.aws_s3_boto.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-aws-s3",
        "secrets_template": data_sources.aws_s3.TOML_SERVICE_ACCOUNT,
    },
    "📝 Google Sheet": {
        "module": data_sources.google_sheet,
        "secret_key": "gsheets",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
        "get_connector": data_sources.google_sheet.get_connector,
        "tutorial": data_sources.google_sheet.tutorial,
        "tutorial_anchor": "#tutorial-connecting-to-google-sheet",
        "secrets_template": data_sources.google_sheet.TOML_SERVICE_ACCOUNT,
    },
}

NO_CREDENTIALS_FOUND = """❌ **We couldn't find credentials for '`{}`' in your Streamlit Secrets.**   
Please follow our tutorial just below 👇"""

CREDENTIALS_FOUND_BUT_ERROR = """**❌ Credentials were found but there is an error.**  
While you have successfully filled in Streamlit secrets for the key `{}`,
we have not been able to connect to the data source. You might have forgotten some fields.  
            
Check the exception below 👇  
"""

PIPFILE_URL = "https://github.com/streamlit/data_sources_app/blob/main/Pipfile"
WHAT_NEXT = f"""## What next?

🚀 Kick-off your own app now!  

- Create a new repository
- Paste the code above into a new file `streamlit_app.py` and use it as a starter! 
- Add your dependencies in a `requirements.txt` (take inspiration from our [`Pipfile`]({PIPFILE_URL})!)

And the rest **you know already**: deploy, add credentials and you're ready to go!

🤔 Stuck? Check out our docs on [creating](https://docs.streamlit.io/library/get-started/create-an-app) 
and [deploying](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app) an app or reach out to 
support@streamlit.io!
"""

QUESTION_OR_FEEDBACK = """Questions? Comments? Please ask in the [Streamlit community](https://discuss.streamlit.io/)."""


def has_data_source_key_in_secrets(data_source: str) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def show_success(data_source: str):
    st.success(
        f"""👏 Congrats! You have successfully filled in your Streamlit secrets..  
    Below, you'll find a sample app that connects to {data_source} and its associated [source code](#code)."""
    )


def show_error_when_not_connected(data_source: str):

    st.error(
        NO_CREDENTIALS_FOUND.format(
            DATA_SOURCES[data_source]["secret_key"],
        )
    )

    st.write(f"### Tutorial: connecting to {data_source}")
    ui.load_keyboard_class()
    DATA_SOURCES[data_source]["tutorial"]()


def what_next():
    st.write(WHAT_NEXT)


def code(app):
    st.markdown("## Code")
    sourcelines, _ = inspect.getsourcelines(app)
    st.code(textwrap.dedent("".join(sourcelines[1:])), "python")


def connect(data_source):
    """Try connecting to data source.
    Print exception should something wrong happen."""

    try:
        get_connector = DATA_SOURCES[data_source]["get_connector"]
        connector = get_connector()
        return connector

    except Exception as e:

        st.sidebar.error("❌ Could not connect.")

        st.error(
            CREDENTIALS_FOUND_BUT_ERROR.format(DATA_SOURCES[data_source]["secret_key"])
        )

        st.exception(e)

        st.stop()


# If viewer clicks on page selector: Update query params to point to this page.
def change_page_url():
    """Update query params to reflect the selected page."""
    if st.session_state["page_selector"] == intro.INTRO_IDENTIFIER:
        st.experimental_set_query_params()
    else:
        st.experimental_set_query_params(data_source=st.session_state["page_selector"])


if __name__ == "__main__":

    st.set_page_config(page_title="Data Sources app", page_icon="🔌", layout="centered")

    # Infer selected page from query params.
    query_params = st.experimental_get_query_params()
    if "data_source" in query_params:
        page_url = query_params["data_source"][0]
        if page_url in DATA_SOURCES.keys():
            st.session_state["page_selector"] = page_url

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        list(DATA_SOURCES.keys()),
        index=0,
        key="page_selector",
        on_change=change_page_url,
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
        data_source_key_in_secrets = has_data_source_key_in_secrets(data_source)

        if data_source_key_in_secrets:
            connect(data_source)
            st.sidebar.success("✔ Connected!")
            show_success(data_source)
        else:
            st.sidebar.error("❌ Could not connect!")
            show_error_when_not_connected(data_source)
            st.caption(QUESTION_OR_FEEDBACK)
            st.stop()

    # Release balloons to celebrate (only upon first success)
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

    # Show source code and what next
    if show_code:
        code(data_source_app)
        what_next()

    st.caption(QUESTION_OR_FEEDBACK)
