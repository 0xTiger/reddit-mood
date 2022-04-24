import csv
import json
import argparse
from itertools import product

import matplotlib.pyplot as plt
from skimage import io
from sklearn.neighbors import NearestCentroid


parser = argparse.ArgumentParser()
parser.add_argument('id')
args = parser.parse_args()

""" TODO
# COMMENT CONVERSIONS MADE IN THE LIST 'DAYS'
# INPUT CLRS MANUALLY IN HEX INSTEAD OF RGB
"""

rgb2Hex = lambda c: f'0x{c[0]:02x}{c[1]:02x}{c[2]:02x}'


def categorise(day_colors, colors):
    if not day_colors:
        raise ValueError('No day colors specified')
    if not colors:
        raise ValueError('No colors to choose from specified')
    clf = NearestCentroid()
    clf.fit(colors, range(len(colors)))
    return clf.predict(day_colors)


def traverse_ordered(a, str):
    if str == 'v': key = lambda x: (x[0], x[1])
    elif str == 'h': key = lambda x: (x[1], x[0])
    return sorted(a, key=key)


file = f'mood_diary_imgs/{args.id}.png'
info_file = 'assets/temp.csv'
save_file = 'assets/mood.json'

with open(save_file) as f: 
    orig = json.load(f)

if args.id in orig:
    print(f'WARNING POST {args.id} ALREADY SCRAPED, CURRENT WILL BE OVERWRITTEN')
traversal_order = input("Nodes traversed h or v first (h/v)?:")

img = io.imread(file)

fig, ax = plt.subplots(num=args.id)

bkg_clrs, dis_clrs = [], []
xs, ys = [], []
def onclick(event):
    valid_click = (
        event.button in (1, 3)
        and not event.dblclick 
        and event.xdata is not None 
        and event.ydata is not None
    )
    if not valid_click:
        print(f'Warning: invalid {event}')
        return

    x = int(event.xdata)
    y = int(event.ydata)
    
    if event.button == 1 and event.key is None:
        ax.axhline(y)
        ys.append(y)

    elif event.button == 3 and event.key is None:
        ax.axvline(x)
        xs.append(x)

    elif event.button == 1 and event.key == 'b' : # Picks background colour
        bkg_clrs.append(img[y][x])
        print(f'{bkg_clrs[-1]} added to bkg_clrs')

    elif event.button == 1 and event.key == 'v' : # Picks mood colour
        if x < 0 or y < 0:
            clr = input("Input colour:")
            dis_clrs.append(list(map(int, clr.split(','))))
            print(f'{dis_clrs[-1]} added to dis_clrs')
        else:
            dis_clrs.append(img[y][x])
            print(f'{dis_clrs[-1]} added to dis_clrs')

    plt.show()


fig.canvas.mpl_connect('button_press_event', onclick)

plt.imshow(img)
plt.show()

days = [img[y][x] for x,y in traverse_ordered(product(xs, ys), traversal_order)]
days = categorise(days, bkg_clrs + dis_clrs)
print(days)
len_days_before = len(days)
print(len_days_before)

days = list(filter(lambda x: x >= len(bkg_clrs), days))
days = list(map(lambda x: x - len(bkg_clrs), days))
print(days)
len_days_after = len(days)
print(len_days_after)

with open(info_file, 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['bkg_clrs'] + list(map(rgb2Hex, bkg_clrs)))
        writer.writerow(['dis_clrs'] + list(map(rgb2Hex, dis_clrs)))
        writer.writerow(['len_days_before'] + [len_days_before])
        writer.writerow(['len_days_after'] + [len_days_after])
        writer.writerow(['--------------------------------------'])
        writer.writerows([[v, rgb2Hex(dis_clrs[v])] for v in days])


if input("Save to json (y/n)?:") == 'y':
    orig[args.id] = {'clrs': list(map(rgb2Hex, dis_clrs)), 'data': days}
    with open(save_file, 'w') as o:
        json.dump(orig, o, indent=2)

    print(f"Saved json @ {save_file}")
