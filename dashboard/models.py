from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here
class File_upload(models.Model):

    title_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length = 100)
    uploader = models.CharField(max_length = 100, default="")
    file = models.FileField(upload_to="")
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.title_id)

#Recently Viewed
class FileHistory(models.Model):
    file_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s history"

#File History
class LogHistory(models.Model):
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255)
    action = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.updated_by}'s log"
    
#User Log
class LogUser(models.Model):
    log_user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.log_user} {self.action}"


    
# class History(models.Model):
#     hist_id = models.BigAutoField(primary_key=True, default=1)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     file = models.ManyToManyField(File_upload, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user}'s history"

    
    
