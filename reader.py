import json
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from matplotlib import animation, ticker


dow = lambda i: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][(i + 1) % 7]
clr = lambda i,frame: {
    'All Days': ['k', 'k', 'k', 'k', 'k', 'k', 'k'],
    'Weekends': ['k', 'k', 'k', 'k', 'k', 'g', 'g'],
    'Mondays':  ['b', 'k', 'k', 'k', 'k', 'k', 'k']
}[frame][i]


with open('assets/mood.json') as f:
    data = json.load(f)

normed = []
for v in data.values():
    moods = np.array(v['data'], dtype=float)
    normed.append(10 * np.nan_to_num(moods, nan=np.nanmean(moods)) / len(v['clrs']))

daily_average_mood = np.mean(normed, axis=0)
everyday = np.arange(365)
weekends = [i for i in everyday if dow(i) in ['sat', 'sun']]
mondays = [i for i in everyday if dow(i) == 'mon']

lowess = sm.nonparametric.lowess
w = [i for _, i in lowess(daily_average_mood, everyday, frac=1/3)]
z = [i for _, i in lowess(daily_average_mood[weekends], weekends, frac=1/3)]
u = [i for _, i in lowess(daily_average_mood[mondays], mondays, frac=1/3)]

plt.style.use('ggplot')
fig, ax = plt.subplots()


def animate(frame):
    colors = [clr(day_of_week, frame) for day_of_week in (everyday + 1) % 7]
    ax.clear()
    ax.scatter(everyday, daily_average_mood, marker='.', c=colors, alpha=0.8)
    ax.plot(everyday, w, 'k--', label='All days')
    if frame == 'Weekends': ax.plot(weekends, z, 'g--', label='Weekends')
    if frame == 'Mondays': ax.plot(mondays, u, 'b--', label='Mondays')

    mposs = [1,32,60,91,121,152,182,213,244,274,305,335,365]
    months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

    ax.set_xticks(mposs)
    ax.set_xticklabels([])
    # Create minor ticks and labels
    # Display the labels at minor ticks spaced between the bars
    minor_locations = [mposs[i] + 0.5*(mposs[i+1]-mposs[i]) for i in range(len(mposs)-1)]
    ax.xaxis.set_minor_locator(ticker.FixedLocator(minor_locations))
    ax.xaxis.set_minor_formatter(ticker.FixedFormatter(months))
    # Hide the minor ticks but leave the labels
    ax.tick_params(axis='x', which='minor', length=0, labelsize=10)

    colors = {'All Days': 'k', 'Weekends': 'g',  'Mondays': 'b'}[frame]
    shared_kwargs = dict(
        alpha=0.6,
        xycoords='axes fraction',
        verticalalignment='top',
        horizontalalignment='left', 
        rotation=0,
    )
    ax.annotate(text=frame, xy=(0.10, 0.90), fontsize=20, color=colors, **shared_kwargs)
    ax.annotate(text='u/tigeer', xy=(0.9, 0.05), fontsize=8, color='k', **shared_kwargs)
    ax.set_title("How happy were redditors \non each day of 2019?", fontsize=18)
    ax.set_ylabel("Average Happiness /10")
    ax.set_xlabel("Month")

ani = animation.FuncAnimation(
    fig, 
    animate, 
    frames=['All Days', 'Weekends', 'Mondays']*6, 
    interval=3000, 
    repeat_delay=0
)
plt.show()
