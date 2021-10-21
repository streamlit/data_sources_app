from supabase_py import create_client, Client
import streamlit as st

supabase: Client = create_client(**st.secrets["supabase"])
data = supabase.table("users").select("*").execute()
st.write(data)
