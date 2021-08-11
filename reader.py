import numpy as np
import csv
import json
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib.animation as animation
from matplotlib.ticker import FixedLocator, FixedFormatter

strHex = lambda x: "%0.2x" % x
rgb2Hex = lambda c: '0x' + strHex(c[0]) + strHex(c[1]) + strHex(c[2])

dow = lambda i: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][(i + 1) % 7]
clr = lambda i,frame: {'All Days': ['k', 'k', 'k', 'k', 'k', 'k', 'k'],
                    'Weekends': ['k', 'k', 'k', 'k', 'k', 'g', 'g'],
                    'Mondays': ['b', 'k', 'k', 'k', 'k', 'k', 'k']}[frame][i]

dir = 'assets/'
data_file = dir + 'mood.json'

with open(data_file) as f:
    data = json.load(f)

normed = []
for k, v in data.items():
    moods = np.array(v['data'], dtype=float)
    normed.append(10 * np.nan_to_num(moods, nan=np.nanmean(moods)) / len(v['clrs']))

normed = np.array(normed)
daily_average_mood = normed.mean(axis=0)

lowess = sm.nonparametric.lowess
x, y = np.arange(365), daily_average_mood

x2 = [i for i in x if dow(i) in ['sat', 'sun']]
y2 = daily_average_mood[x2]

x3 = [i for i in x if dow(i) == 'mon']
y3 = daily_average_mood[x3]

w = [i[1] for i in lowess(y, x, frac=1./3)]
z = [i[1] for i in lowess(y2, x2, frac=1./3)]
u = [i[1] for i in lowess(y3, x3, frac=1./3)]

plt.style.use('ggplot')
fig = plt.figure()
ax = fig.add_subplot(1,1,1)

def animate(frame):

    ax.clear()
    for day, mood in zip(x, y):
        ax.scatter(day, mood, marker='.', c=clr((day + 1) % 7, frame), alpha=0.6)
    ax.plot(x, w, 'k--', label='All days')
    if frame == 'Weekends': ax.plot(x2, z, 'g--', label='Weekends')
    if frame == 'Mondays': ax.plot(x3, u, 'b--', label='Mondays')

    mposs = [1,32,60,91,121,152,182,213,244,274,305,335,365]
    #months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

    ax.set_xticks(mposs)
    # Don't display *any* major ticks labels
    ax.set_xticklabels('')
    # Create minor ticks and labels
    # Display the labels at MINOR ticks spaced between the bars
    minor_locations = [mposs[i] + 0.5*(mposs[i+1]-mposs[i]) for i in range(len(mposs)-1)]
    ax.xaxis.set_minor_locator(FixedLocator(minor_locations))
    ax.xaxis.set_minor_formatter(FixedFormatter(months))
    # Now actually hide the minor ticks but leave the labels
    ax.tick_params(axis='x', which='minor', length=0, labelsize=10)

    cs = {'All Days': 'k', 'Weekends': 'g',  'Mondays': 'b'}[frame]
    ax.annotate(text=frame, xy =(0.10,0.90), fontsize=20, alpha=0.6,
                        xycoords='axes fraction', verticalalignment='top',
                        horizontalalignment='left' , rotation = 0, color=cs)
    ax.annotate(text='u/tigeer', xy =(0.9,0.05), fontsize=8, alpha=0.6,
                        xycoords='axes fraction', verticalalignment='top',
                        horizontalalignment='left' , rotation = 0, color='k')

    plt.title("How happy were redditors \non each day of 2019?", fontsize=18)
    plt.ylabel("Average Happiness /10")
    plt.xlabel("Month")
    #plt.legend()

ani = animation.FuncAnimation(fig, animate, frames=['All Days', 'Weekends', 'Mondays']*6, interval=3000, repeat_delay=0)
#ani.save(dir + "mood.mp4")
plt.show()


# with open(dir + 'normed_mood.csv', 'w') as csvFile:
#         writer = csv.writer(csvFile, delimiter=',')
#         writer.writerows([[k for k in data]] + list(np.transpose(np.array(normed))))
#
# print("Saved csv @ %s" % dir + 'normed_mood.csv')
