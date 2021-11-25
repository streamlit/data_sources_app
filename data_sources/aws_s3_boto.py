import streamlit as st
import boto3

from utils.ui import to_do, to_button

SIGN_UP = """**[Sign up](https://aws.amazon.com/) for AWS or log in**"""

CREATE_BUCKET = f"""**Create a bucket**  
Go to the [S3 console](https://s3.console.aws.amazon.com/s3/home), click on {to_button("Create bucket")} 
and create a bucket
"""

UPLOAD_FILE_IN_BUCKET = f"""**Upload one or more file(s) in the bucket**  
Click on one of your buckets and head to the upload section. Now upload one or more file(s)
"""

CREATE_ACCESS_KEYS = f"""**Create an access key**  
First, visit the [AWS console](https://console.aws.amazon.com/). Then:
"""

FORMAT_INTO_TML = f"""**Generate your TOML credentials for Streamlit**  
Paste your "Access Key ID" and "Secret Access Key" below to generate TOML credentials
"""

PASTE_INTO_SECRETS = f"""**Paste these TOML credentials into your Streamlit Secrets! **  
You should click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} > {to_button("Secrets")}"""


# @st.experimental_singleton()
def get_connector():
    """Create a connector to AWS S3"""

    connector = boto3.Session(
        aws_access_key_id=st.secrets.aws_s3.ACCESS_KEY_ID,
        aws_secret_access_key=st.secrets.aws_s3.SECRET_ACCESS_KEY,
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
            (
                st.image,
                "https://user-images.githubusercontent.com/7164864/143440317-7db1d5f9-7dc6-45c2-b637-3ec360e73a6d.png",
            ),
        ],
        "create_bucket",
    )

    to_do(
        [
            (st.write, UPLOAD_FILE_IN_BUCKET),
            (
                st.image,
                "https://user-images.githubusercontent.com/7164864/143440405-aa572b34-b559-407c-97f5-ded4ad9f0495.png",
            ),
        ],
        "upload_file_in_bucket",
    )

    to_do(
        [
            (st.write, CREATE_ACCESS_KEYS),
            (
                st.image,
                "https://user-images.githubusercontent.com/7164864/143440472-f0bf5bd3-4029-49ad-8732-49e45ebdeef8.png",
            ),
        ],
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
        [
            (st.write, PASTE_INTO_SECRETS),
            (
                st.image,
                "https://user-images.githubusercontent.com/7164864/143440545-bf90572b-a192-47b1-986f-abcdeec625b6.png",
            ),
        ],
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
            aws_access_key_id=st.secrets.aws_s3.ACCESS_KEY_ID,
            aws_secret_access_key=st.secrets.aws_s3.SECRET_ACCESS_KEY,
        ).resource("s3")
        return connector

    # Time to live: the maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    @st.experimental_memo(ttl=TTL)
    def get_buckets(_connector) -> list:
        return [bucket.name for bucket in list(_connector.buckets.all())]

    def to_tuple(s3_object):
        return (
            s3_object.key,
            s3_object.last_modified,
            s3_object.size,
            s3_object.storage_class,
        )

    @st.experimental_memo(ttl=TTL)
    def get_files(_connector, bucket) -> pd.DataFrame:
        files = list(s3.Bucket(name=bucket).objects.all())
        if files:
            df = pd.DataFrame(
                pd.Series(files).apply(to_tuple).tolist(),
                columns=["key", "last_modified", "size", "storage_class"],
            )
            return df

    st.markdown(f"## 📦 Connecting to AWS S3")

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
