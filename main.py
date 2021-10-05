import inspect
import textwrap
import streamlit as st
from big_query_app import main as big_query_app
from snowflake_app import main as snowflake_app
from google_sheet_app import main as google_sheet_app
from intro import main as intro, INTRO_IDENTIFIER
import time


DATA_SOURCES = {
    INTRO_IDENTIFIER: {
        "app": intro,
        "secret_key": None,
        "docs_url": None,
        "app_path": "intro.py",
    },
    "🔎 BigQuery": {
        "app": big_query_app,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/bigquery.html",
        "app_path": "big_query_app.py",
    },
    "❄️ Snowflake": {
        "app": snowflake_app,
        "secret_key": "snowflake",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
        "app_path": "snowflake_app.py",
    },
    "📝 Public Google Sheet": {
        "app": google_sheet_app,
        "secret_key": "gsheets",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
        "app_path": "google_sheet_app.py",
    },
}

ERROR_MESSAGE = """Unfortunately, no credentials were found for data source: `{}` in your Streamlit secrets.
You can have a look at our [documentation]({}) 
to read more about how to connect to databases.  

If you have filled in secrets and this error still shows, make sure the secrets are under the identifier {}
We also optionally display it just below:"""


def has_credentials_for(data_source) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def _dev_load_secrets():
    import toml

    with open(".streamlit/secrets.toml", encoding="utf-8") as f:
        secrets_file_str = f.read()
    secrets = toml.loads(secrets_file_str)
    return secrets


if __name__ == "__main__":

    # ---- DEV ----
    secrets = st.sidebar.selectbox("(Dev) Secrets are...", ["Full", "Empty"])
    if secrets == "Full":
        st.secrets = _dev_load_secrets()
    else:
        st.secrets = dict()

    # -------------

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        list(DATA_SOURCES.keys()),
        index=0,
    )

    st.session_state["active_page"] = data_source

    if data_source == INTRO_IDENTIFIER:
        show_code = False
        show_balloons = False

    else:

        show_code = st.sidebar.checkbox("Show code")
        show_balloons = True

        st.title(f"{data_source} dashboard")

        has_credentials = has_credentials_for(data_source)

        if has_credentials:
            st.sidebar.success("✔ Connected.")

        else:
            st.sidebar.error("Not connected.")

            st.error(
                ERROR_MESSAGE.format(
                    data_source,
                    DATA_SOURCES[data_source]["docs_url"],
                    DATA_SOURCES[data_source]["secret_key"],
                )
            )

            # Show docs in an iframe
            with st.expander("Open the documentation ⬇️"):
                st.components.v1.iframe(
                    DATA_SOURCES[data_source]["docs_url"], height=600, scrolling=True
                )

    # Display data source app
    data_source_app = DATA_SOURCES[st.session_state["active_page"]]["app"]
    data_source_app()

    # Show source code if user checked the box
    if show_code:

        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(data_source_app)
        st.code(textwrap.dedent("".join(sourcelines[1:])), "python")

    # Release balloons to celebrate
    if show_balloons:
        st.balloons()
