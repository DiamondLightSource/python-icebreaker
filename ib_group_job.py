#!/usr/bin/env python
"""
External job for calling IceBreaker grouping within Relion 3.1
in_parts is input star file from relion picking job 
in_mics is previous grouping job directory

Run in main Relion project directory
"""

import argparse
import json
import os
import os.path
import shutil

import gemmi
import sys
sys.path.insert(0, "/dls/ebic/data/staff-scratch/test_ice/relion_wrappers/ICEBREAKER/IBscripts")
sys.path.insert(0, "/home/lexi/Documents/Diamond/ICEBREAKER/IBscripts")
import ice_groups as ib_igroups


def run_job(project_dir, job_dir, args_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_parts", help="Input: particle star file")
    parser.add_argument("--in_mics", help="Input: previous ice_group job")
    args = parser.parse_args(args_list)
    parts_star = args.in_parts
    group_star = os.path.join(project_dir, args.in_mics)

    with open(group_star) as f:
        lines = [line.rstrip() for line in f]
    group_job = lines[1]

    ib_igroups.main(os.path.join(project_dir, parts_star),
                    os.path.join(project_dir, group_job))

    # Writing a star file for Relion
    part_doc = open('ib_icegroups.star', 'w')
    part_doc.write(os.path.join(project_dir, parts_star))
    part_doc.write(os.path.join(project_dir, group_job))
    part_doc.close()

    # Required star file
    out_doc = gemmi.cif.Document()
    output_nodes_block = out_doc.add_new_block('output_nodes')
    loop = output_nodes_block.init_loop('', ['_rlnPipeLineNodeName', '_rlnPipeLineNodeType'])
    loop.add_row([os.path.join(job_dir, 'particles.star'), '5'])
    out_doc.write_file('RELION_OUTPUT_NODES.star')


def main():
    """Change to the job working directory, then call run_job()"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--j", help="relion stuff...")
    parser.add_argument("--pipeline_control", help="relion scheduler stuff...")
    known_args, other_args = parser.parse_known_args()

    project_dir = os.getcwd()
    job_dir = known_args.out_dir
    try:
        os.mkdir(job_dir)
    except FileExistsError: pass
    os.chdir(job_dir)
    try:
        run_job(project_dir, job_dir, other_args)
    except:
        open('RELION_JOB_EXIT_FAILURE', 'w').close()
        raise
    else:
        open('RELION_JOB_EXIT_SUCCESS', 'w').close()


if __name__ == "__main__":
    main()
