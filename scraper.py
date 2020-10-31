import numpy as np
import csv
import json
import matplotlib.pyplot as plt
from itertools import product
from skimage import io
from sklearn.neighbors import NearestCentroid
""" TODO
# FIX QCoreApplication::exec: The event loop is already running?
# COMMENT CONVERSIONS MADE IN THE LIST 'DAYS'
# INPUT CLRS MANUALLY IN HEX INSTEAD OF RGB
"""


strHex = lambda x: "%0.2x" % x
rgb2Hex = lambda c: '0x' + strHex(c[0]) + strHex(c[1]) + strHex(c[2])

def categorise(x, a):
    labels=range(len(a))
    clf = NearestCentroid()
    clf.fit(a, labels)
    return clf.predict(x)

def trav_ord(a, str):
    if str == 'v':
        a = sorted(a, key = lambda x: (x[0], x[1]))
    elif str == 'h':
        a = sorted(a, key = lambda x: (x[1], x[0]))
    return a

id = 'ei7r4y'

file = 'mood_diary_imgs' + id + '.png'
info_file = 'assets/temp.csv'
save_file = 'assets/mood.json'

with open(save_file) as f: orig = json.load(f)
if id in orig:
    print("WARNING POST ALREADY SCRAPED, CURRENT WILL BE OVERWRITTEN")

img = io.imread(file)

fig = plt.figure(num = id)
ax = fig.add_subplot(111)

bkg_clrs = []
dis_clrs = []
xs, ys = [], []
def onclick(event):
    valid_click = fig.canvas.manager.toolbar._active is None and event.xdata is not None and event.ydata is not None
    if valid_click:
        if event.dblclick or (event.button != 1 and event.button != 3):
            print('WARNING invalid click MOUSE%d' % event.button)
        else:
            x, y = int(event.xdata), int(event.ydata)

            if event.button == 1 and event.key is None:
                ax.axhline(y)
                ys.append(y)
            elif event.button == 1 and event.key == 'b' :
                bkg_clrs.append(img[y][x])
                print(bkg_clrs[-1])
            elif event.button == 1 and event.key == 'v' :
                if x < 0 or y < 0:
                    clr = input("Input clr:")
                    dis_clrs.append(list(map(int, clr.split(','))))
                    print(dis_clrs[-1])
                else:
                    dis_clrs.append(img[y][x])
                    print(dis_clrs[-1])
            elif event.button == 3 and event.key is None:
                ax.axvline(x)
                xs.append(x)

            plt.show()


cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.imshow(img)
t_o = input("Nodes traversed h or v (h/v)?:")
plt.show()

days = [img[y][x] for x,y in trav_ord(product(xs, ys), t_o)]
days = categorise(days, bkg_clrs + dis_clrs )
print(days)
len_days_before = len(days)
print(len_days_before)

days = list(filter(lambda x: x >= len(bkg_clrs), days))
days = list(map(lambda x: x - len(bkg_clrs), days))
print(days)
len_days_after = len(days)
print(len_days_after)

with open(info_file, 'w', newline='\n') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(['bkg_clrs'] + list(map(rgb2Hex, bkg_clrs)))
        writer.writerow(['dis_clrs'] + list(map(rgb2Hex, dis_clrs)))
        writer.writerow(['len_days_before'] + [len_days_before])
        writer.writerow(['len_days_after'] + [len_days_after])
        writer.writerow(['--------------------------------------'])
        writer.writerows([[v, rgb2Hex(dis_clrs[v])] for v in days])


if input("Save to json (y/n)?:") == 'y':
    orig[id] = {'clrs': list(map(rgb2Hex, dis_clrs)), 'data': days}
    try:
        with open(save_file, 'w') as o:
            json.dump(orig, o, indent=2)

        print("Saved json @ %s" % save_file)
    except:
        print("WARNING FAILED SAVE")
