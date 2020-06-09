import collections
import sys
import os
# import pandas as pd
import mrcfile
import numpy as np
from itertools import groupby

import gemmi
import json
sys.path.insert(0, "/home/lexi/Documents/Diamond/ICEBREAKER/")
import star_appender


# pd.set_option("display.max_colwidth", 10000)

path_to_star = sys.argv[1]
path_to_micrographs = sys.argv[2]

starfile = path_to_star
full_path = path_to_micrographs

'''
last = 99999999
header = ''
rC = 0
with open(starfile, 'r') as f:
    for num, line in enumerate(f, 1):
        if '_rln' in line:
            last = num

        elif(num > last):
            break
        header += line
        if 'MicrographName' in line:
            micro_name = [int(''.join(s)) for is_digit,
                          s in groupby(line, str.isdigit) if is_digit]

        if 'CoordinateX' in line:
            coord_X = [int(''.join(s)) for is_digit,
                       s in groupby(line, str.isdigit) if is_digit]

        if 'CoordinateY' in line:
            coord_Y = [int(''.join(s)) for is_digit,
                       s in groupby(line, str.isdigit) if is_digit]

        if '_rln' in line:
            rC += 1

d1 = pd.read_csv(starfile, sep='\s+', skiprows=last, header=None)

micrographs_used = (d1[:][micro_name[0]-1].unique())
'''

in_doc = gemmi.cif.read_file(starfile)
data_as_dict = json.loads(in_doc.as_json())['particles']

micrographs_used = data_as_dict['_rlnmicrographname']
micrographs_unique = list(set(micrographs_used))
num_mics = len(micrographs_unique)

# mic_coord = collections.OrderedDict()
# for i in range(num_mics):
#     mic_coord[str(micrographs_used[i])] = (d1.loc[d1[micro_name[0]-1] == str(
#             micrographs_used[i])].index[:]).tolist()

# Get all indices of particles from given micrograph
mic_coord = collections.OrderedDict()
for mic in micrographs_unique:
    mic_coord[mic] = [i for i, e in enumerate(micrographs_used) if e == mic]
print(mic_coord)

ice_groups = []
for k in range(num_mics):
    print(f'{k} / {num_mics}')
    mic = micrographs_unique[k]
    im_path = os.path.join(full_path, os.path.split(
            mic[:-4])[-1] + '_grouped.mrc')

    with mrcfile.open(im_path, 'r+', permissive=True) as mrc:  #! change to right path and patch size
        micro_now = mrc.data

    for part_ind in mic_coord[mic]:
        x1 = int(np.floor(data_as_dict['_rlncoordinatex'][part_ind]))
        y1 = int(np.floor(data_as_dict['_rlncoordinatey'][part_ind]))
        if micro_now is not None:
            ice_groups.append(int(micro_now[y1][x1]*10000))
        else:
            ice_groups.append(-1)

star_appender.update_star(starfile, ice_groups)

'''
header += '_rlnHelicalTubeID #'+str(rC+1)+'\n'  # change number
d2 = pd.DataFrame({'_rlnHelicalTubeID': ice_groups})   # Does this make sense?? - assuming order is correct...

result = pd.concat([d1, d2], axis=1, sort=False)
result = result.to_string(header=None, index=None)
with open(starfile[:-5] + '_icegroups_from_original_mean_scaled.star', 'w') as fd:
    fd.write(header)
    fd.write(result)
'''
