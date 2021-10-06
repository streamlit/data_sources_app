import streamlit as st
from google.cloud import bigquery
from google.oauth2.service_account import Credentials


@st.experimental_singleton()
def get_connector():
    """ Create a connector to BigQuery using credentials filled in Streamlit secrets """
    credentials = Credentials.from_service_account_info(st.secrets["bigquery"])
    connector = bigquery.Client(credentials=credentials)
    return connector


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
    TTL = 60 * 60 * 60

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
