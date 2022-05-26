'''
Overlapping note fix for osu!mania. *Not fully tested for long notes*

Simple script will move "overlapping" or duplicate notes to storyboard
if they're found to have the same timing point as another note
in the same column.

Usage: py overlapping_fix.py "<osu file path>"
'''

import sys
import math

chart = sys.argv[1]
overlapped_notes = []
storyboard_samples = []

# Parse notes and key count.
with open(chart, 'r', encoding='utf-8') as f:
    while True:
        line = f.readline()
        if line.startswith('CircleSize:'):
            key_count = int(line.strip().split(':')[1])
            continue
        if line == '[HitObjects]\n':
            notes = f.readlines()
            break

# Create list of dictionaries for key count.
columns = [{} for i in range(key_count)]

# Filter all notes and add them into their designated dict,
# excluding duplicates.
for note in notes:
    x_value = int(note.split(',')[0])
    timing_point = int(note.split(',')[2])
    column_number = math.floor(x_value * key_count / 512)

    if timing_point in columns[column_number]:
        overlapped_notes.append(note)
    else:
        columns[column_number][timing_point] = note

# Convert overlapping notes to storyboard samples.
for note in overlapped_notes:
    isLongNote = False
    timing_point = note.split(',')[2]
    hit_sample = note.split(',')[-1].split(':')

    if (int(hit_sample[0]) > 3):
        isLongNote = True

    if isLongNote:
        storyboard_samples.append(
            'Sample,{},0,"{}",100\n'.format(
                timing_point, hit_sample[5].rstrip()))
    else:
        storyboard_samples.append(
            'Sample,{},0,"{}",100\n'.format(
                timing_point, hit_sample[4].rstrip())
        )

# Open file and overwrite with new data.
with open(chart, 'r+', encoding='utf-8') as f:
    data = f.readlines()

    # Find indices to edit data of file.
    hoIndex = data.index("[HitObjects]\n")
    tpIndex = data.index("[TimingPoints]\n")

    # Remove notes and insert storyboard sounds.
    data = data[:hoIndex+1]
    data = data[:tpIndex] + storyboard_samples + data[tpIndex:]

    # Add filtered notes to [HitObjects]
    for column in columns:
        for note in column.values():
            data.append(note)

    f.seek(0)
    f.write(''.join(data))
    f.truncate()

print(f'Done! Removed {len(overlapped_notes)} overlapping notes.')
