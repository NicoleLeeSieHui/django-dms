from django.db import models
from django.utils import timezone

# Create your models here
class File_upload(models.Model):

    title = models.CharField(max_length = 100)
    uploader = models.CharField(max_length = 100, default="")
    file = models.FileField(upload_to="")
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name
