import streamlit as st
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import json, toml
from io import StringIO

from utils.ui import to_do, to_button, image_from_url

TUTORIAL_1 = """**Enable the BigQuery API.**  

Programmatic access to BigQuery is controlled through [Google 
Cloud Platform](https://cloud.google.com/). Create an account or sign in and head over to the [APIs 
& Services dashboard](https://console.cloud.google.com/apis/dashboard). If it's not already listed,
search for the [BigQuery API](https://console.cloud.google.com/marketplace/product/google/bigquery.googleapis.com)
and enable it."""

TUTORIAL_2_1 = """**Create a service account & key file.**  

To use the BigQuery API from Streamlit Cloud, 
you need a Google Cloud Platform service account (a special account type for programmatic 
data access). Go to the [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
page, choose a project and click <span class="kbdx"> + CREATE SERVICE ACCOUNT </span>."""

TUTORIAL_2_2 = """If that button is gray and unavailable, you don't have the correct 
permissions. Ask the admin of your Google Cloud project for help."""

TUTORIAL_2_3 = """After clicking on <span class="kbdx">DONE</span>
, you should be back on the service accounts overview. Click on your service account, head over to 
<span class="kbdx"> Keys </span> > <span class="kbdx"> Add a key </span> > <span class="kbdx"> Create a key </span> > <span class="kbdx"> JSON </span> 
to create and download your service account file."""

TUTORIAL_3 = """**Convert your JSON service account to TOML.**"""

PASTE_INTO_SECRETS = f"""**Paste these TOML credentials into your Streamlit Secrets! **  

To open your settings, click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} and then update {to_button("Sharing")} and {to_button("Secrets")}"""


@st.experimental_singleton()
def get_connector():
    """Create a connector to BigQuery using credentials filled in Streamlit secrets"""
    credentials = Credentials.from_service_account_info(st.secrets["bigquery"])
    connector = bigquery.Client(credentials=credentials)
    return connector


def tutorial():
    st.write(
        """We assume that you have a BigQuery account already, and a database.  
        If not, please follow [Google's quickstart guide](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui).
    """
    )

    to_do(
        [
            (st.write, TUTORIAL_1),
            (
                st.image,
                image_from_url(
                    "https://user-images.githubusercontent.com/7164864/143440812-fbff40a0-2c15-4ade-af74-48b4bdaa5700.png"
                ),
            ),
        ],
        "bigquery_enabled",
    )

    to_do(
        [
            (st.write, TUTORIAL_2_1),
            (
                st.image,
                image_from_url(
                    "https://user-images.githubusercontent.com/7164864/143441050-51754071-0463-4c0b-a733-78c6e9d73572.png"
                ),
            ),
            (st.caption, TUTORIAL_2_2),
            (st.write, TUTORIAL_2_3),
            (
                st.image,
                image_from_url(
                    "https://user-images.githubusercontent.com/7164864/143441099-8edeb680-c5c7-452f-aae9-30de5f8b700d.png"
                ),
            ),
        ],
        "service_account_created",
    )

    def json_to_toml():

        widget_choice = st.selectbox(
            "Choose how to insert your service account",
            ["Upload JSON file", "Paste raw JSON content"],
            index=0,
        )

        service_account_str = None

        if widget_choice == "Upload JSON file":
            service_account_file = st.file_uploader(
                "Upload your JSON service account",
                accept_multiple_files=False,
                type="json",
            )

            if service_account_file is not None:
                service_account_str = StringIO(
                    service_account_file.getvalue().decode("utf-8")
                ).read()

        elif widget_choice == "Paste raw JSON content":
            service_account_str = st.text_area("Paste your JSON service account below")

        convert = st.button("Convert to TOML")

        if service_account_str or convert:
            try:
                input_json = json.loads(service_account_str)
                input_json = {"bigquery": input_json}
                toml_output = toml.dumps(input_json)
                st.write("""TOML output:""")
                st.caption(
                    "(You can copy this TOML by hovering on the code box: a copy button will appear on the right)"
                )
                st.code(toml_output, "toml")
            except Exception as e:
                st.error(
                    "There has been a problem converting your JSON input to TOML. Please check that your JSON input is valid. More information below 👇"
                )
                st.exception(e)

    to_do(
        [
            (st.write, TUTORIAL_3),
            (json_to_toml,),
        ],
        "filled_in_secrets",
    )

    to_do(
        [
            (st.write, PASTE_INTO_SECRETS),
            (
                st.image,
                image_from_url(
                    "https://user-images.githubusercontent.com/7164864/143465207-fa7ddc5f-a396-4291-a08b-7d2ecc9512d2.png"
                ),
            ),
        ],
        "copy_pasted_secrets",
    )


def app():
    import pandas as pd
    import streamlit as st
    from google.cloud import bigquery
    from google.oauth2.service_account import Credentials

    # Share the connector across all users connected to the app
    @st.experimental_singleton()
    def get_connector():
        """Create a connector using credentials filled in Streamlit secrets"""
        credentials = Credentials.from_service_account_info(st.secrets["bigquery"])
        connector = bigquery.Client(credentials=credentials)
        return connector

    # Time to live: the maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    # Using `experimental_memo()` to memoize function executions
    @st.experimental_memo(ttl=TTL)
    def get_projects(_connector) -> list:
        """Get the list of projects available"""
        return [project.project_id for project in list(_connector.list_projects())]

    @st.experimental_memo(ttl=TTL)
    def get_data(_connector, project: str) -> pd.DataFrame:
        """Get schema data for a given project"""
        query = f"SELECT * FROM {project}.INFORMATION_SCHEMA.SCHEMATA;"
        return _connector.query(query).to_dataframe()

    st.markdown(f"## 🔎 BigQuery app")

    big_query_connector = get_connector()

    projects = get_projects(big_query_connector)
    project = st.selectbox("Choose a BigQuery project", projects)

    data = get_data(big_query_connector, project)
    st.write(f"👇 Find below the available schemas in project `{project}`!")
    st.dataframe(data)
