from django.db import models

# Create your models here.
class Notification(models.Model):
    notifications_id = models.CharField(primary_key=True, max_length=255)
    module = models.CharField()
    to_user_id = models.CharField()
    message = models.CharField()
    notifications_status = models.CharField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'admin"."notifications'