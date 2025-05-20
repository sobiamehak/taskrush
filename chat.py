import streamlit as st

# ------------ Message Class ------------ #
class Message:
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message

# ------------ Private Chat Class ------------ #
class PrivateChat:
    def __init__(self, user1, user2):
        self.chat_id = self.get_chat_id(user1, user2)
        self.messages = []

    def add_message(self, sender, message):
        self.messages.append(Message(sender, message))

    def get_messages(self):
        return self.messages

    @staticmethod
    def get_chat_id(user1, user2):
        return "_".join(sorted([user1, user2]))

# ------------ Chat Manager ------------ #
class ChatManager:
    def __init__(self):
        if "private_chats" not in st.session_state:
            st.session_state.private_chats = {}

    def chat_ui(self):
        st.subheader("💬 Private Chat")

        current_user = st.session_state.user
        if not current_user:
            st.warning("Please login to use chat.")
            return

        chat_with = st.text_input("Enter username to chat with")

        if chat_with:
            chat_id = PrivateChat.get_chat_id(current_user['username'], chat_with)

            # Retrieve or create a private chat
            if chat_id not in st.session_state.private_chats:
                st.session_state.private_chats[chat_id] = PrivateChat(current_user['username'], chat_with)

            private_chat = st.session_state.private_chats[chat_id]

            st.markdown(f"### Chat with {chat_with}")

            # Show previous messages
            for msg in private_chat.get_messages():
                sender_display = "🟢 You" if msg.sender == current_user['username'] else f"🔵 {msg.sender}"
                st.markdown(f"**{sender_display}:** {msg.message}")

            # Input and send message
            new_msg = st.text_input("Type your message", key="private_msg")
            if st.button("Send Message"):
                if new_msg.strip():
                    private_chat.add_message(current_user['username'], new_msg.strip())
                    st.rerun()
