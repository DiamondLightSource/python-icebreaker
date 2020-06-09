import collections
import sys
import os
import mrcfile
import numpy as np

import gemmi
import json
sys.path.insert(0, "/home/lexi/Documents/Diamond/ICEBREAKER/")
import star_appender


def main(starfile, mic_path):

    in_doc = gemmi.cif.read_file(starfile)
    data_as_dict = json.loads(in_doc.as_json())['particles']

    micrographs_used = data_as_dict['_rlnmicrographname']
    micrographs_unique = list(set(micrographs_used))
    num_mics = len(micrographs_unique)

    mic_coord = collections.OrderedDict()
    for mic in micrographs_unique:
        mic_coord[mic] = [i for i, e in enumerate(micrographs_used)
                          if e == mic]
    print(mic_coord)

    ice_groups = []
    for k in range(num_mics):
        print(f'{k} / {num_mics}')
        mic = micrographs_unique[k]
        im_path = os.path.join(mic_path, os.path.split(
                mic[:-4])[-1] + '_grouped.mrc')

        with mrcfile.open(im_path, 'r+', permissive=True) as mrc:
            micro_now = mrc.data

        for part_ind in mic_coord[mic]:
            x1 = int(np.floor(data_as_dict['_rlncoordinatex'][part_ind]))
            y1 = int(np.floor(data_as_dict['_rlncoordinatey'][part_ind]))
            if micro_now is not None:
                ice_groups.append(int(micro_now[y1][x1]*10000))
            else:
                ice_groups.append(-1)

    star_appender.update_star(starfile, ice_groups)

    return True


if __name__ == '__main__':
    starfile = sys.argv[1]
    mic_path = sys.argv[2]
    main(starfile, mic_path)
