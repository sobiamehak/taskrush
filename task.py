import streamlit as st
from comment import CommentManager
from payment import PaymentManager
from db import tasks_collection  # ✅ MongoDB collection import

class TaskManager:
    def __init__(self):
        self.payment_manager = PaymentManager()

    def post_task(self, username):
        st.subheader("📝 Post a New Task")
        title = st.text_input("Task Title")
        description = st.text_area("Task Description")
        budget = st.number_input("Budget (PKR)", min_value=100, step=50)

        if st.button("Post Task"):
            task = {
                'username': username,
                'title': title,
                'description': description,
                'budget': budget,
                'comments': []
            }

            # ✅ Save to MongoDB
            tasks_collection.insert_one(task)
            st.success("✅ Task posted successfully!")

            # ✅ Create Stripe checkout
            self.payment_manager.create_stripe_checkout(
                amount=budget,
                entry={'task_title': title}
            )

    def view_tasks(self):
        st.subheader("📄 All Posted Tasks")

        # ✅ Fetch tasks from MongoDB
        tasks = list(tasks_collection.find())
        if not tasks:
            st.info("No tasks posted yet.")
            return

        for i, task in enumerate(tasks):
            with st.expander(f"{task['title']} - by {task['username']} (Budget: {task['budget']} PKR)"):
                st.write(task['description'])

                # ✅ Comments
                comment_manager = CommentManager()
                comment_manager.add_comment(i, tasks)

                # ✅ Payment link at the bottom
                st.markdown("#### 💳 Make a Payment")
                self.payment_manager.create_stripe_checkout(
                    amount=task['budget'],
                    entry={'task_title': task['title']}
                )

    def get_all_tasks(self):
        return list(tasks_collection.find())
