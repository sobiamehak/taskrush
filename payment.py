import streamlit as st
import stripe


# Load environment variables from .env
import streamlit as st
# stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]




# Set your Stripe secret key from environment variable
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]


# In-memory offer list (replace with DB later if needed)
offers = []

# Offer class definition
class Offer:
    def __init__(self, task_title, seller, amount):
        self.task_title = task_title
        self.seller = seller
        self.amount = amount
        self.is_paid = False

# Payment Manager
class PaymentManager:
    def __init__(self):
        self.show_offer_input = False
        self.selected_task = None
        self.offer_amount = 0

    def start_offer(self, task):
        self.show_offer_input = True
        self.selected_task = task

    def send_offer_ui(self, seller_username):
        if self.show_offer_input and self.selected_task:
            st.subheader(f"Send Offer for: {self.selected_task['title']}")
            self.offer_amount = st.number_input("Enter Offer Amount (PKR)", min_value=100, step=50)
            if st.button("Send Offer"):
                new_offer = Offer(
                    task_title=self.selected_task['title'],
                    seller=seller_username,
                    amount=self.offer_amount
                )
                offers.append({
                    'task_title': self.selected_task['title'],
                    'buyer': self.selected_task['username'],
                    'offer': new_offer
                })
                st.success("✅ Offer sent to buyer!")
                self.show_offer_input = False
                self.selected_task = None

    def view_offers(self, current_user):
        st.subheader("📨 Your Offers")

        user_offers = [o for o in offers if o['buyer'] == current_user['username']]

        if not user_offers:
            st.info("No offers received yet.")
            return

        for i, entry in enumerate(user_offers):
            offer = entry['offer']
            with st.expander(f"{offer.task_title} — from {offer.seller}"):
                st.markdown(f"💰 **Offer Amount:** PKR {offer.amount}")
                if not offer.is_paid:
                    if st.button(f"Pay with Stripe (PKR {offer.amount})", key=f"pay_{i}"):
                        self.create_stripe_checkout(offer.amount, entry)
                else:
                    st.success("✅ Already Paid")

    def create_stripe_checkout(self, amount, entry):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'pkr',
                        'product_data': {
                            'name': f"Offer for {entry['task_title']}",
                        },
                        'unit_amount': int(amount * 100),  # PKR to paisa
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url="http://localhost:8501?success=true",
                cancel_url="http://localhost:8501?canceled=true",
            )
            st.markdown(f"[Click here to pay securely 🔐](%s)" % session.url)
        except Exception as e:
            st.error(f"Stripe Error: {e}")
