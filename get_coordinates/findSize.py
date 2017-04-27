#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image
import json

coordinates = json.load(open('coordinates.json'))
h = coordinates['abs_size']['height']
w = coordinates['abs_size']['width']
ratio = w / float(h)
print 'original size: {}, {}'.format(w, h)

station2pixel = {}

# reduce width of the image as long as there occurs a pixel
# that would belong to two stations
current_result = None
got_double = False

while w > 0 and not got_double:
    next_result = np.zeros((w, h), dtype=np.uint8)
    next_mapping = {}
    for s in coordinates['relative']:
        x = int(coordinates['relative'][s]['x'] * w)
        y = int(coordinates['relative'][s]['y'] * h)
        if next_result[x, y] > 0:
            got_double = True
            break
        else:
            next_result[x, y] = 1
            next_mapping[s] = [x, y]
    if not got_double:
        current_result = next_result
        station2pixel = next_mapping
        print '\roptimizing width: h {}, w {}'.format(h, w),
    w -= 1
print

# reduce height of the image as long as there occurs a pixel
# that would belong to two stations
got_double = False
while(h > 0 and not got_double):
    next_result = np.zeros((w, h), dtype=np.uint8)
    next_mapping = {}
    for s in coordinates['relative']:
        x = int(coordinates['relative'][s]['x'] * w)
        y = int(coordinates['relative'][s]['y'] * h)
        if next_result[x, y] > 0:
            got_double = True
        else:
            next_result[x, y] = 1
            next_mapping[s] = [x, y]
    if not got_double:
        current_result = next_result
        station2pixel = next_mapping
        print '\roptimizing height: h {}, w {}'.format(h, w),
    h -= 1

print
print 'reduced to', current_result.shape

# getting rid of empty rows
print 'removing empty rows'
non_empty_rows = []
reduce_counter = 0
for row in range(current_result.shape[1]):
    stations_of_row = [s for s in station2pixel if station2pixel[s][1] > (row - reduce_counter)]
    if current_result[:, row].sum() > 0:
        non_empty_rows.append(row)
    else:
        reduce_counter += 1
        for s in stations_of_row:
            station2pixel[s][1] -= 1

new_result = np.array(current_result[:, non_empty_rows])
print 'reduced to', new_result.shape

# getting rid of empty columns
print 'removing empty columns'
non_empty_cols = []
reduce_counter = 0
for col in range(new_result.shape[0]):
    stations_of_col = [s for s in station2pixel if station2pixel[s][0] > (col - reduce_counter)]
    if new_result[col, :].sum() > 0:
        non_empty_cols.append(col)
    else:
        reduce_counter += 1
        for s in stations_of_col:
            station2pixel[s][0] -= 1

very_new_result = np.array(new_result[non_empty_cols, :])
print 'reduced to', very_new_result.shape

# reduced width and hight so that each pixel at most belongs to one station
# the spatial relations should retained
print 'should be {} stations / white pixel'.format(len(coordinates['relative'].keys()))
# print ' ' + '_' * (2 * very_new_result.shape[0] - 1)
# for y in range(very_new_result.shape[1]):
#     print '|' + '|'.join([u"\u2588" if very_new_result[x, y] == 1 else '_' for x in range(very_new_result.shape[0])]) + '|'

print 'building mappings'
pixel2station = {}
for s in station2pixel:
    if station2pixel[s][0] not in pixel2station:
        pixel2station[station2pixel[s][0]] = {}
    pixel2station[station2pixel[s][0]][station2pixel[s][1]] = s

json.dump(pixel2station, open('pixel2station.json', 'w'), indent=2)
json.dump(station2pixel, open('station2pixel.json', 'w'), indent=2)
Image.fromarray(very_new_result.T * 255).save('input.png')
