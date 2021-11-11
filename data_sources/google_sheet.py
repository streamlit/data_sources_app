import streamlit as st
from gsheetsdb import connect
import pandas as pd

from utils.ui import to_do, to_button

INIT_GSHEET = f"""**If you don't have one yet, [create a new Google Sheet](https://sheets.new/)**.  

Give it any name, and fill it with mock data."""

MAKE_IT_PUBLIC = f"""**Make sure that your Sheet is public**  

Click on {to_button("Share")} > {to_button("Share with ...")} and select {to_button("Anyone with the link can view")}."""

PASTE_INTO_SECRETS = f"""**Paste the TOML credentials into your Streamlit Secrets! **  

If the Cloud console is not yet opened, click on {to_button("Manage app")} in the bottom right part of this window.  
Once it is opened, then click on {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")} and paste your TOML service account there. Don't forget to {to_button("Save")}!"""

TOML_SERVICE_ACCOUNT = """[gsheets]
    public_gsheets_url = "https://docs.google.com/..."
"""

# @st.experimental_singleton()
# We intendedly do not cache the connector in the actual data sources app
# so that if secrets are removed, the error is shown and we don't use
# the connector from cache
@st.experimental_singleton()
def get_connector():
    connector = connect()

    assert st.secrets["gsheets"]["public_gsheets_url"].startswith(
        "https://docs.google.com/"
    ), "Invalid URL, must start with https://docs.google.com"

    return connector


def tutorial():

    to_do(
        [
            (st.write, INIT_GSHEET),
        ],
        "google_sheet_public_gsheet",
    )

    to_do(
        [(st.write, MAKE_IT_PUBLIC), (st.image, "imgs/link_sharing.png")],
        "make_it_public",
    )

    def url_to_toml():
        import toml

        url_input_str = st.text_input("URL of the Google Sheet")
        convert = st.button("Create TOML credentials")
        if url_input_str or convert:
            assert url_input_str.startswith(
                "https://docs.google.com/"
            ), "Invalid URL, must start with https://docs.google.com"
            toml_output = toml.dumps({"gsheets": {"public_gsheets_url": url_input_str}})
            st.code(toml_output, "toml")

    to_do(
        [
            (
                st.write,
                """**Create TOML credentials**""",
            ),
            (url_to_toml,),
        ],
        "google_sheet_creds_formatted",
    )

    to_do(
        [(st.write, PASTE_INTO_SECRETS), (st.image, "imgs/fill_secrets.png")],
        "copy_pasted_secrets",
    )


def app():
    import streamlit as st
    import pandas as pd
    from gsheetsdb import connect

    # Share the connector across all users connected to the app
    @st.experimental_singleton()
    def get_connector():
        return connect()

    # Time to live: the maximum number of seconds to keep an entry in the cache
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
