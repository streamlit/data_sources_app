import streamlit as st
from gsheetsdb import connect
import pandas as pd
import numpy as np

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton()
def get_connector():
    return connect()


def main():

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


if __name__ == "__main__":
    main()
