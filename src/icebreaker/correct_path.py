"""
Creates a folder tree that is the relion standard and then populates folder tree with the flattened micrographs produced by ICEBREAKER
"""
import gemmi
import os
import json
import pathlib
import shutil


def correct(ctf_star, all_dir, ending):
    in_doc = gemmi.cif.read_file(ctf_star)
    data_as_dict = json.loads(in_doc.as_json())["micrographs"]

    for i in range(len(data_as_dict["_rlnmicrographname"])):
        name = data_as_dict["_rlnmicrographname"][i]
        dirs, mic_file = os.path.split(name)
        #outdir = pathlib.Path(name).parts
        # print(x[-2])
        xhead, xtail = os.path.split(name)
        # print(xhead)
        full_dir = xhead  # outdir[-2] #'Movies'
        # full_dir=os.path.join(x[2],
        # for d in dirs.split('/'):
        #    full_dir = os.path.join(full_dir, d)
        #    print(d)
        pathlib.Path(full_dir).mkdir(parents=True, exist_ok=True)
        picked_star = os.path.splitext(mic_file)[0] + f"_{ending}.mrc"
        if os.path.isfile(os.path.join(all_dir, picked_star)):
            try:
                shutil.move(
                    os.path.join(all_dir, picked_star),
                    os.path.join(full_dir, picked_star),
                )
            except FileNotFoundError:
                print("Warning - Flattened Mic not found (Most likely already moved)")
                pass
