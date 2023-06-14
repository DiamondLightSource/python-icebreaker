import argparse

from icebreaker import five_figures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Directory containing grouped micrographs",
        dest="indir",
    )
    parser.add_argument(
        "-j", help="Number of processes", dest="nproc", type=int, default=1
    )
    args = parser.parse_args()

    five_figures.main(args.indir, cpus=args.nproc)
