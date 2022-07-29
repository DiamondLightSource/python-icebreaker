import argparse

from icebreaker import ice_groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--star",
        help="Star file containing particles",
        dest="instar",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Directory containing micrographs pointed to in the input star file",
        dest="indir",
    )
    args = parser.parse_args()

    ice_groups.main(args.instar, args.indir)
