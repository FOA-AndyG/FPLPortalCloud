from datetime import datetime

from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# email function =================================================================
def create_email_backend():
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'system.admin@enitiallab.com'
    EMAIL_HOST_PASSWORD = 'Sa!@12345'
    email_backend = EmailBackend(host=EMAIL_HOST, port=EMAIL_PORT, use_tls=EMAIL_USE_TLS,
                                 username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD, fail_silently=False)
    return email_backend


def send_account_email_function(sender, recipient, link, email_subject, email_template):
    try:
        email_backend = create_email_backend()
        email_from = sender
        recipient_customer = [recipient.username]
        content = {
            'customer': recipient,
            'login_link': link,
        }
        msg_html = render_to_string(email_template, content)

        msg_customer = EmailMessage(subject=email_subject, body=msg_html, from_email=email_from,
                                    to=recipient_customer, connection=email_backend)
        msg_customer.content_subtype = "html"
        msg_customer.send()
        email_backend.close()
        print("Email sent!")
        # return True
    except Exception as e:
        print(e)
        # return False


def create_fedex_email_backend():
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'williamw@fplsolution.com'
    # email account password
    # EMAIL_HOST_PASSWORD = 'WiWu%6784$'
    # google app password
    EMAIL_HOST_PASSWORD = "ttqm unug qqhn bmev"
    email_backend = EmailBackend(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        use_tls=EMAIL_USE_TLS,
        username=EMAIL_HOST_USER,
        password=EMAIL_HOST_PASSWORD,
        fail_silently=False
    )
    return email_backend


def send_fedex_email_function(df):
    try:
        email_backend = create_fedex_email_backend()

        current_date = datetime.now().strftime("%Y-%m-%d")
        email_subject = f"FPL Pickup Request – Trailer Ready"
        email_from = 'williamw@fplsolution.com'

        recipient_email = ["andyg@furnitureproslogistics.com"]
        cc_email = ["andyg@furnitureproslogistics.com"]

        # recipient_email = [
        #     "industry-trailer-request@corp.ds.fedex.com",
        #     "LH.IDSY@corp.ds.fedex.com",
        #     "danny.orozco@fedex.com",
        #     "maria.solorzano@fedex.com",
        #     "esquivelmarco78@gmail.com",
        #     "mmikeg186@gmail.com",
        #     "davidvgvgonzalez777@gmail.com",
        #     "pocket30kk@gmail.com",
        # ]
        # cc_email = [
        #     "vincentd@furnitureproslogistics.com",
        #     "victorh@furnitureproslogistics.com",
        #     "abnerg@furnitureproslogistics.com",
        #     "andyg@furnitureproslogistics.com"
        # ]

        email_template = 'OMSOrderApp/parts/fedex_email_template.html'
        context = {
            "data": df.to_dict(orient="records"),
            "current_date": current_date,
        }
        msg_html = render_to_string(email_template, context)

        msg_customer = EmailMessage(
            subject=email_subject,
            body=msg_html,
            from_email=email_from,
            to=recipient_email,
            cc=cc_email,
            connection=email_backend)
        msg_customer.content_subtype = "html"
        msg_customer.send()

        email_backend.close()
        return {"status": True, "message": "Email sent successfully!"}
    except Exception as e:
        return {"status": False, "message": str(e)}
