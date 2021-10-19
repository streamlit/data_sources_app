import inspect
import textwrap
import streamlit as st
from pathlib import Path

from big_query_app import (
    main as big_query_app,
    get_connector as get_big_query_connector,
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

TUTORIALS_ROOT = Path("./tutorials")

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
        "docs_md_file_path": TUTORIALS_ROOT / "bigquery.md",
    },
    "❄️ Snowflake": {
        "app": snowflake_app,
        "secret_key": "snowflake",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
        "app_path": "snowflake_app.py",
        "get_connector": get_snowflake_connector,
        "docs_md_file_path": TUTORIALS_ROOT / "snowflake.md",
    },
    "📝 Public Google Sheet": {
        "app": google_sheet_app,
        "secret_key": "gsheets",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
        "app_path": "google_sheet_app.py",
        "get_connector": get_google_sheet_connector,
        "docs_md_file_path": TUTORIALS_ROOT / "public-gsheet.md",
    },
}

ERROR_MESSAGE = """❌ Unfortunately, no credentials were found for data source: `{}` in your Streamlit secrets.
If you have already filled in secrets and this error still shows, make sure the secrets are under the identifier '`{}`'.  

Otherwise, follow the to-do below:"""


def has_credentials_in_secrets(data_source) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def show_error_when_not_connected(data_source: str):

    st.error(
        ERROR_MESSAGE.format(
            data_source,
            DATA_SOURCES[data_source]["secret_key"],
        )
    )

    def striken(text):
        return "".join(chr(822) + t for t in text)

    def to_do_element(text, checkbox_id):
        cols = st.columns((1, 20))
        done = cols[0].checkbox(" ", key=checkbox_id)
        if done:
            cols[1].write(f"<strike>{text}</strike>", unsafe_allow_html=True)
        else:
            cols[1].write(text, unsafe_allow_html=True)

    to_do_element(
        """**Create a BigQuery database.** For this example, we will use one of the sample datasets from BigQuery 
                (namely the shakespeare table). If you want to create a new dataset instead, 
                follow [Google's quickstart guide](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui).""",
        "database_exists",
    )

    to_do_element(
        """**Enable the BigQuery API.** Programmatic access to BigQuery is controlled through [Google 
        Cloud Platform](https://cloud.google.com/). Create an account or sign in and head over to the [APIs 
        & Services dashboard](https://console.cloud.google.com/apis/dashboard) (select or create a project 
        if asked). Search for the BigQuery API and enable it.""",
        "bigquery_enabled",
    )

    to_do_element(
        """**Create a service account & key file.** To use the BigQuery API from Streamlit Cloud, 
            you need a Google Cloud Platform service account (a special account type for programmatic 
            data access). Go to the [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
            page, choose a project and create an account with the **Viewer** permission (this will let the account access data 
            but not change it).<br><br>If the button `CREATE SERVICE ACCOUNT` is gray, you don't have the correct 
            permissions. Ask the admin of your Google Cloud project for help. <br><br> After clicking `DONE`, you 
            should be back on the service accounts overview. Click on your service account, head over to `Keys` > 
            `Add a key` > `Create a key` > `JSON`. file for the new account and download it.""",
        "service_account_created",
    )

    to_do_element(
        """**Fill in the credentials inside Streamlit using Streamlit Secrets.**""",
        "filled_in_secrets",
    )

    cols = st.columns(2)
    cols[0].code(
        """{
"type": "service_account",
"project_id": ...
"private_key_id": ...
"private_key": ...
"client_email": ...
...""",
        language="json",
    )

    cols[0].caption("Your `.json` service account should look like that.")

    cols[1].code(
        """[bigquery]
type = "service_account"
project_id = ...
private_key_id = ...
private_key = ...
client_email = ...
...""",
        language="toml",
    )

    cols[1].caption("👈 Change this into `.toml` format")

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

    def to_button(text):
        return f'<span class="kbdx">{text}</span>'

    load_keyboard_class()
    to_do_element(
        f"""**Copy paste these `.toml` credentials into your Streamlit Secrets: **  
        You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}""",
        "copy_pasted_secrets",
    )

    st.video("./secrets.mov")


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

        st.write(f"### You have chosen to connect to **{data_source}**. Let's do it!")

        # First, look for credentials in the secrets
        has_credentials = has_credentials_in_secrets(data_source)

        if has_credentials:
            st.sidebar.success("✔ Found credentials!")
        else:
            st.sidebar.error("❌ Could not find credentials in your Streamlit Secrets.")
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
