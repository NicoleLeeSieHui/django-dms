from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.contrib.sites.shortcuts import get_current_site  
from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMessage  
from django.core.files.storage import FileSystemStorage

from django.views.generic.edit import FormView
from django.template.loader import render_to_string  

from django.utils.encoding import force_bytes, force_str 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  

from dms import settings
from .forms import UploadFile, RegistrationForm
from . models import File_upload, History
from .token import account_activation_token  

#main page
def home(request):
    return render(request, "index.html")

@login_required(login_url='signin')
#user homepage
def homepage(request):

    if 's' in request.GET:
        s = request.GET['s']
        file = File_upload.objects.filter(title__icontains=s)

    else: 
        #to get all the uploaded files 
        file = File_upload.objects.all()
        
    return render(request, "homepage.html",{'file':file})

#admin homepage
def staffhomepage(request):

    #to get all the uploaded files
    file = File_upload.objects.all()
    return render(request, "staffhomepage.html",{'file':file})

#register new account
def register(request):
    rform = RegistrationForm()

    #registration
    if request.method == "POST":
       rform = RegistrationForm(request.POST)
       if rform.is_valid():
        user = rform.save(commit = False)
        user.is_active = False
        user.save()

        # Email send to user for verification 
        current_site = get_current_site(request)
        from_mail = settings.EMAIL_HOST_USER
        to_mail = [user.email]
        mail_subject = "Email Confirmation - DMS Page"
        message = render_to_string('verification.html', {  
            'user': user,  
            'domain': current_site.domain,  
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
            'token':account_activation_token.make_token(user)  
        })
        email = EmailMessage(  
                    mail_subject, message, from_mail, to_mail,
        )  
        email.send()  
        return redirect('message')


    context = {'rform':rform}

    return render(request, "register.html", context)
    

def activate(request, uidb64, token): 

    #to activate a new user 
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        login(request, user)
        return redirect('homepage')

    else:
        return render(request, 'failed.html')
        

def signin(request):
    #login
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        #check whether user is exist
        user = authenticate(request, username=username, password=password)

        #User exists
        if user is not None:
            login(request, user)
            return redirect('homepage')

        else:
            #User not exist
            messages.info(request,"Invalid Username or Password !!")
    
    context = {}

    return render(request, "signin.html", context)
    

class UploadFile(FormView):
    template_name = 'upload.html'
    form_class = UploadFile
    success_url = '/'

    #save the detail of uploaded file
    def form_valid(self,form):
        form.save()
        print(form.cleaned_data)
        super().form_valid(form)
        
        return redirect('homepage')
    
def history(request):
    if request.method == "POST":
        user = request.user
        action = request.POST['action']
        history = History(user=user, action=action)
        history.save()

        return redirect(f"/media/{action}")
    
    return render(request, "history.html")


def updatefile(request,title):

    if request.method == "POST":
        file = request.FILES['file']
        fs = FileSystemStorage()
        upfile = fs.save(file.name, file)

        File_upload.objects.filter(title=title).update(file=file)
        return redirect('homepage')

    return render(request, "update.html")

def editfile(request,title):
    file = File_upload.objects.get(title=title)

    if request.method == "POST":
        file.title = request.POST['title']
        file.save()
        return redirect('homepage')
        
    context = {'efile':file}

    return render(request, "edit.html", context)

def deletefile(request,title):
    file = File_upload.objects.get(title=title)

    if request.method == "POST":
        file.delete()
        return redirect('homepage')

    context = {'dfile':file}
    return render(request, "delete.html", context)

def message(request):
    return render(request, "message.html")

def error(request):
    return render(request, "error.html")

def signout(request):
    #logout
    logout(request)

    return redirect('home')





