import streamlit as st
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection

from utils.ui import to_do, to_button

TOML_SERVICE_ACCOUNT = """[snowflake]
    user = ...
    password = ...
    account = ...
    warehouse = ...
"""

PASTE_INTO_SECRETS = f"""**Paste these `.toml` credentials into your Streamlit Secrets! **  
You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}"""

# @st.experimental_singleton()
# We intendedly do not cache the connector in the actual data sources app
# so that if secrets are removed, the error is shown and we don't use
# the connector from cache
def get_connector() -> SnowflakeConnection:
    """ Create a connector to SnowFlake using credentials filled in Streamlit secrets """
    connector = connect(**st.secrets["snowflake"], client_session_keep_alive=True)
    return connector


def tutorial():
    st.write(
        """First, sign up for [Snowflake](https://signup.snowflake.com/)
    and log into the Snowflake [web interface](https://docs.snowflake.com/en/user-guide/connecting.html#logging-in-using-the-web-interface) 
    (write down your username, password, and account identifier!)"""
    )

    to_do(
        [
            (st.write, """**Format your credentials into `.toml` as below:**"""),
            (st.code, TOML_SERVICE_ACCOUNT, "toml"),
        ],
        "snowflake_creds_formatted",
    )

    to_do(
        [(st.write, PASTE_INTO_SECRETS), (st.image, "imgs/arrow.png")],
        "copy_pasted_secrets",
    )


def app():
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

    # The maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

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
