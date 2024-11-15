from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import groq
import os

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat, File
import markdown
from django.utils.safestring import mark_safe

from django.utils import timezone

from RAG.scripts.query_data import query_rag

from django.views.decorators.csrf import csrf_exempt
from subprocess import call

# os.environ['GROQ_API_KEY'] = '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'
# groq_client = groq.Client() 

# def ask_groq(message):
#     # response = groq_client.generate(prompt=message)
#     # query = groq.Query("generate(text, prompt='{}')".format(message))
#     # response = groq_client.execute(query)
#     response = groq_client(groq.generate(prompt=message))
#     answer = response.text
#     return answer

# Create your views here.
def chatbot(request, file_id):
    file = File.objects.get(id=file_id)

    chats = Chat.objects.filter(user=request.user, file=file)

    if request.method == 'POST':
        message = request.POST.get('message')
        # response = ask_groq(message)
        # response = 'Hello, ' + request.user.username

        response = query_rag(query_text=message, file=file, user_id=request.user.id)
        # response = extract_content(response)
        print (response)

        # Replace single newlines with <br> for line breaks
        response = response.replace('\n', '<br>')

        # Convert markdown to html
        response = mark_safe(markdown.markdown(response))


        if response is not None:
            chat = Chat(user=request.user, file=file, message=message, response=response, created_at=timezone.now())
            chat.save()
            return JsonResponse({'message': message, 'response': response})
        else:
            print("no response")

    return render(request, 'chat1.html', {'chats': chats, 'file_url': f'/media/{file.file.name}', 'file_name': file.name})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})

    else:     
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('dashboard')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    # Fetch all files associated with the logged-in user
    files = File.objects.filter(user=request.user)

    return render(request, 'dashboard.html', {'files': files})

def chat(request):
    return render(request, 'chat1.html')


from django.conf import settings
from django.http import FileResponse, Http404
def pdf_view(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        raise Http404("File not found")
    
@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        # Save the file
        file = File.objects.create(user=request.user, file=pdf_file, name=pdf_file.name)
        print("Here")

        # Run populate_database.py
        # To be changed later
        import sys
        python_executable = sys.executable
        script_path = os.path.join(settings.BASE_DIR, 'RAG', 'scripts', 'populate_database.py')
        call([python_executable, script_path, "--filename", f"{file.user.id}_{str(pdf_file.name.replace(' ', '_').replace('(', '').replace(')', ''))}", "--owner", str(file.user.id)])

        return JsonResponse({'success': True, 'file_url': f'/dashboard'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def delete(request, file_id):
    file = File.objects.get(id=file_id)
    file.delete()
    request.redirect(dashboard)