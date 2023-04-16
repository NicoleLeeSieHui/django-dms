from django.shortcuts import render, redirect, get_object_or_404
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
from .forms import RegistrationForm, AdminRegistrationForm, CheckBoxForm, UserPasswordForm, OwnPasswordForm
from .models import File_upload, FileHistory, LogHistory, LogUser
from django.contrib.auth.models import User
from .token import account_activation_token  

from django.contrib.auth.hashers import make_password

from django.http import HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


def trackuser(request,username):
    # retrieve the current user's uploaded files and count them
    upload_files = File_upload.objects.filter(uploader=username)
    upload_count = upload_files.count()

    delete_files = LogHistory.objects.filter(updated_by__username=username, action="deleted")
    delete_count = delete_files.count()

    edit_files = LogHistory.objects.filter(updated_by__username=username, action="edited")
    edit_count = edit_files.count()

    update_files = LogHistory.objects.filter(updated_by__username=username, action="updated")
    update_count = update_files.count()

    view_files = FileHistory.objects.filter(user__username=username)
    view_count = view_files.count()

    context = {'upload_count': upload_count,'delete_count': delete_count, 
               'edit_count':edit_count, 'update_count':update_count, 'view_count': view_count}

    return render(request, 'trackuser.html', context)


def loghistory_pdf(request):
    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # Create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Designate The Model
    loghistorys = LogHistory.objects.all()

    # Create blank list
    lines = []

    for loghistory in loghistorys:
        lines.append(str(loghistory.updated_at))
        lines.append(str(loghistory.updated_by)+ " " + loghistory.action + " file " + loghistory.file_name)
        lines.append("(" + loghistory.file_path + ")")
        lines.append("===================")
        lines.append("")
        
    #Loop
    for line in lines:
        textob.textLine(line)
            
    #Finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
        
    # Create a new HttpResponse object with the PDF data
    response = HttpResponse(buf, content_type='application/pdf')

    # Set the Content-Disposition header to inline to display the PDF in the browser
    response['Content-Disposition'] = 'inline; filename="loghistory.pdf"'

    # Return the HttpResponse object
    return response

def loguser_pdf(request):
    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # Create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Designate The Model
    logusers = LogUser.objects.all()

    # Create blank list
    lines = []

    for loguser in logusers:
        lines.append(str(loguser.time)+ "  " + str(loguser.log_user) + " " + loguser.action)
        lines.append("")
        
    #Loop
    for line in lines:
        textob.textLine(line)
            
    #Finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
        
    # Create a new HttpResponse object with the PDF data
    response = HttpResponse(buf, content_type='application/pdf')

    # Set the Content-Disposition header to inline to display the PDF in the browser
    response['Content-Disposition'] = 'inline; filename="loguser.pdf"'

    # Return the HttpResponse object
    return response


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

    if 's' in request.GET:
        s = request.GET['s']
        file = File_upload.objects.filter(title__icontains=s)

    else: 
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
    
def adminregister(request):
    rform = AdminRegistrationForm()

    #registration
    if request.method == "POST":
       rform = AdminRegistrationForm(request.POST)
       if rform.is_valid():
        user = rform.save(commit = False)
        user.is_staff = True
        user.is_superuser = True
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

    return render(request, "adminregister.html", context)

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
        if user.is_staff == True:
                login(request, user)
                return redirect('staffhomepage')
            
        else: 
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
            if user.is_staff == True:
                login(request, user)
                loguser_obj = LogUser(
                    log_user=request.user,
                    action="logged in"
                    )
                loguser_obj.save()
                return redirect('staffhomepage')
            
            else: 
                login(request, user)
                loguser_obj = LogUser(
                    log_user=request.user,
                    action="logged in"
                    )
                loguser_obj.save()
                return redirect('homepage')

        else:
            #User not exist
            messages.info(request,"Invalid Username or Password !!")
    
    context = {}

    return render(request, "signin.html", context)
    

def userlist(request):

    if 's' in request.GET:
        s = request.GET['s']
        users = User.objects.filter(username__icontains=s)

    else: 
        #to get all the uploaded files 
        users = User.objects.all()

    return render(request, 'userlist.html', {'users': users})

def adduser(request):
    form1 = RegistrationForm()
    form2 = CheckBoxForm()

    if request.method == "POST":
       form1 = RegistrationForm(request.POST)
       form2 = CheckBoxForm(request.POST)
       if form1.is_valid():
        if form2.is_valid():
            if request.POST.get('my_checkbox'):
                users = form1.save(commit = False)
                users.is_active = True
                users.is_staff = True
                users.is_superuser = True
                users.save()

            else:
                users = form1.save(commit = False)
                users.is_active = True
                users.is_staff = False
                users.is_superuser = False
                users.save()
        
        return redirect('userlist')
    
    context = {'form1':form1, 'form2': form2}

    return render(request, 'adduser.html', context)

