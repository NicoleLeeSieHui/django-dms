from django.contrib import admin
from . models import File_upload, FileHistory, LogHistory, LogUser

# Register your models here.
admin.site.register(File_upload)
admin.site.register(FileHistory)
admin.site.register(LogHistory)
admin.site.register(LogUser)