from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here
class File_upload(models.Model):

    title = models.CharField(max_length = 100)
    uploader = models.CharField(max_length = 100, default="")
    file = models.FileField(upload_to="")
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name
    
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=1000, default="")
    date = models.DateTimeField(default=timezone.now)
