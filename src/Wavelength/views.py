from django.shortcuts import render, redirect
from .models import FileUpload
import mne
import pandas as pd  
import numpy as np                
import plotly.graph_objects as go 
import plotly.io as pio
from plotly.offline import plot
from plotly.graph_objs import Layout, YAxis, Scatter, Annotation, Annotations, Data, Figure, Marker, Font
mne.set_log_level('WARNING')

 # Process the uploaded file here (e.g., using MNE)
def handle_uploaded_file(f): 
   # Read and save raw data
   raw = mne.io.read_raw_fif(f, preload=True)
   print(raw.info) 
   #Preprossing with filtering
   raw.filter(1,20)
   epoch_plot=epoch_handler(raw)
   channel_plot= channel_picks(raw)

   return epoch_plot, channel_plot

   
# def events(raw):
#    events = mne.find_events(raw, stim_channel="STI 014")
#    event_ids= ['aud_1', 'aud_r', 'vis_1', 'smiley', 'button']
#    fig = mne.viz.plot_events(events, raw.info['sfreq'], raw.first_samp, show=False)
#    figure = go.Figure(layout=dict(showlegend=True), data=[dict(name=e) for e in event_ids])
#    events_html= pio.to_html(fig, full_html=True)
#    return events_html

def channel_picks(raw):
   picks = mne.pick_types(raw.info, meg='grad', exclude=[])
   start, stop = raw.time_as_index([0,10])
   
   n_channels = 20
   data, times = raw[picks[:n_channels], start:stop]
   ch_names = [raw.info['ch_names'][p] for p in picks[:n_channels]]
   step = 1. / n_channels
   kwargs = dict(domain=[1 - step, 1], showticklabels=False, zeroline=False, showgrid=False)

   
   layout = Layout(yaxis=go.layout.YAxis(kwargs), showlegend=False)
   traces = [Scatter(x=times, y=data.T[:, 0])]


   for ii in range(1, n_channels):
        kwargs.update(domain=[1 - (ii + 1) * step, 1 - ii * step])
        layout.update({'yaxis%d' % (ii + 1): go.layout.YAxis(kwargs), 'showlegend': False})
        traces.append(Scatter(x=times, y=data.T[:, ii], yaxis='y%d' % (ii + 1)))

  
   annotations = Annotations([go.layout.Annotation(x=-0.06, y=0, xref='paper', yref='y%d' % (ii + 1),
                                      text=ch_name, font=go.layout.annotation.Font(size=9), showarrow=False)
                          for ii, ch_name in enumerate(ch_names)])
   layout.update(annotations=annotations)
   layout.update(autosize=False, width=1000, height=600)
   fig = Figure(data=Data(traces), layout=layout)
   channels_html= pio.to_html(fig, full_html=True)
   return channels_html

      
def epoch_handler(raw):
   #Preprosses with ICA
   ica = mne.preprocessing.ICA(n_components=20,random_state=0)    
   ica.fit(raw)
   bad_ica, scores = ica.find_bads_eog(raw, 'MEG 0122', threshold =2)   
   
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
   epochs = ica.apply(epochs,exclude=ica.exclude)
   epochs.apply_baseline((None,0))
   
   values = epochs.get_data().mean(axis=0)
   values = pd.DataFrame(np.transpose(values), columns=epochs.info['ch_names'])
   values.head()
   
   fig = go.Figure(layout=dict(xaxis=dict(title='time'),yaxis=dict(title='data')))
   for ch in epochs.info['ch_names']:
      fig.add_scatter(x=epochs.times, y=values[ch], name=ch)

   epochs_html= pio.to_html(fig, full_html=True)
   return epochs_html
   

def settings(request):
    return render(request, "pages/settings.html", {})
   
def presentation (request):
    return render(request, "pages/presentation.html", {})

#First page
def home (request):
    #In here, you can pull data, transform data, etc
     if request.method == 'POST':
        newfile = request.FILES['file']
        document = FileUpload.objects.create(file=newfile)
        document.save()
        return redirect('settings')
     return render(request,"pages/home.html", {})



    
 