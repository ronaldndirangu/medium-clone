from django.core.mail import send_mail, EmailMessage
from authors import settings
from django.template.loader import render_to_string
from authors.apps.authentication.models import User


class SendEmail():
    def send_article_notification_email(self, email, title, author):
        user = User.objects.filter(email=email).first()
        subject = "Notifications"

        # render template
        body = render_to_string('article_notification.html', context={
            'action_url': "http://",
            'user': user,
            'title': title,
            'author': author
        })

        # set mail to email content with subject, body ,sender and recepient
        # with html content type
        mail = EmailMessage(
            subject, body, "authorshaven@gmail.com", to=[email])
        mail.content_subtype = 'html'

        # send email
        mail.send()

    def send_comment_notification_email(self, email, title, author, commenter):
        user = User.objects.filter(email=email).first()
        subject = "Notifications"

        # render template
        body = render_to_string('comment_notification.html', context={
            'action_url': "http://",
            'user': user,
            'title': title,
            'author': author,
            'commenter': commenter
        })

        # set mail to email content with subject, body ,sender and recepient
        # with html content type
        mail = EmailMessage(
            subject, body, "authorshaven@gmail.com", to=[email])
        mail.content_subtype = 'html'

        # send email
        mail.send()
