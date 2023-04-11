from django.contrib import admin
from . models import File_upload, FileHistory, LogHistory

# Register your models here.
admin.site.register(File_upload)
admin.site.register(FileHistory)
admin.site.register(LogHistory)