def edituser(request, id):

    form = CheckBoxForm()
    users = User.objects.get(id=id)

    if request.method == 'POST':
        form = CheckBoxForm(request.POST)
        users.username = request.POST['username']
        users.email = request.POST['email']

        if form.is_valid():
            if request.POST.get('my_checkbox'):
                users.is_staff = True
                users.is_superuser = True
                users.save()

            else:
                users.is_staff = False
                users.is_superuser = False
                users.save()

        return redirect('userlist')          
    
    return render(request, 'edituser.html', {'users': users, 'form': form})

def editown(request, id):
    
    users = User.objects.get(id=id)
    form = OwnPasswordForm(users)

    if request.method == 'POST':
        users.username = request.POST['username']
        users.email = request.POST['email']
        form = OwnPasswordForm(users, request.POST)

        if form.is_valid():
            form.save()
            users.save()
            if request.user.is_staff == True:
                return redirect('staffhomepage')
            
            else: 
                return redirect('homepage')
        
        else:
            form = UserPasswordForm(users)        
    
    return render(request, 'editown.html', {'users': users, 'form': form})

def userpassword(request, id):
   users = User.objects.get(id=id)

   if request.method == 'POST':
        new_password = request.POST['new_password1']
        hashed_password = make_password(new_password)
        users.password = hashed_password
        users.save()

        return redirect('userlist')
        
   return render(request, 'userpassword.html', {'users': users})

def uploadfile(request):
    if request.method == "POST":
        title = request.POST['title']
        uploader = request.POST.get('uploader')
        file = request.FILES['file']
        File_upload.objects.create(title=title,uploader=uploader,file=file)

        file_obj = File_upload.objects.get(title=title)

        loghistory_obj = LogHistory(
            updated_by=request.user,
            file_name=file_obj.title,
            file_path=file_obj.file,
            action="uploaded"
            )
        loghistory_obj.save()
        
        if request.user.is_staff == True:
            return redirect('staffhomepage')
            
        else: 
            return redirect('homepage')
        

    return render(request, "upload.html")
    

def viewfile(request,title):
    # Get the file object using the file_id
    file_obj = File_upload.objects.get(title=title)

    # Create a new FileHistory object
    history_obj = FileHistory(
        file_name=file_obj.title,
        file_path=file_obj.file,
        user=request.user
    )
    history_obj.save()

    # Render the file view template
    return render(request, 'view.html', {'file': file_obj})

def loghistory(request):

    history_list = LogHistory.objects.all()
    
    return render(request, 'loghistory.html', {'history_list': history_list})

def loguser(request):

    loguser_list = LogUser.objects.all()
    
    return render(request, 'loguser.html', {'loguser_list': loguser_list})

def viewprofile(request,id):

    user = User.objects.get(id=id)
    
    return render(request, 'viewprofile.html', {'user':user})

def viewhistory(request, username):

    user = get_object_or_404(User, username=username)

    if 's' in request.GET:
        s = request.GET['s']
        history_list = FileHistory.objects.filter(file_name__icontains=s)

    else:
        
        history_list = user.filehistory_set.all()
    
    return render(request, 'viewhistory.html', {'user': user, 'history_list': history_list})


def updatefile(request,title):

    if request.method == "POST":
        file = request.FILES['file']
        fs = FileSystemStorage()
        upfile = fs.save(file.name, file)

        File_upload.objects.filter(title=title).update(file=file)

        file = File_upload.objects.get(title=title)

        loghistory_obj = LogHistory(
            updated_by=request.user,
            file_name=file.title,
            file_path=file.file,
            action="updated"
            )
        loghistory_obj.save()

        if request.user.is_staff == True:
            return redirect('staffhomepage')
            
        else: 
            return redirect('homepage')

    return render(request, "update.html")

def editfile(request,title):
    file = File_upload.objects.get(title=title)

    if request.method == "POST":

        file.title = request.POST['title']
        file.save()

        loghistory_obj = LogHistory(
            updated_by=request.user,
            file_name=file.title,
            file_path=file.file,
            action="edited"
            )
        loghistory_obj.save()

        if request.user.is_staff == True:
            return redirect('staffhomepage')
            
        else: 
            return redirect('homepage')
        
    context = {'efile':file}

    return render(request, "edit.html", context)

def deletefile(request,title):
    file = File_upload.objects.get(title=title)
    
    if request.method == "POST":

        loghistory_obj = LogHistory(
            updated_by=request.user,
            file_name=file.title,
            file_path=file.file,
            action="deleted"
            )
        loghistory_obj.save()

        if FileHistory.objects.filter(file_name=file.title) is not None:
            file.delete()
            FileHistory.objects.filter(file_name=file.title).delete()

            if request.user.is_staff == True:
                return redirect('staffhomepage')
            else: 
                return redirect('homepage')

        else:
            file.delete()
            
            if request.user.is_staff == True:
                return redirect('staffhomepage')
            else: 
                return redirect('homepage')

    context = {'dfile':file}
    return render(request, "delete.html", context)

def message(request):
    return render(request, "message.html")

def error(request):
    return render(request, "error.html")

def signout(request):
    #logout
    loguser_obj = LogUser(
        log_user=request.user,
        action="logged out"
        )
    loguser_obj.save()
    logout(request)

    return redirect('home')





