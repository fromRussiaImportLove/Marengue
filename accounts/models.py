from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class AdvUser(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True)
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Have user activated?')
    send_messages = models.BooleanField(default=True, verbose_name='Do send notify about changes?')
    telegram_username = models.CharField(max_length=32, unique=True,
                                         verbose_name='Telegram username for bot communicating')
    calendar_link = models.URLField(verbose_name='Link for common calendar')

    STUDENT = 1
    TEACHER = 2
    SUPERVISOR = 3
    ROLE_CHOICES = (
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (SUPERVISOR, 'Supervisor'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

'''
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        AdvUser.objects.create(user=instance)
    instance.AdvUser.save()
'''