import streamlit as st
from gsheetsdb import connect, OperationalError
import pandas_profiling

from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import numpy as np

TTL = 60 * 60 * 60


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton()
def connect_to_gsheetsdb():
    return connect()


def init_gsheetsdb_connection():
    """ Try connecting to gsheetsdb. Print exception should something wrong happen. """

    try:
        return connect_to_gsheetsdb()

    except Exception as e:

        st.error(
            """Couldn't load your credentials. Did you have a look at our tutorial? """
        )

        with st.expander("👇 Read more about the error"):
            st.write(e)

        st.stop()


@st.experimental_memo(ttl=TTL)
def query_to_dataframe(_connector, query: str) -> pd.DataFrame:
    rows = _connector.execute(query, headers=1)
    dataframe = pd.DataFrame(list(rows))
    return dataframe


@st.experimental_memo(ttl=600)
def get_data_gsheetsdb(_connector, gsheets_url="") -> pd.DataFrame:
    return query_to_dataframe(_connector, f'SELECT * FROM "{gsheets_url}"')


def main():

    st.session_state["active_page"] = "📝 Google Sheet"

    gsheet_connector = init_gsheetsdb_connection()
    gsheets_url = st.secrets["gsheets"]["public_gsheets_url"]
    data = get_data_gsheetsdb(gsheet_connector, gsheets_url)

    if data.empty:
        st.write("The sheet seems empty... try another one!")
        return

    # --------------------------------------------

    st.write("### 🤹‍♀️ A quick look")

    st.write(
        "Here's a sample of the data in the input Google Sheet you provided in the secrets:"
    )
    st.table(data.head())


if __name__ == "__main__":
    main()
