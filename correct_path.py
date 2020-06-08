'''
Creates a folder tree that is the relion standard and then populates folder tree with the flattened micrographs produced by ICEBREAKER
'''
import gemmi
import os
import json
import pathlib
import shutil


def correct(ctf_star, all_dir):
    in_doc = gemmi.cif.read_file(ctf_star)
    data_as_dict = json.loads(in_doc.as_json())['micrographs']

    for i in range(len(data_as_dict['_rlnmicrographname'])):
        name = data_as_dict['_rlnmicrographname'][i]
        dirs, mic_file = os.path.split(name)
        full_dir = ''
        for d in dirs.split('/')[2:]:
            full_dir = os.path.join(full_dir, d)
        pathlib.Path(full_dir).mkdir(parents=True, exist_ok=True)
        picked_star = os.path.splitext(mic_file)[0] + '_flattened.mrc'
        try:
            shutil.move(os.path.join(all_dir, picked_star),
                        os.path.join(full_dir, picked_star))
        except FileNotFoundError:
            pass
            # print(f"Warning - Flattened Mic not found (Most likely already moved)")
            # Dont fail as this is often the case when iterating
