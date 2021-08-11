#!/usr/bin/env python

import argparse
import os
from pathlib import Path
import shutil

def clean_author(names):
    def multiple(names): return " and " in names

    first_surname = names.split(",")[0].strip() if "," in names else names.strip()
    if multiple(names): 
        return first_surname+" et al"
    return first_surname

def clean_title(title):
    return re.sub(r'[^A-Za-z0-9 -]+', '', title).strip()[:40].strip()

def main(csv_filename):
    with open(csv_filename, encoding='utf-8') as csv_file:
        csv = csv_file.readlines()

    old_cwd = os.getcwd()
    p = Path(csv_filename)
    os.chdir(p.parent.absolute())

    for line in csv[1:]:
        _, _, _, filename, count = line.split(";")
        count = int(count)
        if filename:
            new_path = ""
            if count == -2:
                if not Path("text-not-found/").exists():
                    os.mkdir("text-not-found/")
                new_path = Path("text-not-found/").joinpath(Path(filename).name)
            elif count == -1:
                if not Path("sanity-check/").exists():
                    os.mkdir("sanity-check/")
                new_path = Path("sanity-check/").joinpath(Path(filename).name)
            elif count >= 10:
                if not Path("keywords/").exists():
                    os.mkdir("keywords/")
                new_path = Path("keywords/").joinpath(Path(filename).name)
            if new_path:
                shutil.copyfile(filename, new_path)

    os.chdir(old_cwd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CSV to read."
    )
    parser.add_argument(
        'csv',
        metavar='CSV input',
        type=str,
        help='CSV input filename'
    )
    args = parser.parse_args()
    main(csv_filename=args.csv)
