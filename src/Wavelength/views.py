from django.conf import settings
from django.shortcuts import render
from .models import FileUpload
import mne

 # Process the uploaded file here (e.g., using MNE)
def handle_uploaded_file(f): 
   # Read and save raw data
   raw = mne.io.read_raw_fif(f, preload=True) 
   print(raw.info)
   
   #Preprossing with filtering
   raw.filter(1,20)
      
   #Preprosses with ICA
   ica = mne.preprocessing.ICA(n_components=20,random_state=0)
   ica.fit(raw.copy().filter(8,35))
   ica.plot_components(outlines="head") #ICA displays
   
    
   bad_ica, scores = ica.find_bads_eog(raw, 'MEG 0122', threshold =2)   
   ica.apply(raw.copy(), exclude =ica.exclude).plot() #graph with better icas
   
   events = mne.find_events(raw, stim_channel="STI 014")
   event_dict = {
    "auditory/left": 1,
    "auditory/right": 2,
    "visual/left": 3,
    "visual/right": 4,
    "face": 5,
    "buttonpress": 32,
}
   epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict, preload=True) 
   epochs.plot(n_epochs=10, events=True) #before ica
   
   epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict, preload=True) 
   epochs = ica.apply(epochs,exclude=ica.exclude)
   epochs.apply_baseline((None,0))
   epochs["auditory"].plot_image(picks=[13]) #ICA Epoch image for one channel
   
def settings (request):
    return render(request, "pages/settings.html", {})

#First page
def home (request):
    #In here, you can pull data, transform data, etc
     if request.method == 'POST':
        newfile = request.FILES['file']
        document = FileUpload.objects.create(file=newfile)
        document.save()
        handle_uploaded_file(newfile)        
        return render(request, "pages/settings.html", {})
     return render(request,"pages/home.html", {})




    
