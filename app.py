# uv venv --python 3.12.0
# .venv\Scripts\activate      # Windows
import streamlit as st
from user import UserManager
from task import TaskManager
from comment import CommentManager
from chat import ChatManager
from payment import PaymentManager
from streamlit_cookies_manager import EncryptedCookieManager

import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


MONGO_URI = st.secrets["MONGO_URI"]


MONGO_URI = st.secrets.get("MONGO_URI")
if not MONGO_URI:
    st.error("MONGO_URI missing")
    st.stop()

cookies = EncryptedCookieManager(
    prefix="taskrush_",  # Cookie name prefix
    password="a3f9dce0b1e04c8a8d5f4b1e12c4f9f3"  # Keep this secret
)

# cookies()  # This **loads** the cookies from the browser, this is required before access


class SuperTaskerApp:
    """
    Main application class to manage the TaskRush platform UI and user sessions.
    Uses OOP principles: encapsulation, single responsibility for each manager.
    """

    def __init__(self):
        self.user_manager = UserManager()
        self.task_manager = TaskManager()
        self.comment_manager = CommentManager()
        self.chat_manager = ChatManager()
        self.payment_manager = PaymentManager()


        if 'user' not in st.session_state:
         if cookies.get("user"):
            st.session_state["user"] = cookies.get("user")


        self.app_logo = "🛠️ TaskRush"
    
    def run(self):
        self.apply_local_css("assets/styles.css")
        self.check_payment_status()
        self.show_logo()
        self.login_or_signup_flow()


    def check_payment_status(self):
        query_params = st.query_params

        if "success" in query_params:
            st.success("✅ Payment successful! Thank you.")
            st.query_params.clear()  # Clear the query string after handling

        elif "canceled" in query_params:
            st.warning("❌ Payment canceled. You can try again.")
            st.query_params.clear()

  

    def show_logo(self):
        st.markdown(
            f"""
            <h1 style='
                color: #0b5394; background:pink;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                font-weight: 800;
                letter-spacing: 2px;
                text-align: center;
                margin-bottom: 30px;
            '>{self.app_logo}</h1>
            """,
            unsafe_allow_html=True
        )

    def login_or_signup_flow(self):
       if "user" in st.session_state and st.session_state.user:
         self.show_user_sidebar()
       else:
        choice = st.radio("Account Access", ["Login", "Signup"])

        if choice == "Login":
                self.user_manager.login()
                if "user" in st.session_state and st.session_state.user:
                 cookies["user"] = st.session_state["user"]
                 cookies.save()
                 
                
        else:
                self.user_manager.signup()

    

    def show_user_sidebar(self):
        user = st.session_state.user
        st.sidebar.success(f"Logged in as {user['username']} ({user['role'].capitalize()})")

        nav_choice = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Post Task", "View Tasks", "Chat", "My Offers", "Logout"]
        )

        if nav_choice == "Dashboard":
            self.show_dashboard()
        elif nav_choice == "Post Task":
            self.post_task()
        elif nav_choice == "View Tasks":
            self.view_tasks()
        elif nav_choice == "Chat":
            self.chat_ui()
        elif nav_choice == "My Offers":
            self.view_offers()
        elif nav_choice == "Logout":
            self.logout()

    def show_dashboard(self):
        st.subheader("📋 Dashboard")
        st.write(f"Welcome back, **{st.session_state.user['username']}**! Here's your overview:")

    def post_task(self):
        """
        Allow both buyers and sellers to post new tasks.
        """
        st.subheader("📝 Post a New Task")
        self.task_manager.post_task(st.session_state.user['username'])

    def view_tasks(self):
        st.subheader("🔍 Available Tasks")
        tasks = self.task_manager.get_all_tasks()

        if not tasks:
            st.info("No tasks posted yet. Please check back later.")
            return

        for i, task in enumerate(tasks):
            with st.expander(f"{task['title']} — by {task['username']} (Budget: {task['budget']} PKR)"):
                st.markdown(f"**Description:** {task['description']}")
                self.comment_manager.add_comment(i, tasks)

                # Sellers only can send offers
                if st.session_state.user['role'] == "seller":
                    if st.button(f"Send Offer for '{task['title']}'", key=f"offer_btn_{i}"):
                        self.payment_manager.start_offer(task)

        # Show the offer input UI if an offer is in process
        if self.payment_manager.show_offer_input:
            self.payment_manager.send_offer_ui(st.session_state.user['username'])

    def view_offers(self):
        if st.session_state.user['role'] == "buyer":
            st.subheader("💼 Your Received Offers")
            self.payment_manager.view_offers(st.session_state.user)
        else:
            st.warning("⚠️ Only buyers can view received offers.")

    def chat_ui(self):
        st.subheader("💬 Chat")
        self.chat_manager.chat_ui()

    def logout(self):
        """
        Logout the current user and refresh the app.
        """
        st.session_state.user = None
        del cookies["user"]
        cookies.save()
        st.success("✅ Logged out successfully!")
        st.rerun()

    def apply_local_css(self, css_file):
        try:
            with open(css_file) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("CSS file not found. Please check the path.")

# Run the app
if __name__ == "__main__":
    app = SuperTaskerApp()
    app.run()