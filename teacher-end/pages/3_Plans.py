
import streamlit as st
import stripe
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

stripe.api_key = ""

plans = {
    "Essentials": {
        "description": "Exam monitoring, review exams for possible cheating, restrict computer functionality, basic plagiarism detection, integration with Canvas LTI, access 480p exam recordings.",
        "price": "$13 per student annually",
        "cta": "Purchase Essentials",
        "id": "huoqejpwqjfiowehgoipq1"
    },
    "Enhanced": {
        "description": "All Essentials features, AI-driven live proctoring and content analysis, customizable reporting, access 720p exam recordings, option for live proctor, enhanced plagiarism detection and verification.",
        "price": "$14.50 per student annually",
        "cta": "Purchase Enhanced",
        "id": "i2o3jr230ruijpiehgo"
    },
    "Institutional": {
        "description": "All Enhanced features, ID verification and photo comparison, exam environment monitoring, detailed AI exam reports, access 1080p exam recordings, early access to beta features and research, priority support and training, consultation and collaboration, consent to white-labeling.",
        "price": "$16 per student annually",
        "cta": "Contact Sales",
        "id": "ji214j3bhijdpoa024u9"
    },
    "Custom": {
        "description": "Choose the features most important to your organization, access up to 4K exam recordings.",
        "price": "Contact for quote",
        "cta": "Contact Sales",
        "id": "i21kojq30rjseejpsie394asldk"
    }
}

def send_sales_email(email, plan_name):
    """Send email to sales team"""
    try:
        sender_email = st.secrets.get("SENDER_EMAIL")  # Store email in Streamlit secrets
        sender_password = st.secrets.get("SENDER_PASSWORD")  # Store password in Streamlit secrets
        
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = "sales@sysproctoring.com"
        message['Subject'] = f"Sales Inquiry for {plan_name} Plan"
        
        body = f"""
        A potential customer has expressed interest in the {plan_name} plan.

        Customer Email: {email}

        Please follow up with this customer to discuss their specific needs.
        """
        message.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

st.set_page_config(initial_sidebar_state="collapsed")
st.title("Pricing Plans")

col1, col2, col3, col4 = st.columns(4)

for i, (plan_name, plan_details) in enumerate(plans.items()):
    with (col1 if i == 0 else col2 if i == 1 else col3 if i == 2 else col4):
        with st.container(border=True):
            st.subheader(plan_name)
            st.write(plan_details["description"])
            st.write(f"**Price:** {plan_details['price']}")
            
            if plan_details["cta"] == "Purchase Essentials":
                if st.button(plan_details["cta"], key=f"{plan_details['id']}"):
                    try:
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price_data': {
                                    'currency': 'usd',
                                    'product_data': {
                                        'name': 'Essentials Plan',
                                    },
                                    'unit_amount': 1300,
                                },
                                'quantity': 1,
                            }],
                            mode='payment',
                            success_url='https://example.com/success',
                            cancel_url='https://example.com/cancel',
                        )
                        st.rerun()
                        st.markdown(f"<script>window.location.href='{checkout_session.url}';</script>", unsafe_allow_html=True)
                    except stripe.error.StripeError as e:
                        st.error(f"Error: {e}")
            
            elif plan_details["cta"] == "Purchase Enhanced":
                if st.button(plan_details["cta"], key=f"{plan_details['id']}"):
                    try:
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price_data': {
                                    'currency': 'usd',
                                    'product_data': {
                                        'name': 'Enhanced Plan',
                                    },
                                    'unit_amount': 1450,
                                },
                                'quantity': 1,
                            }],
                            mode='payment',
                            success_url='https://example.com/success',
                            cancel_url='https://example.com/cancel',
                        )
                        st.rerun()
                        st.markdown(f"<script>window.location.href='{checkout_session.url}';</script>", unsafe_allow_html=True)
                    except stripe.error.StripeError as e:
                        st.error(f"Error: {e}")
            
            elif plan_details["cta"] == "Contact Sales":
                email = st.text_input(
                    "Your Email", 
                    key=f"email_{plan_name}", 
                    placeholder="Enter your email"
                )
                
                if st.button(plan_details["cta"], key=f"{plan_details['id']}"):
                    if email and '@' in email:
                        if send_sales_email(email, plan_name):
                            st.success("We'll contact you soon!")
                    else:
                        st.error("Please enter a valid email address.")