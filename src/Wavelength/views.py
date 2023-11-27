from django.shortcuts import render, redirect, HttpResponse
from .models import FileUpload
import mne
from mne.preprocessing import EOGRegression, ICA
import plotly.io as pio
import plotly.subplots
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
    chs = []
    chan_idxs = [raw.ch_names.index(ch) for ch in chs]
    new_raw.plot(order=chan_idxs, start=12, duration=4)
    print(new_raw.info)
    fig = raw.plot(order=chan_idxs, start=12, duration=4)
    channels_html= pio.to_html(fig, full_html=True)
    return HttpResponse("Channel graph handled.")
      
def events(request):
    raw.crop(tmax=60).load_data()
    return HttpResponse("Events graph handled.")
   
# def events(raw):
#    events = mne.find_events(raw, stim_channel="STI 014")
#    event_ids= ['aud_1', 'aud_r', 'vis_1', 'smiley', 'button']
#    fig = mne.viz.plot_events(events, raw.info['sfreq'], raw.first_samp, show=False)
#    figure = go.Figure(layout=dict(showlegend=True), data=[dict(name=e) for e in event_ids])
#    events_html= pio.to_html(fig, full_html=True)
#    return events_html

# def channel_picks(raw):
#    picks = mne.pick_types(raw.info, meg='grad', exclude=[])
#    start, stop = raw.time_as_index([0,10])
   
#    n_channels = 20
#    data, times = raw[picks[:n_channels], start:stop]
#    ch_names = [raw.info['ch_names'][p] for p in picks[:n_channels]]
#    step = 1. / n_channels
#    kwargs = dict(domain=[1 - step, 1], showticklabels=False, zeroline=False, showgrid=False)

   
#    layout = Layout(yaxis=go.layout.YAxis(kwargs), showlegend=False)
#    traces = [Scatter(x=times, y=data.T[:, 0])]


#    for ii in range(1, n_channels):
#         kwargs.update(domain=[1 - (ii + 1) * step, 1 - ii * step])
#         layout.update({'yaxis%d' % (ii + 1): go.layout.YAxis(kwargs), 'showlegend': False})
#         traces.append(Scatter(x=times, y=data.T[:, ii], yaxis='y%d' % (ii + 1)))

  
#    annotations = Annotations([go.layout.Annotation(x=-0.06, y=0, xref='paper', yref='y%d' % (ii + 1),
#                                       text=ch_name, font=go.layout.annotation.Font(size=9), showarrow=False)
#                           for ii, ch_name in enumerate(ch_names)])
#    layout.update(annotations=annotations)
#    layout.update(autosize=False, width=1000, height=600)
#    fig = Figure(data=Data(traces), layout=layout)
#    channels_html= pio.to_html(fig, full_html=True)
#    return channels_html

      
# def epoch_handler(raw):
#    #Preprosses with ICA
#    ica = mne.preprocessing.ICA(n_components=20,random_state=0)    
#    ica.fit(raw)
#    bad_ica, scores = ica.find_bads_eog(raw, 'MEG 0122', threshold =2)   
   
#    events = mne.find_events(raw, stim_channel="STI 014")
#    event_dict = {
#     "auditory/left": 1,
#     "auditory/right": 2,
#     "visual/left": 3,
#     "visual/right": 4,
#     "face": 5,
#     "buttonpress": 32,
#    }
#    epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict, preload=True) 
#    epochs = ica.apply(epochs,exclude=ica.exclude)
#    epochs.apply_baseline((None,0))
   
#    values = epochs.get_data().mean(axis=0)
#    values = pd.DataFrame(np.transpose(values), columns=epochs.info['ch_names'])
#    values.head()
   
#    fig = go.Figure(layout=dict(xaxis=dict(title='time'),yaxis=dict(title='data')))
#    for ch in epochs.info['ch_names']:
#       fig.add_scatter(x=epochs.times, y=values[ch], name=ch)

#    epochs_html= pio.to_html(fig, full_html=True)
#    return epochs_html
   

def settings1(request):
    return render(request, "pages/settings-pg1.html", {})

def settings2(request):
    return render(request, "pages/settings-pg2.html", {})
   
def settings3(request):
    return render(request, "pages/settings-pg3.html", {})

def presentation (request):    
    graph_vars_dict = {
        var: globals()[var] for var in ['filter_html', 'regression_html', 'ica_html']
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



    
 