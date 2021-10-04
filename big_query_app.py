import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
from streamlit_agraph import agraph, TripleStore, Config, Node, Edge
import itertools


def get_graph_data(table_sizes_df, max_schemas=5, max_tables=15):

    # Add schemas
    schema_subset = table_sizes_df.schema.unique()[:max_schemas]
    nodes = [Node(id=schema, size=200, color="red") for schema in schema_subset]

    # Add tables
    # TODO: Better filtering of max_tables. Should be max_tables per schema. `groupby().sample()` etc.
    tables_subset = table_sizes_df.table.unique()[:max_tables]
    nodes += [Node(id=table, size=100, color="blue") for table in tables_subset]

    # Add schema -> table
    edges = [
        Edge(source=schema, target=table)
        for schema, table in table_sizes_df[["schema", "table"]]
        .drop_duplicates()
        .values
        if schema in schema_subset and table in tables_subset
    ]

    config = Config(
        height=600,
        width=600,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        directed=True,
        collapsible=True,
        initialZoom=1.5,
    )

    return config, nodes, edges


def main():

    st.session_state["active_page"] = "🔎 BigQuery"

    # This is our connection to BigQuery
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["bigquery"]
        )
        _CLIENT = bigquery.Client(credentials=credentials)

    except Exception as e:
        st.sidebar.error(
            """Couldn't load your credentials.  
            Did you have a look at our [tutorial on connecting to BigQuery](https://docs.streamlit.io/en/latest/tutorial/bigquery.html)?
            """
        )

        with st.sidebar.expander("👇 Read more about the error"):
            st.write(e)

        return ""

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

    st.write("### ❓ Query")

    query_form = st.form(key="query_form")
    input_query_sql = query_form.text_area(
        label="Run arbitrary BigQuery query",
        key="input_sql",
        height=10,
        value="SELECT * FROM s4a-prod.streamlit_web_db.apps LIMIT 10;",
    )
    submit_query = query_form.form_submit_button()
    if submit_query:
        st.code(input_query_sql, language="sql")
        st.table(_CLIENT.query(input_query_sql).to_dataframe().iloc[:, :4])


if __name__ == "__main__":
    main()
