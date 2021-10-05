import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
import itertools


def main():

    st.session_state["active_page"] = "🔎 BigQuery"

    # This is our connection to BigQuery
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["bigquery"]
        )
        _CLIENT = bigquery.Client(credentials=credentials)

    except Exception as e:
        st.error(
            """Couldn't load your credentials.  
            Did you have a look at our tutorial?"""
        )

        with st.expander("👇 Read more about the error"):
            st.write(e)

        st.stop()

    def get_project_schemas(project):
        query = f"SELECT * FROM {project}.INFORMATION_SCHEMA.SCHEMATA;"
        return _CLIENT.query(query).to_dataframe()

    def get_schema_table_sizes(project, schema):
        query = f"""SELECT table_id AS table, sum(size_bytes)/pow(10,9) as size_in_gb
        FROM {project}.{schema}.__TABLES__
        GROUP BY table_id
        """
        return _CLIENT.query(query).to_dataframe()

    @st.cache(ttl=2000, show_spinner=False)
    def load_big_query_data(project):
        table_sizes_df = pd.DataFrame()

        project_df = get_project_schemas(project)
        for schema in project_df.schema_name.unique():

            table_size_df_new = get_schema_table_sizes(project, schema)
            table_size_df_new["project"] = project
            table_size_df_new["schema"] = schema
            table_sizes_df = pd.concat([table_sizes_df, table_size_df_new])

        return table_sizes_df

    projects = [project.project_id for project in list(_CLIENT.list_projects())]
    project = st.selectbox("Choose a BigQuery project", projects)

    with st.spinner(f"Collecting data for BigQuery project `{project}`..."):
        table_sizes_df = load_big_query_data(project)

    st.write(f"Project `{project}`")

    st.write("### 🥇 Largest tables")

    st.write(
        f"Below you'll find the 10 largest tables in your BigQuery project `{project}`:"
    )
    st.table(
        table_sizes_df[["project", "schema", "table", "size_in_gb"]]
        .set_index("project")
        .sort_values(by="size_in_gb", ascending=False)
        .head(10)
    )


if __name__ == "__main__":
    main()
