import sys
from multiprocessing import Lock, Manager, Pool
from pathlib import Path

import mrcfile
import numpy as np


def single_mic_5fig(mic_name: str, r: int = 10000) -> str:
    with mrcfile.open(mic_name, "r", permissive=True) as mrc:
        img = mrc.data
        if not np.isnan(np.sum(img)):
            min = int(np.min(img) * r)
            q1 = int(np.quantile(img, 0.25) * r)
            median = int(np.median(img) * r)
            q3 = int(np.quantile(img, 0.75) * r)
            max = int(np.max(img) * r)
            csv_lines = f"{mic_name},{min},{q1},{median},{q3},{max}"
        else:
            csv_lines = ""
    return csv_lines


def _process_mrc(img_path: str, csv_lines: list, lock: Lock, r: int) -> None:
    with mrcfile.open(img_path, "r", permissive=True) as mrc:
        img = mrc.data
        if not np.isnan(np.sum(img)):
            path = img_path[:-4]
            min = int(np.min(img) * r)
            q1 = int(np.quantile(img, 0.25) * r)
            median = int(np.median(img) * r)
            q3 = int(np.quantile(img, 0.75) * r)
            max = int(np.max(img) * r)
            lock.acquire()
            csv_lines.append(f"{path},{min},{q1},{median},{q3},{max}\n")
            lock.release()
    return None


def main(grouped_mic_dir: str, cpus: int = 1, append: bool = False) -> list:
    manager = Manager()
    lock = manager.Lock()
    files = [str(filename) for filename in Path(grouped_mic_dir).glob("**/*.mrc")]
    r = 10000

    csv_lines = manager.list()
    with Pool(cpus) as p:
        p.starmap(_process_mrc, [(fl, csv_lines, lock, r) for fl in sorted(files)])
    if append and Path("five_figs_test.csv").is_file():
        with open("five_figs_test.csv", "a+") as f:
            for line in csv_lines:
                f.write(line)
    else:
        with open("five_figs_test.csv", "w") as f:
            f.write("path,min,q1,q2=median,q3,max\n")
            for line in csv_lines:
                f.write(line)
    return csv_lines


if __name__ == "__main__":
    grouped_mic_dir = sys.argv[1]
    main(grouped_mic_dir)
