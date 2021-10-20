import streamlit as st
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from ui import to_do, to_button

TUTORIAL_1 = """**Enable the BigQuery API.**  
Programmatic access to BigQuery is controlled through [Google 
Cloud Platform](https://cloud.google.com/). Create an account or sign in and head over to the [APIs 
& Services dashboard](https://console.cloud.google.com/apis/dashboard). If it's not already listed,
search for the [BigQuery API](https://console.cloud.google.com/marketplace/product/google/bigquery.googleapis.com)
and enable it."""

TUTORIAL_2 = """**Create a service account & key file.**  
To use the BigQuery API from Streamlit Cloud, 
you need a Google Cloud Platform service account (a special account type for programmatic 
data access). Go to the [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
page, choose a project and click <span class="kbdx"> + CREATE SERVICE ACCOUNT </span>.  
You can restrict  to the **Viewer** permission (this will let the account access data 
but not change it).<br><br>If that button is gray and unavailable, you don't have the correct 
permissions. Ask the admin of your Google Cloud project for help. <br><br> After clicking  <span class="kbdx">DONE</span>
, you should be back on the service accounts overview. Click on your service account, head over to 
<span class="kbdx"> Keys </span> > <span class="kbdx"> Add a key </span> > <span class="kbdx"> Create a key </span> > <span class="kbdx"> JSON </span> 
to create and download your service account file."""

TUTORIAL_3 = """**Transform your `.json` credentials into `.toml` format.**  
Streamlit Secrets expect credentials to be given in the following format:"""

TUTORIAL_4 = f"""**Paste these `.toml` credentials into your Streamlit Secrets! **  
You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}"""

JSON_SERVICE_ACCOUNT = """{
    "type": "service_account",
    "project_id": ...
    "private_key_id": ...
    "private_key": ...
    "client_email": ...
    ..."""

TOML_SERVICE_ACCOUNT = """[bigquery]
    type = "service_account"
    project_id = ...
    private_key_id = ...
    private_key = ...
    client_email = ...
    ..."""


@st.experimental_singleton()
def get_connector():
    """ Create a connector to BigQuery using credentials filled in Streamlit secrets """
    credentials = Credentials.from_service_account_info(st.secrets["bigquery"])
    connector = bigquery.Client(credentials=credentials)
    return connector


def tutorial():
    st.write(
        """We assume that you have a BigQuery account already, and a database. If not, please
    follow [Google's quickstart guide](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui).
    """
    )

    to_do(
        [
            (st.write, TUTORIAL_1),
            (st.image, "tutorials/images/big-query-3.png", None, 300),
            (st.image, "tutorials/images/big-query-3.png"),
        ],
        "bigquery_enabled",
    )

    to_do(
        [(st.write, TUTORIAL_2)],
        "service_account_created",
    )

    to_do(
        [
            (st.write, TUTORIAL_3),
            (st.code, TOML_SERVICE_ACCOUNT, "toml"),
        ],
        "filled_in_secrets",
    )

    to_do(
        [(st.write, TUTORIAL_4)],
        "copy_pasted_secrets",
    )

    st.image("arrow.png")


def main():
    import pandas as pd
    import streamlit as st
    from google.cloud import bigquery
    from google.oauth2.service_account import Credentials

    # Share the connector across all users connected to the app
    @st.experimental_singleton()
    def get_connector():
        """ Create a connector using credentials filled in Streamlit secrets """
        credentials = Credentials.from_service_account_info(st.secrets["bigquery"])
        connector = bigquery.Client(credentials=credentials)
        return connector

    # The maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    # Using `experimental_memo()` to memoize function executions
    @st.experimental_memo(ttl=TTL)
    def get_projects(_connector) -> list:
        """ Get the list of projects available """
        return [project.project_id for project in list(_connector.list_projects())]

    @st.experimental_memo(ttl=TTL)
    def get_data(_connector, project: str) -> pd.DataFrame:
        """ Get schema data for a given project """
        query = f"SELECT * FROM {project}.INFORMATION_SCHEMA.SCHEMATA;"
        return _connector.query(query).to_dataframe()

    st.markdown(f"## 🔎 Connecting to Big Query")

    big_query_connector = get_connector()

    projects = get_projects(big_query_connector)
    project = st.selectbox("Choose a BigQuery project", projects)

    data = get_data(big_query_connector, project)
    st.write(f"👇 Find below the available schemas in project `{project}`!")
    st.dataframe(data)


if __name__ == "__main__":
    main()
