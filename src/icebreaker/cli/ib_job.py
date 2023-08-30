#!/usr/bin/env python
"""
External job for calling IceBreaker equalize within Relion 3.1
in_star is input star file from relion motion cor

Run in main Relion project directory
external_IBequal.py
"""


import argparse
import json
import os
import os.path
import pathlib

import gemmi

from icebreaker import correct_path
from icebreaker import icebreaker_equalize_multi as ib_equal
from icebreaker import icebreaker_icegroups_multi as ib_group
from icebreaker import star_appender


def run_job(project_dir, job_dir, args_list, mode, cpus):
    parser = argparse.ArgumentParser()
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--in_mics", help="Input: Motion correction star file")
    input_group.add_argument("--single_mic", help="Single motion corrected micrograph")
    args = parser.parse_args(args_list)

    if args.in_mics:
        starfile = args.in_mics

        # Reading the micrographs star file from relion
        ctf_star = os.path.join(project_dir, starfile)
        in_doc = gemmi.cif.read_file(ctf_star)

        data_as_dict = json.loads(in_doc.as_json())["micrographs"]

        # Not crucial so if fails due to any reason just carry on
        try:
            with open("done_mics.txt", "r") as f:
                done_mics = f.read().splitlines()
        except Exception:
            done_mics = []
    else:
        data_as_dict = {"_rlnmicrographname": [args.single_mic]}
        done_mics = []

    pathlib.Path("IB_input").mkdir(exist_ok=True)

    for micrograph in data_as_dict["_rlnmicrographname"]:
        if os.path.split(micrograph)[-1] not in done_mics:
            try:
                (pathlib.Path("IB_input") / pathlib.Path(micrograph).name).symlink_to(
                    pathlib.Path(project_dir) / micrograph
                )
            except FileExistsError:
                print(
                    f"WARNING: IB_input/{os.path.split(micrograph)[-1]} "
                    "already exists but is not in the done micrographs"
                )

    if mode == "group":
        ib_group.main("IB_input", cpus)
        print("Done equalizing")
    elif mode == "flatten":
        ib_equal.main("IB_input", cpus)

    if args.in_mics:
        with open(
            "done_mics.txt", "a+"
        ) as f:  # Done mics is to ensure that IB doesn't pick from already done mics
            for micrograph in os.listdir("IB_input"):
                if micrograph.endswith("mrc"):
                    f.write(micrograph + "\n")

    correct_path.correct(
        data_as_dict, os.path.join("IB_input", f"{mode}ed"), f"{mode}ed"
    )

    # Writing a star file for Relion
    # part_doc = open('ib_equalize.star', 'w')
    # part_doc.write(os.path.join(project_dir, starfile)+'\n')
    # part_doc.write(job_dir)
    # part_doc.close()

    if args.in_mics:
        star_appender.mic_star(ctf_star, job_dir, mode)

    # Required star file
    out_doc = gemmi.cif.Document()
    output_nodes_block = out_doc.add_new_block("output_nodes")
    loop = output_nodes_block.init_loop(
        "", ["_rlnPipeLineNodeName", "_rlnPipeLineNodeType"]
    )
    # loop.add_row([os.path.join(job_dir, 'ib_equalize.star'), '1'])
    loop.add_row([os.path.join(job_dir, f"{mode}ed_micrographs.star"), "1"])
    out_doc.write_file("RELION_OUTPUT_NODES.star")


def main():
    """Change to the job working directory, then call run_job()"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--mode", help="ICEBREAKER mode to run i.e. flatten or group")
    parser.add_argument("--j", help="relion stuff...", type=int)
    parser.add_argument("--pipeline_control", help="relion scheduler stuff...")
    known_args, other_args = parser.parse_known_args()

    cpus = known_args.j
    mode = known_args.mode
    poss_modes = ["group", "flatten"]
    if mode not in poss_modes:
        print("IB ERROR - Mode type not found")
        exit()

    project_dir = os.getcwd()
    job_dir = known_args.out_dir
    try:
        os.mkdir(job_dir)
    except FileExistsError:
        pass
    os.chdir(job_dir)
    try:
        run_job(project_dir, job_dir, other_args, mode, cpus)
    except Exception:
        open("RELION_JOB_EXIT_FAILURE", "w").close()
        raise
    else:
        open("RELION_JOB_EXIT_SUCCESS", "w").close()


if __name__ == "__main__":
    main()
