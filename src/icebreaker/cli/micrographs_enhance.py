import argparse

from icebreaker import icebreaker_equalize_multi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Directory containing micrographs (MRC files). Output will appear in a new directory called 'flattened' within this directory",
        dest="indir",
    )
    parser.add_argument(
        "-j", help="Number of processes", dest="nproc", type=int, default=1
    )
    args = parser.parse_args()

    icebreaker_equalize_multi.main(args.indir, args.nproc)
