
from pymongo import MongoClient

import streamlit as st
# MONGO_URI = st.secrets["MONGO_URI"]

MONGO_URI = st.secrets["MONGO_URI"]


if not MONGO_URI:
    st.error("❌ MONGO_URI not found in environment. Please check your .env file.")
    st.stop()

client = MongoClient(MONGO_URI)

db = client["taskrush_db"]  # You can name it anything
tasks_collection = db["tasks"]
