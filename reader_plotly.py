import numpy as np
import pandas as pd
import plotly.graph_objects as go
import csv
import json
import statsmodels.api as sm


dow = lambda i: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][i]

data_file = 'assets/mood.json'

with open(data_file) as f:
    data = json.load(f)

for k, v in data.items():
    v['data'] = [x if x is not None else np.mean([x for x in v['data'] if x is not None]) for x in v['data']]

normed = [list(map(lambda x: 10*round(x / len(v['clrs']), 3), v['data'])) for k, v in data.items()]
moods = [np.mean(x) for x in np.transpose(np.array(normed))]

weekdays = [(i + 1) % 7 for i in range(365)]
#maybe animate to emphasize cyclical nature

lowess = sm.nonparametric.lowess

df = pd.DataFrame({'x': list(range(365)), 'y': moods, 'dow': map(dow, weekdays)})
df['moving_avg'] = [i[1] for i in lowess(df['y'], df['x'], frac=1./3)]

weekends = df[df['dow'].isin(['sat', 'sun'])]
weekends['moving_avg'] = [i[1] for i in lowess(weekends['y'], weekends['x'], frac=1./3)]

mondays = df[df['dow'] == 'mon']
mondays['moving_avg'] = [i[1] for i in lowess(mondays['y'], mondays['x'], frac=1./3)]

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='markers', name='All Days', marker=dict(color='black')))
fig.add_trace(go.Scatter(x=weekends['x'], y=weekends['y'], mode='markers', name='Weekends', marker=dict(color='green'), visible='legendonly'))
fig.add_trace(go.Scatter(x=mondays['x'], y=mondays['y'], mode='markers', name='Mondays', marker=dict(color='blue'), visible='legendonly'))
fig.add_trace(go.Line(x=df['x'], y=df['moving_avg'], name='All Days moving avg', line=dict(color='black', dash='dash')))
fig.add_trace(go.Line(x=weekends['x'], y=weekends['moving_avg'], name='Weekends moving avg', line=dict(color='green', dash='dash')))
fig.add_trace(go.Line(x=mondays['x'], y=mondays['moving_avg'], name='Mondays moving avg', line=dict(color='blue', dash='dash')))
fig.update_layout(

    title="How happy were redditors on each day of 2019?",
    xaxis_title="Month",
    yaxis_title="Average Happiness /10",
    font=dict(size=18, family="Courier New, monospace"),
    xaxis = dict(
        tickmode = 'array',
        tickvals = [0,32,60,91,121,152,182,213,244,274,305,335],
        ticktext = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    ))
fig.show()
