from django.shortcuts import render, redirect
from .forms import FileUploadForm

#First page
def home (request):
    #In here, you can pull data, transform data, etc
    return render(request,"pages/home.html", {}) 
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the uploaded file here (e.g., using MNE)
            uploaded_file = form.cleaned_data['file']
            
             # Do your processing here with 'uploaded_file'
            print(f"Uploaded file name: {uploaded_file.name}")


            # Redirect to a success page or do something else
            return redirect('')
        else: form.errors
    else:
        form = FileUploadForm()


    return render(request,'pages/home.html', {'form': form})