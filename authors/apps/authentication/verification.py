from django.core.mail import send_mail, EmailMessage
from authors import settings
from .models import User
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from datetime import date


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


class SendEmail():
    def send_verification_email(self, email, request):
        user = User.objects.filter(email=email).first()
        subject = "Verify your Authors Haven account"

        token = account_activation_token.make_token(user)
        current_site = get_current_site(request)

        # render template mail.txt
        body = render_to_string('mail.html', context={
            'action_url': "http://",
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
            'token': token
        })

        # set mail to email content with subject, body ,sender and recepient
        # with html content type
        mail = EmailMessage(subject, body, "janetnim401@gmail.com", to=[email])
        mail.content_subtype = 'html'

        # send email
        mail.send()

        return (token, urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'))

    def send_reset_pass_email(self, email, request):
        user = User.objects.filter(email=email).first()
        subject = "Forgot your Authors Haven password"

        token = account_activation_token.make_token(user)
        current_site = get_current_site(request)

        # render template mail.txt
        body = render_to_string('reset-password-mail.html', context={
            'action_url': "https://",
            'user': user,
            'domain': 'ah-titans-frontend.herokuapp.com',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
            'token': token
        })

        # set mail to email content with subject, body ,sender and recepient
        # with html content type
        mail = EmailMessage(subject, body, "janetnim401@gmail.com", to=[email])
        mail.content_subtype = 'html'

        # send email
        mail.send()

        return (token, urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'))
