import streamlit as st
import boto3

from utils.ui import to_do, to_button

SIGN_UP = """**[Sign up](https://aws.amazon.com/) for AWS or log in**"""

CREATE_BUCKET = f"""**Create a bucket**  
Go to the [S3 console](https://s3.console.aws.amazon.com/s3/home), click on {to_button("Create bucket")} 
and create a bucket
"""

CREATE_BUCKET_IMG_PATH = "imgs/aws-1.png"

UPLOAD_FILE_IN_BUCKET = f"""**Upload a file in the bucket**  
Navigate to the upload section of your new bucket and upload one or more file(s)
"""

CREATE_ACCESS_KEYS = f"""**Create an access key**  
Go to the [AWS console](https://console.aws.amazon.com/) and under your user name selector, 
click on {to_button("Security Credentials")}  
On the new page, toggle {to_button("> Access keys (access key ID and secret access key)")} you will 
be able to click on {to_button("Create New Access Key")} and then toggle {to_button("> Show Access Key")}.
"""

FORMAT_INTO_TML = f"""**Generate your TOML credentials for Streamlit**  
Paste your "Access Key ID" and "Secret Access Key" below to generate TOML credentials
"""

PASTE_INTO_SECRETS = f"""**Paste these `.toml` credentials into your Streamlit Secrets! **  
You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}"""


@st.experimental_singleton()
def get_connector():
    """Create a connector to AWS S3"""

    connector = boto3.Session(
        aws_access_key_id=st.secrets.aws_s3.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=st.secrets.aws_s3.AWS_SECRET_ACCESS_KEY,
    ).resource("s3")

    return connector


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

    to_do(
        [
            (st.write, UPLOAD_FILE_IN_BUCKET),
        ],
        "upload_file_in_bucket",
    )

    to_do(
        [(st.write, CREATE_ACCESS_KEYS)],
        "create_access_keys",
    )

    def generate_toml():
        import toml

        form = st.form(key="toml_form")
        access_key_id = form.text_input("Access Key ID")
        secret_access_key = form.text_input("Secret Access Key", type="password")
        submit = form.form_submit_button("Create TOML credentials")
        if submit:
            json_credentials = {
                "aws_s3": {
                    "ACCESS_KEY_ID": access_key_id,
                    "SECRET_ACCESS_KEY": secret_access_key,
                }
            }
            toml_credentials = toml.dumps(json_credentials)
            st.write("""TOML credentials:""")
            st.caption(
                "(You can copy this TOML by hovering on the code box: a copy button will appear on the right)"
            )
            st.code(toml_credentials, "toml")

    to_do(
        [
            (st.write, FORMAT_INTO_TML),
            (generate_toml,),
        ],
        "format_into_toml",
    )

    to_do(
        [(st.write, PASTE_INTO_SECRETS), (st.image, "imgs/fill_secrets.png")],
        "copy_pasted_secrets",
    )


def app():
    import streamlit as st
    import pandas as pd
    import boto3

    @st.experimental_singleton()
    def get_connector():
        """Create a connector to AWS S3"""
        connector = boto3.Session(
            aws_access_key_id=st.secrets.aws_s3.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=st.secrets.aws_s3.AWS_SECRET_ACCESS_KEY,
        ).client("s3")
        return connector

    # Time to live: the maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    @st.experimental_memo(ttl=TTL)
    def get_buckets(_connector) -> list:
        return [bucket.name for bucket in list(_connector.buckets.all())]

    @st.experimental_memo(ttl=TTL)
    def get_files(_connector, bucket) -> pd.DataFrame:
        files = s3.list_objects_v2(Bucket=bucket).get("Contents")
        if files:
            return pd.DataFrame(files)[["Key", "LastModified", "Size", "StorageClass"]]

    st.markdown(f"## 📦 Connecting to AWS S3 (boto3)")

    s3 = get_connector()

    buckets = get_buckets(s3)
    if buckets:
        st.write(f"🎉 Found {len(buckets)} bucket(s)!")
        bucket = st.selectbox("Choose a bucket", buckets)
        files = get_files(s3, bucket)
        if isinstance(files, pd.DataFrame):
            st.write(f"📁 Found {len(files)} file(s) in this bucket:")
            st.dataframe(files)
        else:
            st.write(f"This bucket is empty!")
    else:
        st.write(f"Couldn't find any bucket. Make sure to create one!")
