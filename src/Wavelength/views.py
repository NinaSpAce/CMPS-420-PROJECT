from django.shortcuts import render, redirect, HttpResponse
from .models import FileUpload
import mne
from mne.preprocessing import EOGRegression, ICA
import plotly.io as pio

import pandas as pd
import numpy as np
import plotly.graph_objects as go

mne.set_log_level('WARNING')


def filter_handling(request):
    raw.crop(0, 60).pick(picks=["mag", "stim"]).load_data()
    meg_picks = mne.pick_types(raw.info, meg=True)
    freqs = (60, 120, 180, 240)
    raw_notch_fit= raw.copy().notch_filter(freqs=freqs, picks=meg_picks, method="spectrum_fit", filter_length="10s"
    )

    spectrum = raw_notch_fit.compute_psd(fmax=75)
    psds, freq = spectrum.get_data(return_freqs=True)
    
    df_filter= pd.DataFrame(data=psds.T, columns=spectrum.info['ch_names'])
    
    fig = go.Figure()
    
    for ch in df_filter.columns:
        fig.add_trace(go.Scatter(x=freq, y=df_filter[ch], mode='lines', name=ch))
    
    fig.update_layout(title_text="Filtered Data", font=dict(size=20, family="Arial"))

    global filter_html
    filter_html= pio.to_html(fig, full_html=True)
    print(raw.info)
    return HttpResponse("Filtering Handled.")

def regression_handling(request):
    raw.pick(["eeg", "eog", "stim"])
    raw.load_data()
    raw.set_eeg_reference("average")
    raw.filter(0.3, 40)

    events = mne.find_events(raw)
    event_id = {"visual/left": 3, "visual/right": 4}
    epochs = mne.Epochs(raw, events, event_id=event_id, preload=True)
    model_plain = EOGRegression(picks="eeg", picks_artifact="eog").fit(epochs)
    epochs_clean_plain = model_plain.apply(epochs)
    epochs_clean_plain.apply_baseline()
    
    values = epochs_clean_plain.get_data().mean(axis=0)
    
    values = pd.DataFrame(np.transpose(values), columns=epochs_clean_plain.info['ch_names'])
    values.head()
    
    fig = go.Figure()
    
    
    fig.update_layout(title_text="Regression Data", font=dict(size=20, family="Arial"))
    
    for ch in epochs_clean_plain.info['ch_names']:
      fig.add_scatter(x=epochs_clean_plain.times, y=values[ch], name=ch)

    global regression_html
    regression_html= pio.to_html(fig, full_html=True)
    print(raw.info)
    return HttpResponse("Regression Handled.")


def ica_handling(request):
     raw.crop(tmax=60.0).pick_types(meg="mag", eeg=True, stim=True, eog=True)
     raw.load_data()
     filt_raw = raw.copy().filter(l_freq=1.0, h_freq=None)
     ica = ICA(n_components=15, max_iter="auto", random_state=97)
     ica.fit(filt_raw)

     ica.exclude = []
     eog_indices, eog_scores = ica.find_bads_eog(filt_raw)
     ica.exclude = eog_indices  
     
     ica_sources = ica.get_sources(inst=filt_raw)
     
     ica_sources_array = ica_sources.get_data()
    
     ica_df = pd.DataFrame(data=ica_sources_array.T[:, :15], columns=ica.info['ch_names'][:15])

     fig = go.Figure()
     
     times = raw.times
     
     for ch in ica_df.columns:
         fig.add_trace(go.Scatter(x=times, y=ica_df[ch], name=ch, mode='lines'))
     
     fig.update_layout(title_text="ICA Data", font=dict(size=20, family="Arial"))
     
    
     global ica_html
     ica_html= pio.to_html(fig, full_html=True)
     return HttpResponse("ICA Handled.")

       

def channel_graph(request):
    new_raw = raw.copy()
    channel_names = new_raw.ch_names
    channels_to_plot = channel_names[:20] 
    chan_idxs = [channel_names.index(ch) for ch in channels_to_plot]
    fig = go.Figure()
    
    for ids in chan_idxs:
        channel_data = new_raw.get_data()[ids, :]
        times = new_raw.times
        
        fig.add_trace(go.Scatter(x=times, y=channel_data, mode= 'lines', name= f'{new_raw.ch_names[ids]}'))
    
    fig.update_layout(width=800, height= 400, title_text="Channel Data", font=dict(size=20, family="Arial"))
    print(new_raw.info)
    global channels_html
    channels_html= pio.to_html(fig, full_html=True)
    return HttpResponse("Channel graph handled.")
      
      
def epoch_handler(request):
    new_raw = raw.copy()
    events = mne.find_events(new_raw, stim_channel="STI 014")
    event_dict = {
    "auditory/left": 1,
    "auditory/right": 2,
    "visual/left": 3,
    "visual/right": 4,
    "smiley": 5,
    "buttonpress": 32,
}
    reject_criteria = dict(
    mag=4000e-15,  # 4000 fT
    grad=4000e-13,  # 4000 fT/cm
    eeg=150e-6,  # 150 µV
    eog=250e-6, # 250 µV
)  
    epochs = mne.Epochs(
    new_raw,
    events,
    event_id=event_dict,
    tmin=-0.2,
    tmax=0.5,
    reject=reject_criteria,
    preload=True,
)
   
    selected_conds = ["auditory/left", "auditory/right", "visual/left", "visual/right"]
    epochs.equalize_event_counts(selected_conds)  # this operates in-place
    aud_epochs = epochs["auditory"]
    vis_epochs = epochs["visual"]
    del new_raw, epochs  # free up memory
   
    values = aud_epochs.get_data().mean(axis=0)

    print("Z values shape:", values.T.shape)
    print("X values shape:", aud_epochs.times.shape)
    print("Y values shape:", len(aud_epochs.info['ch_names']))
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=values.T, x=aud_epochs.times, y=aud_epochs.info['ch_names'], colorscale='Viridis'))
    
    fig.update_layout( 
    height= 600,
    title='Epochs Heatmap',
    font=dict(size=20, family='Arial')
)
    print(fig)
    global epochs_html
    epochs_html= pio.to_html(fig, full_html=True)
    return HttpResponse("Epochs graph handled.")
   

def settings1(request):
    return render(request, "pages/settings-pg1.html", {})

def presentation (request):    
    graph_vars_dict = {
        var: globals()[var] for var in ['filter_html', 'regression_html', 'ica_html', 'channels_html', 'epochs_html']
        if var in globals() and var != 'raw'  # Exclude 'raw'                                  
    }

    return render(request, "pages/presentation.html", graph_vars_dict)


#First page
def home (request):
    #In here, you can pull data, transform data, etc
     if request.method == 'POST':
        newfile = request.FILES['file']
        global raw
        raw = mne.io.read_raw_fif(newfile, verbose=False, preload=True)
        print(raw.info)
        document = FileUpload.objects.create(file=newfile)
        document.save()
        return redirect('settings-graphs')
     return render(request,"pages/home.html", {})



    
 