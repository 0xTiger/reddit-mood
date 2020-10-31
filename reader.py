import numpy as np
import csv
import json
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib.animation as animation
from matplotlib.ticker import FixedLocator, FixedFormatter

strHex = lambda x: "%0.2x" % x
rgb2Hex = lambda c: '0x' + strHex(c[0]) + strHex(c[1]) + strHex(c[2])

day_of_week = lambda i: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][i]
clr = lambda i,j: [['k', 'k', 'k', 'k', 'k', 'k', 'k'],
                    ['k', 'k', 'k', 'k', 'k', 'g', 'g'],
                    ['b', 'k', 'k', 'k', 'k', 'k', 'k']][j][i]

dir = 'assets/'
data_file = dir + 'mood.json'

with open(data_file) as f:
    data = json.load(f)

for k, v in data.items():
    v['data'] = [x if x is not None else np.mean([x for x in v['data'] if x is not None]) for x in v['data']]

normed = [list(map(lambda x: 10*round(float(x)/ len(v['clrs']), 3), v['data'])) for k,v in data.items()]
moods = [np.mean(x) for x in np.transpose(np.array(normed))]

weekdays = [(i + 1) % 7 for i in range(365)]
#maybe animate to emphasize cyclical nature

lowess = sm.nonparametric.lowess
x, y = list(range(365)), moods
x2 = [i for i in x if dow(weekdays[i]) in ['sat', 'sun']]
y2 = [moods[i] for i in x2]
x3 = [i for i in x if dow(weekdays[i]) == 'mon']
y3 = [moods[i] for i in x3]
w = [i[1] for i in lowess(y, x, frac=1./3)]
z = [i[1] for i in lowess(y2, x2, frac=1./3)]
u = [i[1] for i in lowess(y3, x3, frac=1./3)]

plt.style.use('ggplot')
fig = plt.figure()
ax = fig.add_subplot(1,1,1)

def animate(j):

    ax.clear()
    for day, mood in zip(x, y):
        ax.scatter(day, mood, marker='.', c=clr(weekdays[day], j), alpha=0.6)
    ax.plot(x, w, 'k--', label='All days')
    if j == 1: ax.plot(x2, z, 'g--', label='Weekends')
    if j == 2: ax.plot(x3, u, 'b--', label='Mondays')
    ax.plot()

    mposs = [1,32,60,91,121,152,182,213,244,274,305,335,365]
    #bin_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    bin_labels = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

    ax.set_xticks(mposs)
    # Don't display *any* major ticks labels
    ax.set_xticklabels('')
    # Create minor ticks and labels
    # Display the labels at MINOR ticks spaced between the bars
    minor_locations = [mposs[i] + 0.5*(mposs[i+1]-mposs[i]) for i in range(len(mposs)-1)]
    ax.xaxis.set_minor_locator(FixedLocator(minor_locations))
    ax.xaxis.set_minor_formatter(FixedFormatter(bin_labels))
    # Now actually hide the minor ticks but leave the labels
    ax.tick_params(axis='x', which='minor', length=0, labelsize=10)

    shown = ['All Days', 'Weekends', 'Mondays'][j]
    cs = ['k', 'g', 'b'][j]
    ax.annotate(s=shown, xy =(0.10,0.90), fontsize=20, alpha=0.6,
                        xycoords='axes fraction', verticalalignment='top',
                        horizontalalignment='left' , rotation = 0, color=cs)
    ax.annotate(s='u/tigeer', xy =(0.9,0.05), fontsize=8, alpha=0.6,
                        xycoords='axes fraction', verticalalignment='top',
                        horizontalalignment='left' , rotation = 0, color='k')

    plt.title("How happy were redditors \non each day of 2019?", fontsize=18)
    plt.ylabel("Average Happiness /10")
    plt.xlabel("Month")
    #plt.legend()

ani = animation.FuncAnimation(fig, animate, frames=list(range(3))*6, interval=3000, repeat_delay=0)
#ani.save(dir + "mood.mp4")
plt.show()


# with open(dir + 'normed_mood.csv', 'w') as csvFile:
#         writer = csv.writer(csvFile, delimiter=',')
#         writer.writerows([[k for k in data]] + list(np.transpose(np.array(normed))))
#
# print("Saved csv @ %s" % dir + 'normed_mood.csv')
