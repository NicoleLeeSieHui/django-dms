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

#main page
def home(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        #check whether user is exist
        user = authenticate(request, username=username, password=password)

        #User exists
        if user is not None:
            #check whether user is admin
            if user.is_staff == True:
                login(request, user)

                #create LogUser obj to record users' entry log
                loguser_obj = LogUser(
                    log_user=request.user,
                    action="logged in"
                    )
                loguser_obj.save()
                return redirect('staffhomepage')
            
            else: 
                login(request, user)
                
                #create LogUser obj to record users' entry log
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

    return render(request, "index.html", context)

@login_required(login_url='')
#user homepage
def homepage(request):

    #if search
    if 's' in request.GET:
        s = request.GET['s']
        file = File_upload.objects.filter(title__icontains=s)

    else: 
        #to get all the uploaded files 
        file = File_upload.objects.all()
        
    return render(request, "homepage.html",{'file':file})

#admin homepage
def staffhomepage(request):

    #if search
    if 's' in request.GET:
        s = request.GET['s']
        file = File_upload.objects.filter(title__icontains=s)

    else: 
        #to get all the uploaded files 
        file = File_upload.objects.all()

    return render(request, "staffhomepage.html",{'file':file})

#user register new account
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
    
#admin register new account
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

#activate account
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
      
#display system users (admin only)
def userlist(request):
    
    #if search
    if 's' in request.GET:
        s = request.GET['s']
        users = User.objects.filter(username__icontains=s)

    else: 
        #to get all the system users 
        users = User.objects.all()

    return render(request, 'userlist.html', {'users': users})

#add new user (admin only)
def adduser(request):
    form1 = RegistrationForm()
    form2 = CheckBoxForm()

    if request.method == "POST":
       form1 = RegistrationForm(request.POST)
       form2 = CheckBoxForm(request.POST)
       if form1.is_valid():
        if form2.is_valid():
            #check whether the user is assigned as admin
            if request.POST.get('my_checkbox'):
                #admin
                users = form1.save(commit = False)
                users.is_active = True
                users.is_staff = True
                users.is_superuser = True
                users.save()

            else:
                #normal user
                users = form1.save(commit = False)
                users.is_active = True
                users.is_staff = False
                users.is_superuser = False
                users.save()
        
        return redirect('userlist')
    
    context = {'form1':form1, 'form2': form2}

    return render(request, 'adduser.html', context)

#edit user (admin only)
def edituser(request, id):

    form = CheckBoxForm()
    users = User.objects.get(id=id)

    if request.method == 'POST':
        form = CheckBoxForm(request.POST)
        users.username = request.POST['username']
        users.email = request.POST['email']

        if form.is_valid():
            #check whether the user is assigned as admin
            if request.POST.get('my_checkbox'):
                #admin
                users.is_staff = True
                users.is_superuser = True
                users.save()

            else:
                #normal user
                users.is_staff = False
                users.is_superuser = False
                users.save()

        return redirect('userlist')          
    
    return render(request, 'edituser.html', {'users': users, 'form': form})

#edit own profile details
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

#change user password (admin only)
def userpassword(request, id):
   users = User.objects.get(id=id)

   if request.method == 'POST':
        #hash the new password 
        new_password = request.POST['new_password1']
        hashed_password = make_password(new_password)
        users.password = hashed_password
        users.save()

        return redirect('userlist')
        
   return render(request, 'userpassword.html', {'users': users})

#upload new file
def uploadfile(request):
    if request.method == "POST":
        title = request.POST['title']
        uploader = request.POST.get('uploader')
        file = request.FILES['file']
        #create file obj to store file uploaded
        File_upload.objects.create(title=title,uploader=uploader,file=file)

        file_obj = File_upload.objects.get(title=title)

        #create a new LogHistory object to record file uploaded history
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
    
#view file
def viewfile(request,title):
    #get the file object using the title
    file_obj = File_upload.objects.get(title=title)

    #create a new FileHistory object to store file recently viewed
    history_obj = FileHistory(
        file_name=file_obj.title,
        file_path=file_obj.file,
        user=request.user
    )
    history_obj.save()

    return render(request, 'view.html', {'file': file_obj})

#display all file uploaded, deleted, updated, edited history
def loghistory(request):

    #get all the LogHistory objects
    history_list = LogHistory.objects.all()
    
    return render(request, 'loghistory.html', {'history_list': history_list})

#generate pdf report for file history log (admin only)
def loghistory_pdf(request):
    #create Bytestream buffer
    buf = io.BytesIO()
    
    #create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    
    #create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    #get all the history objects
    loghistorys = LogHistory.objects.all()

    #create blank list
    lines = []

    for loghistory in loghistorys:
        lines.append(str(loghistory.updated_at))
        lines.append(str(loghistory.updated_by)+ " " + loghistory.action + " file " + loghistory.file_name)
        lines.append("(" + loghistory.file_path + ")")
        lines.append("===================")
        lines.append("")
        
    #loop
    for line in lines:
        textob.textLine(line)
            
    #finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
        
    #create a new HttpResponse object with the PDF data
    response = HttpResponse(buf, content_type='application/pdf')

    #to display the PDF in the browser
    response['Content-Disposition'] = 'inline; filename="loghistory.pdf"'

    return response

#display all the user entry and exit log (admin only)
def loguser(request):

    #get all the LogUser objects
    loguser_list = LogUser.objects.all()
    
    return render(request, 'loguser.html', {'loguser_list': loguser_list})

#generate pdf report for user history log (admin only)
def loguser_pdf(request):
    #create Bytestream buffer
    buf = io.BytesIO()
    
    #create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    
    #create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    #get all the LogUser objects
    logusers = LogUser.objects.all()

    #create blank list
    lines = []

    for loguser in logusers:
        lines.append(str(loguser.time)+ "  " + str(loguser.log_user) + " " + loguser.action)
        lines.append("")
        
    #loop
    for line in lines:
        textob.textLine(line)
            
    #finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
        
    #create a new HttpResponse object with the PDF data
    response = HttpResponse(buf, content_type='application/pdf')

    #display the PDF in the browser
    response['Content-Disposition'] = 'inline; filename="loguser.pdf"'

    return response

#view own profile details
def viewprofile(request,id):

    #get the user object using the user id
    user = User.objects.get(id=id)
    
    return render(request, 'viewprofile.html', {'user':user})

#view own recently viewed record
def viewhistory(request, username):

    user = get_object_or_404(User, username=username)

    #if search
    if 's' in request.GET:
        s = request.GET['s']
        history_list = FileHistory.objects.filter(file_name__icontains=s)

    else:
        
        #get the recently viewed file of the user 
        history_list = user.filehistory_set.all()
    
    return render(request, 'viewhistory.html', {'user': user, 'history_list': history_list})

#track user on the amount of upload, delete, edit, update and view (admin only)
def trackuser(request,username):

    users = User.objects.get(username=username)

    #retrieve the user's uploaded files and count 
    upload_files = File_upload.objects.filter(uploader=username)
    upload_count = upload_files.count()

    #retrieve the user's deleted files and count
    delete_files = LogHistory.objects.filter(updated_by__username=username, action="deleted")
    delete_count = delete_files.count()

    #retrieve the user's edited files and count
    edit_files = LogHistory.objects.filter(updated_by__username=username, action="edited")
    edit_count = edit_files.count()

    #retrieve the user's updated files and count
    update_files = LogHistory.objects.filter(updated_by__username=username, action="updated")
    update_count = update_files.count()

    #retrieve the user's viewed files and count
    view_files = FileHistory.objects.filter(user__username=username)
    view_count = view_files.count()

    context = {'users': users, 'upload_count': upload_count,'delete_count': delete_count, 
               'edit_count':edit_count, 'update_count':update_count, 'view_count': view_count}

    return render(request, 'trackuser.html', context)

#update file
def updatefile(request,title):

    if request.method == "POST":
        file = request.FILES['file']
        fs = FileSystemStorage()
        upfile = fs.save(file.name, file)

        #get the title of the file chosen to update
        File_upload.objects.filter(title=title).update(file=file)

        file = File_upload.objects.get(title=title)

        #create a new LogHistory object to record file updated history
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

#edit file title
def editfile(request,title):
    #get the file object using the file title
    file = File_upload.objects.get(title=title)

    if request.method == "POST":

        #save the new file title
        file.title = request.POST['title']
        file.save()

        #create a new LogHistory object to record file edited history
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

#delete file
def deletefile(request,title):
    file = File_upload.objects.get(title=title)
    
    if request.method == "POST":

        #create a new LogHistory object to record file deleted history
        loghistory_obj = LogHistory(
            updated_by=request.user,
            file_name=file.title,
            file_path=file.file,
            action="deleted"
            )
        loghistory_obj.save()

        #the deleted file will be deleted respectively in the recently viewed record
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

#return check email message
def message(request):
    return render(request, "message.html")

#return error message
def error(request):
    return render(request, "error.html")

#sign out from the system
def signout(request):
    
    #create LogUser obj to record users' exit log
    loguser_obj = LogUser(
        log_user=request.user,
        action="logged out"
        )
    loguser_obj.save()
    logout(request)

    return redirect('home')





