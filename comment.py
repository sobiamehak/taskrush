
import streamlit as st

class CommentManager:

    def add_comment(self, task_index, tasks):  # ← accept tasks as argument
        st.markdown("**Comments**")
        task = tasks[task_index]

        if 'user' not in st.session_state or st.session_state.user is None:
            st.warning("Login to comment.")
            return

        comment = st.text_input(f"Leave a comment on {task['title']}:", key=f"comment_{task_index}")
        if st.button("Submit", key=f"btn_{task_index}"):
            task['comments'].append({
                'user': st.session_state.user['username'],
                'text': comment
            })
            st.success("Comment added!")

        for c in task['comments']:
            st.markdown(f"- **{c['user']}**: {c['text']}")
