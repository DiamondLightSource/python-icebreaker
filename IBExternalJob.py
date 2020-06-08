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
import shutil

import gemmi



def run_job(project_dir, job_dir, args_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_star", help="Input: Motion correction star file")
    args = parser.parse_args(args_list)
    starfile = args.in_star

    # Reading the micrographs star file from relion
    in_doc = gemmi.cif.read_file(os.path.join(project_dir, starfile))

    data_as_dict = json.loads(in_doc.as_json())['micrographs']

    try:
        os.mkdir('IB_input')
    except FileExistsError:
        # Not crucial so if fails due to any reason just carry on
        try:
            with open('done_mics.txt', 'a+') as f:  # Done mics is to ensure that cryolo doesn't pick from already done mics
                for micrograph in os.listdir('cryolo_input'):
                    f.write(micrograph + '\n')
        except: pass  # occurs if on first pass
        shutil.rmtree('cryolo_input')
        os.mkdir('cryolo_input')

    # Arranging files for cryolo to predict particles from
    # Not crucial so if fails due to any reason just carry on
    try:
        with open('done_mics.txt', 'r') as f:
            done_mics = f.read().splitlines()
    except: done_mics = []
    for micrograph in data_as_dict['_rlnmicrographname']:
        if os.path.split(micrograph)[-1] not in done_mics:
            os.link(os.path.join(project_dir, micrograph),
                    os.path.join(project_dir, job_dir, 'cryolo_input',
                                 os.path.split(micrograph)[-1]))

    # XXX Run IB on IB_input

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
