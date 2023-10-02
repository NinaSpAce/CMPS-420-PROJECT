
from django.shortcuts import render
from django.http import HttpResponse
from .models import FileUpload
import mne

 # Process the uploaded file here (e.g., using MNE)
def handle_uploaded_file(f):
   mne.io.read_raw_fif(f)

def settings (request):
    return render(request, "pages/settings.html", {})

#First page
def home (request):
    #In here, you can pull data, transform data, etc
     if request.method == 'POST':
        newfile = request.FILES['file']
        document = FileUpload.objects.create(file=newfile)
        document.save()
        return HttpResponse("File was uploaded")
     return render(request,"pages/home.html", {})



    