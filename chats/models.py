from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import datetime

UserModel = get_user_model()


# Create your models here.
class Chat(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    p1 = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name='p1')
    p2 = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name='p2')

    history = models.JSONField(default=dict)

    def add_message(self, who, content):
        if who in [self.p1, self.p2]:
            self.history[str(datetime.datetime.now())] = {
                'author': who.id,
                'message': content
            }
            self.save()
            return True

        return False

