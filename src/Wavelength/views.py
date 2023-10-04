
import re
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib.pylab import rand
from .models import FileUpload
import mne

 # Process the uploaded file here (e.g., using MNE)
def handle_uploaded_file():
   
# Read and save raw data
   data_set= mne.datasets.sample.data_path()
   data_raw_file= ( 
      data_set / "MEG" / "sample" / "sample_audvis_filt-0-40_raw.fif"
   )
   raw = mne.io.read_raw_fif(data_raw_file)
   
#Preprossing with ICA
   ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800)
   ica.fit(raw)
   ica.exclude = [1,2]
   ica.plot_properties(raw, picks=ica.exclude)
   
   original_raw = raw.copy()
   raw.load_data()
   ica.apply(raw)

   channels = [
    "MEG 0111",
    "MEG 0121",
    "MEG 0131",
    "MEG 0211",
    "MEG 0221",
    "MEG 0231",
    "MEG 0311",
    "MEG 0321",
    "MEG 0331",
    "MEG 1511",
    "MEG 1521",
    "MEG 1531",
    "EEG 001",
    "EEG 002",
    "EEG 003",
    "EEG 004",
    "EEG 005",
    "EEG 006",
    "EEG 007",
    "EEG 008",
]
   channel_ids = [raw.ch_names.index(channel) for channel in channels]
   original_raw.plot(order=channel_ids, start=12, duration=4)
   raw.plot(order=channel_ids, start=12, duration=4)
   
def settings (request):
    return render(request, "pages/settings.html", {})

#First page
def home (request):
    #In here, you can pull data, transform data, etc
     if request.method == 'POST':
        newfile = request.FILES['file']
        document = FileUpload.objects.create(file=newfile)
        document.save()
        return render(request, "pages/settings.html", {})
     return render(request,"pages/home.html", {})



    