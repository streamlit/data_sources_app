import streamlit as st
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection


@st.experimental_singleton()
def get_connector() -> SnowflakeConnection:
    """ Create a connector to SnowFlake using credentials filled in Streamlit secrets """
    connector = connect(**st.secrets["snowflake"], client_session_keep_alive=True)
    return connector


def main():
    import streamlit as st
    import pandas as pd
    from snowflake.connector import connect
    from snowflake.connector.connection import SnowflakeConnection

    # Share the connector across all users connected to the app
    @st.experimental_singleton()
    def get_connector() -> SnowflakeConnection:
        """ Create a connector using credentials filled in Streamlit secrets """
        connector = connect(**st.secrets["snowflake"], client_session_keep_alive=True)
        return connector

    TTL = 60 * 60 * 60

    # Using `experimental_memo()` to memoize function executions
    @st.experimental_memo(ttl=TTL)
    def get_databases(_connector) -> pd.DataFrame:
        """ Get all databases available in Snowflake """
        return pd.read_sql("SHOW DATABASES;", _connector)

    @st.experimental_memo(ttl=TTL)
    def get_data(_connector, database) -> pd.DataFrame:
        """ Get tables available in this database """
        query = f"SELECT * FROM {database}.INFORMATION_SCHEMA.TABLES;"
        return pd.read_sql(query, _connector)

    st.markdown(f"## ❄️ Connecting to Snowflake")

    snowflake_connector = get_connector()

    databases = get_databases(snowflake_connector)
    database = st.selectbox("Choose a Snowflake database", databases.name)

    data = get_data(snowflake_connector, database)
    st.write(f"👇 Find below the available tables in database `{database}`")
    st.dataframe(data)


if __name__ == "__main__":
    main()
