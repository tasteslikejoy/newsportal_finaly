from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Reply, PostReply
from .tasks import send_new_reply_notification


@receiver(post_save, sender=Reply)
def send_reply_notification(sender, instance, created, **kwargs):
    if created:
        print(instance)
        (send_new_reply_notification.delay(reply_id=instance.pk))
