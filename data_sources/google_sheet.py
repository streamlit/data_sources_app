import streamlit as st
from gsheetsdb import connect
import pandas as pd
import numpy as np

from utils.ui import to_do, to_button

CREATE_PUBLIC_GSHEET = f"""**Create a [new](https://sheets.new/) public Google Sheet and get
its URL**. Unless of course if you already have an existing one in mind. Simply make sure 
that you turned on link sharing by clicking on {to_button("Share")} > Anyone with the link.
"""

PASTE_INTO_SECRETS = f"""**Paste these `.toml` credentials into your Streamlit Secrets! **  
You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}"""

TOML_SERVICE_ACCOUNT = """[gsheets]
    public_gsheets_url = "..."  # <-- your public Google Sheet URL here
"""

# @st.experimental_singleton()
# We intendedly do not cache the connector in the actual data sources app
# so that if secrets are removed, the error is shown and we don't use
# the connector from cache
@st.experimental_singleton()
def get_connector():
    return connect()


def tutorial():

    to_do(
        [
            (st.write, CREATE_PUBLIC_GSHEET),
        ],
        "google_sheet_create_public_gsheet",
    )

    to_do(
        [
            (st.write, """**Format your credentials into `.toml` as below:**"""),
            (st.code, TOML_SERVICE_ACCOUNT, "toml"),
        ],
        "google_sheet_creds_formatted",
    )

    to_do(
        [(st.write, PASTE_INTO_SECRETS), (st.image, "imgs/arrow.png")],
        "copy_pasted_secrets",
    )


def app():

    # Share the connector across all users connected to the app
    @st.experimental_singleton()
    def get_connector():
        return connect()

    # The maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    # Using `experimental_memo()` to memoize function executions
    @st.experimental_memo(ttl=TTL)
    def query_to_dataframe(_connector, query: str) -> pd.DataFrame:
        rows = _connector.execute(query, headers=1)
        dataframe = pd.DataFrame(list(rows))
        return dataframe

    @st.experimental_memo(ttl=600)
    def get_data(_connector, gsheets_url) -> pd.DataFrame:
        return query_to_dataframe(_connector, f'SELECT * FROM "{gsheets_url}"')

    st.markdown(f"## 📝 Connecting to a public Google Sheet")

    gsheet_connector = get_connector()
    gsheets_url = st.secrets["gsheets"]["public_gsheets_url"]

    data = get_data(gsheet_connector, gsheets_url)
    st.write("👇 Find below the data in the Google Sheet you provided in the secrets:")
    st.dataframe(data)
