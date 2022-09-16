import collections
import sys
import os
import mrcfile
import numpy as np

import gemmi
import json

from icebreaker import star_appender


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def main(starfile, mic_path):

    in_doc = gemmi.cif.read_file(starfile)
    data_as_dict = json.loads(in_doc.as_json())["particles"]

    micrographs_used = data_as_dict["_rlnmicrographname"]
    # print(micrographs_used)
    micrographs_unique = list(set(micrographs_used))
    micrographs_unique.sort()
    num_mics = len(micrographs_unique)

    mic_coord = collections.OrderedDict()
    for mic in micrographs_unique:
        mic_coord[mic] = [i for i, e in enumerate(micrographs_used) if e == mic]

    ice_groups = []
    for k in range(num_mics):
        print(f"{k+1} / {num_mics}")
        mic = micrographs_unique[k]
        # print(mic)
        # im_path = os.path.join(mic_path, os.path.split(
        #         mic[:-4])[2:] + '_grouped.mrc')
        split_path = splitall(mic[:-4] + "_grouped.mrc")
        # print(split_path)
        # im_path = os.path.join(mic_path, *split_path)
        # print(im_path)
        mic_path_new = os.path.dirname(mic_path)
        im_path2 = os.path.join(mic_path_new, *split_path)
        # print(im_path2)
        with mrcfile.open(im_path2, "r+", permissive=True) as mrc:
            micro_now = mrc.data

        for part_ind in mic_coord[mic]:
            x1 = int(np.floor(data_as_dict["_rlncoordinatex"][part_ind]))
            y1 = int(np.floor(data_as_dict["_rlncoordinatey"][part_ind]))
            try:
                ice_groups.append(int(micro_now[y1][x1] * 10000))
            except ValueError:
                print(f"warning, unable to append thickness value for particle at {x1= }, {y1= } in micrograph {mic}")
                print(f"assigning -1 as icethickness value for this particle")
                ice_groups.append(-1)

    star_appender.update_star(starfile, ice_groups)

    return True


if __name__ == "__main__":
    starfile = sys.argv[1]
    mic_path = sys.argv[2]
    main(starfile, mic_path)
