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

SIGN_UP_SNOWFLAKE = """**If you haven't already, [sign up for Snowflake](https://signup.snowflake.com/)**"""

SIGN_IN_URL = "https://docs.snowflake.com/en/user-guide/connecting.html#logging-in-using-the-web-interface"
SIGN_IN_SNOWFLAKE = f"""**Sign in to the [Snowflake web interface]({SIGN_IN_URL})**  

Don't forget to write down your username, password, account and warehouse identifiers, we need them right after!"""

PASTE_INTO_SECRETS = f"""**Paste the TOML credentials generated above into your Streamlit Secrets! **  

If the Cloud console is not yet opened, click on {to_button("Manage app")} in the bottom right part of this window.  
Once it is opened, then click on {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")} and paste your TOML service account there. Don't forget to {to_button("Save")}!"""


# @st.experimental_singleton()
# We intendedly do not cache the connector in the actual data sources app
# so that if secrets are removed, the error is shown and we don't use
# the connector from cache
def get_connector() -> SnowflakeConnection:
    """Create a connector to SnowFlake using credentials filled in Streamlit secrets"""
    connector = connect(**st.secrets["snowflake"], client_session_keep_alive=True)
    return connector


def tutorial():

    to_do([(st.write, SIGN_UP_SNOWFLAKE)], "sign_up_snowflake")
    to_do([(st.write, SIGN_IN_SNOWFLAKE)], "sign_in_snowflake")

    def generate_credentials():
        import toml

        creds = st.form(key="creds")
        user = creds.text_input("User")
        password = creds.text_input("Password", type="password")
        account = creds.text_input("Account")
        warehouse = creds.text_input("Warehouse")
        button = creds.form_submit_button("Create TOML credentials")

        if button:
            toml_credentials = toml.dumps(
                {
                    "snowflake": {
                        "user": user,
                        "password": password,
                        "account": account,
                        "warehouse": warehouse,
                    }
                }
            )
            st.write("""TOML output:""")
            st.caption(
                "(You can copy this TOML by hovering on the code box: a copy button will appear on the right)"
            )
            st.code(toml_credentials, "toml")

    to_do(
        [
            (
                st.write,
                """**Fill in your Snowflake credentials and transform them to TOML:**""",
            ),
            (generate_credentials,),
        ],
        "snowflake_creds_formatted",
    )

    to_do(
        [
            (st.write, PASTE_INTO_SECRETS),
            (st.image, "imgs/fill_secrets.png"),
        ],
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
        """Create a connector using credentials filled in Streamlit secrets"""
        connector = connect(**st.secrets["snowflake"], client_session_keep_alive=True)
        return connector

    # Time to live: the maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    # Using `experimental_memo()` to memoize function executions
    @st.experimental_memo(ttl=TTL)
    def get_databases(_connector) -> pd.DataFrame:
        """Get all databases available in Snowflake"""
        return pd.read_sql("SHOW DATABASES;", _connector)

    @st.experimental_memo(ttl=TTL)
    def get_data(_connector, database) -> pd.DataFrame:
        """Get tables available in this database"""
        query = f"SELECT * FROM {database}.INFORMATION_SCHEMA.TABLES;"
        return pd.read_sql(query, _connector)

    st.markdown(f"## ❄️ Connecting to Snowflake")

    snowflake_connector = get_connector()

    databases = get_databases(snowflake_connector)
    database = st.selectbox("Choose a Snowflake database", databases.name)

    data = get_data(snowflake_connector, database)
    st.write(f"👇 Find below the available tables in database `{database}`")
    st.dataframe(data)
