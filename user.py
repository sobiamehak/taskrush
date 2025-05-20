import streamlit as st

from pymongo import MongoClient
import bcrypt


MONGO_URI = st.secrets["MONGO_URI"]

if not MONGO_URI:
    st.error("❌ MONGO_URI not found. Please check your .env file.")
    st.stop()
client:MongoClient = MongoClient(MONGO_URI)
db = client["tasker_db"]
users_collection = db["users"] 


class UserManager:

    def signup(self):


        st.subheader("🆕 Create an Account")

        if "signup_done" not in st.session_state:
            st.session_state.signup_done = False

        # If signup is not done, show the signup form
        if not st.session_state.signup_done:
            username = st.text_input("Choose a Username")
            password = st.text_input("Choose a Password", type="password")
            role = st.selectbox("Choose Role", ["buyer", "seller"])

            if st.button("Sign Up"):

                # user already singup that names are saved in data base
                if users_collection.find_one({"username": username}):
                    st.warning("⚠️ Username already exists!")
                else:
                    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    # store user in mongodb database
                    users_collection.insert_one({
                    "username": username,
                    "password": hashed_password,
                    "role": role
                })
                    st.session_state.signup_done = True
                    st.balloons()
                    st.rerun()
  

        # If signup is done, show a centered success message
        else:
            st.markdown(
                """
                <div style='
                    background-color: #DFF2BF;
                    color: #4F8A10;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 50px;
                '>
                    ✅ Signup successful! Please <u>switch to Login</u> to continue.
                </div>
                """,
                unsafe_allow_html=True
            )

    def login(self):
        st.session_state.signup_done = False
        st.subheader("🔐 Login to your Account")

        # Initialize session state variables if missing
        if "username_input" not in st.session_state:
            st.session_state.username_input = ""
        if "password_input" not in st.session_state:
            st.session_state.password_input = ""

        # Use st.text_input with keys to persist values
        username = st.text_input("Username", value=st.session_state.username_input, key="username_input")
        password = st.text_input("Password", type="password", value=st.session_state.password_input, key="password_input")

        if st.button("Login"):
            user = users_collection.find_one({"username": username})
            if user and bcrypt.checkpw(password.encode(), user["password"]):
                st.session_state.user = user
                st.session_state.logged_in = True
                st.success(f"Welcome, {username}!")
                st.balloons()
                st.rerun()
            else:
                st.error("Incorrect username or password.")
''