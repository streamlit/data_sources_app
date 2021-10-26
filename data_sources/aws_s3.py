import streamlit as st
import s3fs
import pandas as pd

from utils.ui import to_do, to_button

TOML_SERVICE_ACCOUNT = """[aws_s3]
    AWS_ACCESS_KEY_ID = ...
    AWS_SECRET_ACCESS_KEY = ...
"""

SIGN_UP = """**[Sign up](https://aws.amazon.com/) for AWS or log in**"""

CREATE_BUCKET = f"""**Create an S3 bucket and add a file**  
Go to the [S3 console](https://s3.console.aws.amazon.com/s3/home), click on {to_button("Create bucket")} 
and create a bucket
"""

CREATE_BUCKET_IMG_PATH = "imgs/aws-1.png"

UPLOAD_FILE_IN_BUCKET = f"""**Upload a file in the bucket**  
Navigate to the upload section of your new bucket and upload the sample `.csv` provided below:
"""

FILE_NAME = "myfile.csv"
FILE_PATH = f"utils/{FILE_NAME}"

CREATE_ACCESS_KEYS = f"""**Create an access key**  
Go to the [AWS console](https://console.aws.amazon.com/) and under your user name selector, 
click on {to_button("My Security Credentials")}  
On the new page, you will be able to click on {to_button("Create New Access Key")}  
Now copy the "Access Key ID" and "Secret Access Key".
"""

FORMAT_INTO_TML = f"""**Format your access key into `.toml` format**  
Streamlit Secrets expect credentials to be given in the following format:
"""

PASTE_INTO_SECRETS = f"""**Paste these `.toml` credentials into your Streamlit Secrets! **  
You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}"""

# @st.experimental_singleton()
# We intendedly do not cache the connector in the actual data sources app
# so that if secrets are removed, the error is shown and we don't use
# the connector from cache
def get_connector():
    """ Create a connector to AWS S3 """

    connector = s3fs.S3FileSystem(
        anon=False,
        # Note that Streamlit automatically turns the access keys from your secrets
        # into environment variables, where s3fs searches for them by default.
        # Hence the two following lines are optional, although we keep them for clarity:
        key=st.secrets["aws_s3"]["AWS_ACCESS_KEY_ID"],
        secret=st.secrets["aws_s3"]["AWS_SECRET_ACCESS_KEY"],
    )

    return connector


@st.experimental_memo(ttl=60 * 60)
def load_csv():
    return pd.read_csv(FILE_PATH).to_csv().encode("utf-8")


@st.experimental_memo(ttl=60 * 60)
def read_file(_connector, filename):
    with _connector.open(filename) as f:
        return f.read().decode("utf-8")


def tutorial():

    st.write(
        "(Feel free to skip steps if you already have an account, bucket or file!)"
    )

    to_do(
        [(st.write, SIGN_UP)],
        "sign_up_or_log_in",
    )

    to_do(
        [
            (st.write, CREATE_BUCKET),
            (st.image, CREATE_BUCKET_IMG_PATH),
        ],
        "create_bucket",
    )

    data = load_csv()
    to_do(
        [
            (st.write, UPLOAD_FILE_IN_BUCKET),
            (
                st.download_button,
                "Download sample .csv",
                data,
                FILE_NAME,
            ),
        ],
        "upload_file_in_bucket",
    )

    to_do(
        [(st.write, CREATE_ACCESS_KEYS)],
        "create_access_keys",
    )

    to_do(
        [
            (st.write, FORMAT_INTO_TML),
            (st.code, TOML_SERVICE_ACCOUNT, "toml"),
        ],
        "format_into_toml",
    )

    to_do(
        [(st.write, PASTE_INTO_SECRETS), (st.image, "imgs/arrow.png")],
        "copy_pasted_secrets",
    )


def app():
    import streamlit as st
    import s3fs

    @st.experimental_singleton()
    def get_connector():
        """ Create a connector to AWS S3 """

        connector = s3fs.S3FileSystem(
            anon=False,
            # Note that Streamlit automatically turns the access keys from your secrets
            # into environment variables, where s3fs searches for them by default.
            # Hence the two following lines are optional, although we keep them for clarity:
            key=st.secrets["aws_s3"]["AWS_ACCESS_KEY_ID"],
            secret=st.secrets["aws_s3"]["AWS_SECRET_ACCESS_KEY"],
        )

        return connector

    st.markdown(f"## 📦 Connecting to AWS S3")

    aws_s3_connector = get_connector()
    # st.write(aws_s3_connector.ls("s3://home/"))

    bucket_name = st.text_input(label="Bucket name")
    if bucket_name:
        content = read_file(aws_s3_connector, f"{bucket_name}/{FILE_NAME}")
        st.write("Here's the content of the `.csv` file:")
        st.write(content)