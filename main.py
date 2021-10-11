import inspect
import textwrap
import streamlit as st

from big_query_app import (
    main as big_query_app,
    get_connector as get_big_query_connector,
)

from snowflake_app import (
    main as snowflake_app,
    get_connector as get_snowflake_connector,
)

from google_sheet_app import (
    main as google_sheet_app,
    get_connector as get_google_sheet_connector,
)

from intro import main as intro, INTRO_IDENTIFIER


DATA_SOURCES = {
    INTRO_IDENTIFIER: {
        "app": intro,
        "secret_key": None,
        "docs_url": None,
        "app_path": "intro.py",
        "get_connector": None,
    },
    "🔎 BigQuery": {
        "app": big_query_app,
        "secret_key": "bigquery",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/bigquery.html",
        "app_path": "big_query_app.py",
        "get_connector": get_big_query_connector,
    },
    "❄️ Snowflake": {
        "app": snowflake_app,
        "secret_key": "snowflake",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/snowflake.html",
        "app_path": "snowflake_app.py",
        "get_connector": get_snowflake_connector,
    },
    "📝 Public Google Sheet": {
        "app": google_sheet_app,
        "secret_key": "gsheets",
        "docs_url": "https://docs.streamlit.io/en/latest/tutorial/public_gsheet.html#connect-streamlit-to-a-public-google-sheet",
        "app_path": "google_sheet_app.py",
        "get_connector": get_google_sheet_connector,
    },
}

ERROR_MESSAGE = """Unfortunately, no credentials were found for data source: `{}` in your Streamlit secrets.
You can have a look at our [documentation]({}) 
to read more about how to connect to databases.  

If you have filled in secrets and this error still shows, make sure the secrets are under the identifier '`{}`'.  

We also display docs just below:"""


def has_credentials_in_secrets(data_source) -> bool:
    return DATA_SOURCES[data_source]["secret_key"] in st.secrets


def show_docs_iframe(data_source: str):
    with st.expander("Open the documentation ⬇️"):
        st.components.v1.iframe(
            DATA_SOURCES[data_source]["docs_url"], height=600, scrolling=True
        )


def show_error_when_not_connected(data_source: str):
    st.error(
        ERROR_MESSAGE.format(
            data_source,
            DATA_SOURCES[data_source]["docs_url"],
            DATA_SOURCES[data_source]["secret_key"],
        )
    )


def connect(data_source):
    """Try connecting to data source.
    Print exception should something wrong happen."""

    try:
        get_connector = DATA_SOURCES[data_source]["get_connector"]
        connector = get_connector()
        return connector

    except Exception as e:

        st.error(
            """There has been an error. While we have successfully found your secrets, they seem not to 
            enable connecting to the data source."""
        )

        with st.expander("👇 Read more about the error"):
            st.write(e)

        show_docs_iframe(data_source)
        st.stop()


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
    elif secrets == "Empty":
        st.secrets = dict()

    data_source = st.sidebar.selectbox(
        "Choose a data source",
        list(DATA_SOURCES.keys()),
        index=0,
    )

    st.session_state.active_page = data_source
    if "data_sources_already_connected" not in st.session_state:
        st.session_state.data_sources_already_connected = list()

    if data_source == INTRO_IDENTIFIER:
        show_code = False
        show_balloons = False

    else:
        show_code = True
        show_balloons = True

        # First, look for credentials in the secrets
        has_credentials = has_credentials_in_secrets(data_source)

        if has_credentials:
            st.sidebar.success("✔ Connected.")
        else:
            st.sidebar.error("❌ Not connected.")
            show_error_when_not_connected(data_source)
            show_docs_iframe(data_source)
            st.stop()

        # Then, check if one can successfully connect using the secrets
        connect(data_source)

    # Release balloons to celebrate
    if (
        show_balloons
        and data_source not in st.session_state.data_sources_already_connected
    ):
        st.session_state.data_sources_already_connected.append(data_source)
        show_balloons = False
        st.balloons()

    # Display data source app
    data_source_app = DATA_SOURCES[st.session_state["active_page"]]["app"]
    data_source_app()

    # Show source code
    if show_code:
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(data_source_app)
        st.code(textwrap.dedent("".join(sourcelines[1:])), "python")