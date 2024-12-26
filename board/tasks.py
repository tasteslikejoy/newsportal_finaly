import os.path
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from board.models import Reply


@shared_task()
def send_new_reply_notification(reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    html_content = render_to_string(
        'reply_created_email.html',
        {
            'link': settings.SITE_URL,
            'text': reply.preview()
        }
    )
    msg = EmailMultiAlternatives(
        subject='[Celery] У вас новый отклик!',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reply.post.author.email],
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task()
def send_reply_accept_notification(reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    html_content = render_to_string(
        'reply_accept_email.html',
        {
            'link': settings.SITE_URL,
            'post': f'{settings.SITE_URL}' + r'/posts/' + f'{reply.post.pk}'
        }
    )
    print(reply.author.email)
    msg = EmailMultiAlternatives(
        subject='[Celery] Ваш отклик приняли!',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reply.author.email],
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task()
def send_mass_notification(title, text):
    emails = User.objects.all().values_list('email', flat=True)
    html_content = render_to_string(
        'mass_notification_email.html',
        {
            'link': settings.SITE_URL,
            'title': title,
            'text': text,
         }
    )
    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=emails
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()