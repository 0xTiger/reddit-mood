import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
import statsmodels.api as sm


dow = lambda i: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][(i + 1) % 7]


with open('assets/mood.json') as f:
    data = json.load(f)

normed = []
for v in data.values():
    moods = np.array(v['data'], dtype=float)
    normed.append(10 * np.nan_to_num(moods, nan=np.nanmean(moods)) / len(v['clrs']))

daily_average_mood = np.mean(normed, axis=0)

lowess = sm.nonparametric.lowess

df = pd.DataFrame({'x': list(range(365)), 'y': daily_average_mood})
df['moving_avg'] = [i[1] for i in lowess(df['y'], df['x'], frac=1./3)]
df['dow'] = df['x'].map(dow)

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
    xaxis=dict(
        tickmode='array',
        tickvals=[0,32,60,91,121,152,182,213,244,274,305,335],
        ticktext=['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    ))
fig.show()
