import streamlit as st
from gsheetsdb import connect
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

    # --------------------------------------------

    st.write("### ❓ Query")

    query_form = st.form(key="query_form")

    sample_query = "SELECT * FROM my_gsheet LIMIT 10"

    input_query_sql = query_form.text_area(
        label="Run an arbitrary query on your data in Google Sheets as if it was an SQL table called my_gsheet!",
        key="input_sql",
        height=10,
        value=sample_query,
    )

    submit_query = query_form.form_submit_button("Run query")

    if submit_query:

        # Replace `my_gsheet` by actual secret sheet URL
        if not "my_gsheet" in input_query_sql:
            return st.write("Don't remove 'my_gsheet'! Try again :-)")

        final_query_sql = input_query_sql.replace("my_gsheet", f'"{gsheets_url}"')
        result_dataframe = query_to_dataframe(gsheet_connector, final_query_sql)
        if not result_dataframe.empty:
            st.write("Result: (first 5 rows, first 5 columns)")
            st.table(result_dataframe.head(5).iloc[:, :5])


if __name__ == "__main__":
    main()
