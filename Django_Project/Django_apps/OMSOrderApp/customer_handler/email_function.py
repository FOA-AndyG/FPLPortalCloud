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
