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
import random
import sys
import shutil
import pathlib
import time

import gemmi

from relion_yolo_it import CorrectPath

def run_job(project_dir, job_dir, args_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_star", help="Input: Motion correction star file")
    args = parser.parse_args(args_list)
    starfile = args.in_star

    # Reading the micrographs star file from relion
    in_doc = gemmi.cif.read_file(os.path.join(project_dir, starfile))

    data_as_dict = json.loads(in_doc.as_json())['micrographs']


    # Writing a star file for Relion
    part_doc = open('ib_equalize.star', 'w')
    part_doc.write(os.path.join(project_dir, args.in_mics))
    part_doc.close()

    # Required star file
    out_doc = gemmi.cif.Document()
    output_nodes_block = out_doc.add_new_block('output_nodes')
    loop = output_nodes_block.init_loop('', ['_rlnPipeLineNodeName', '_rlnPipeLineNodeType'])
    loop.add_row([os.path.join(job_dir, '_manualpick.star'), '2'])
    out_doc.write_file('RELION_OUTPUT_NODES.star')
    ctf_star = os.path.join(project_dir, args.in_mics)
    CorrectPath.correct(ctf_star)


def main():
    """Change to the job working directory, then call run_job()"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    known_args, other_args = parser.parse_known_args()
    project_dir = os.getcwd()
    try:
        os.mkdir(known_args.out_dir)
    except FileExistsError: pass
    os.chdir(known_args.out_dir)
    try:
        run_job(project_dir, known_args.out_dir, other_args)
    except:
        open('RELION_JOB_EXIT_FAILURE', 'w').close()
        raise
    else:
        open('RELION_JOB_EXIT_SUCCESS', 'w').close()


if __name__ == "__main__":
    main()
