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

from icebreaker import five_figures


def run_job(project_dir, job_dir, args_list, cpus):
    parser = argparse.ArgumentParser()
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--in_mics", help="Input: IB_grouped star file")
    input_group.add_argument("--single_mic", help="A single IB_grouped micrograph")
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
            micpath = pathlib.Path(micrograph)
            link_path = pathlib.Path("IB_input") / pathlib.Path(
                *list(micpath.parent.parts)[2:]
            )
            if not link_path.exists():
                link_path.mkdir(parents=True)
            try:
                (pathlib.Path("IB_input") / pathlib.Path(micrograph).name).symlink_to(
                    pathlib.Path(project_dir) / micrograph
                )
            except FileExistsError:
                print(
                    f"WARNING: IB_input/{os.path.split(micrograph)[-1]} "
                    "already exists but is not in the done micrographs"
                )

    if args.single_mic:
        five_fig_csv = five_figures.single_mic_5fig(
            pathlib.Path(project_dir)
            / job_dir
            / "IB_input"
            / pathlib.Path(args.single_mic).name
        )
        summary_results = five_fig_csv.split(",")
        print("Results: " + " ".join(summary_results))
    else:
        five_fig_csv = five_figures.main(
            pathlib.Path(project_dir) / job_dir / "IB_input", cpus, append=True
        )
    print("Done five figures")

    if args.in_mics:
        with open(
            "done_mics.txt", "a+"
        ) as f:  # Done mics is to ensure that IB doesn't pick from already done mics
            for micrograph in pathlib.Path("./IB_input").glob("**/*"):
                if micrograph.suffix == ".mrc":
                    f.write(micrograph.name + "\n")

    # Required star file
    out_doc = gemmi.cif.Document()
    output_nodes_block = out_doc.add_new_block("output_nodes")
    loop = output_nodes_block.init_loop(
        "", ["_rlnPipeLineNodeName", "_rlnPipeLineNodeType"]
    )
    # loop.add_row([os.path.join(job_dir, 'ib_equalize.star'), '1'])
    loop.add_row([os.path.join(job_dir, "five_figs_test.csv"), "1"])
    out_doc.write_file("RELION_OUTPUT_NODES.star")


def main():
    """Change to the job working directory, then call run_job()"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--j", help="relion stuff...", type=int)
    parser.add_argument("--pipeline_control", help="relion scheduler stuff...")
    known_args, other_args = parser.parse_known_args()

    project_dir = os.getcwd()
    job_dir = known_args.out_dir
    try:
        os.mkdir(job_dir)
    except FileExistsError:
        pass
    os.chdir(job_dir)
    try:
        run_job(project_dir, job_dir, other_args, known_args.j)
    except Exception:
        open("RELION_JOB_EXIT_FAILURE", "w").close()
        raise
    else:
        open("RELION_JOB_EXIT_SUCCESS", "w").close()


if __name__ == "__main__":
    main()
