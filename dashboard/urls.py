from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import UploadFile

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),  
    path('signin/', views.signin, name="signin"),
    path('homepage/', views.homepage, name="homepage"),
    path('staffhomepage/', views.staffhomepage, name="staffhomepage"),
    path('UploadFile/', UploadFile.as_view(), name='upload'),
    path('updatefile/<str:title>', views.updatefile, name="updatefile"),
    path('editfile/<str:title>', views.editfile, name="editfile"),
    path('deletefile/<str:title>', views.deletefile, name="deletefile"),
    path('message/', views.message, name="message"),
    path('error/', views.error, name="error"),
    path('signout/', views.signout, name="signout"),
    path('home/', views.home, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)