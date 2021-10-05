import streamlit as st
import pandas as pd
import numpy as np
import snowflake.connector
from snowflake.connector.connection import SnowflakeConnection
from millify import millify

TTL = 60 * 60 * 60

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton()
def connect_to_snowflake() -> SnowflakeConnection:
    return snowflake.connector.connect(
        **st.secrets["snowflake"], client_session_keep_alive=True
    )


def init_snowflake_connection() -> SnowflakeConnection:
    """Try connecting to Snowflake.
    Print exception should something wrong happen."""

    try:
        return connect_to_snowflake()

    except Exception as e:

        st.error(
            """Couldn't load your credentials.  
            Did you have a look at our tutorial?"""
        )

        with st.expander("👇 Read more about the error"):
            st.write(e)

        st.stop()


@st.experimental_memo(ttl=TTL)
def query_to_dataframe(
    _connector: SnowflakeConnection,
    query: str,
) -> pd.DataFrame:

    with _connector.cursor() as cur:
        rows = cur.execute(query).fetchall()
        column_names = [column[0] for column in cur.description]

    dataframe = pd.DataFrame(rows)
    if not dataframe.empty:
        dataframe.columns = column_names
    return dataframe


@st.experimental_memo(ttl=TTL)
def get_all_databases(_connector: SnowflakeConnection) -> list:
    dataframe = query_to_dataframe(_connector, "SHOW DATABASES;")
    return dataframe.name.tolist()


@st.experimental_memo(ttl=TTL)
def get_tables(
    _connector: SnowflakeConnection,
    database: str,
) -> pd.DataFrame:

    dataframe = query_to_dataframe(
        _connector, f"SELECT * FROM {database}.INFORMATION_SCHEMA.TABLES;"
    )

    dataframe[["ROW_COUNT", "BYTES"]].fillna(0, inplace=True)
    dataframe["ROW_COUNT"].fillna(0, inplace=True)
    dataframe["BYTES"].fillna(0, inplace=True)
    dataframe["BYTES_PER_ROW"] = (
        dataframe["BYTES"].div(dataframe["ROW_COUNT"]).replace(np.inf, 0).fillna(0)
    )

    return dataframe


def main():

    st.session_state["active_page"] = "❄️ Snowflake"

    snowflake_connector = init_snowflake_connection()

    with st.spinner(f"Collecting databases available in Snowflake..."):
        databases = get_all_databases(snowflake_connector)

    # If the sample Snowflake database is available, use it.
    # Otherwise, use the first database in the list.
    default_db_index = (
        databases.index("SNOWFLAKE_SAMPLE_DATA")
        if "SNOWFLAKE_SAMPLE_DATA" in databases
        else 0
    )

    database = st.selectbox("Choose a DB", databases, index=default_db_index)

    tables = get_tables(snowflake_connector, database)

    # --------------------------------------------

    st.write("### 🌇 Database statistics")

    col1, col2, col3 = st.columns(3)

    n_schemas = millify(tables.TABLE_SCHEMA.nunique())
    col1.metric("Number of schemas", n_schemas)

    n_tables = millify(tables.groupby(["TABLE_SCHEMA", "TABLE_NAME"]).ngroups)
    col2.metric("Number of tables", n_tables)

    n_rows = millify(tables.ROW_COUNT.sum())
    col3.metric("Total number of rows", n_rows)

    # --------------------------------------------

    st.write("### 🤹‍♀️ A quick look")
    st.write(f"Lookup for a sample of the desired table")

    all_tables = tables.TABLE_SCHEMA.str.cat(tables.TABLE_NAME, sep=".").unique()
    input_schema_table = st.selectbox("Choose table to lookup", all_tables)
    input_schema, input_table = input_schema_table.split(".")

    sample_of_input_table = query_to_dataframe(
        snowflake_connector, f"SELECT * FROM {database}.{input_schema_table} LIMIT 5"
    )

    if sample_of_input_table.empty:
        st.warning(f"Chosen table (`{input_table}`) is empty!")
    else:
        st.table(sample_of_input_table.iloc[:, :5])

    # --------------------------------------------

    st.write("### 🏢 Largest/smallest tables")
    st.write(f"Find out notable tables in your database `{database}`:")

    col1, col2, col3 = st.columns(3)
    n = col1.number_input("Number of rows to display", 1, 10, 5)
    by = col2.selectbox("Sort by", ["BYTES", "ROW_COUNT"])
    order = col3.selectbox("Choose order", ["descending", "ascending"])
    ascending = order == "ascending"

    st.table(
        tables[["TABLE_CATALOG", "TABLE_SCHEMA", "TABLE_NAME", "BYTES", "ROW_COUNT"]]
        .set_index("TABLE_CATALOG")
        .sort_values(by=by, ascending=ascending)
        .head(n=n)
    )


if __name__ == "__main__":
    main()
