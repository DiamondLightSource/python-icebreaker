"""
Creates a folder tree that is the relion standard and then populates
folder tree with the flattened micrographs produced by ICEBREAKER
"""
import gemmi
import os
import json
import pathlib
import shutil


def correct(data_as_dict, all_dir, ending):
   for i in range(len(data_as_dict["_rlnmicrographname"])):
        name = data_as_dict["_rlnmicrographname"][i]
        # New name needs to be extracted from inputs of form
        # JobName/JobNumber/path/to/file.suffix
        name_parts = list(pathlib.Path(name).parts)
        mic_file = name_parts[-1]
        full_dir = "/".join(name_parts[2:-1])
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
