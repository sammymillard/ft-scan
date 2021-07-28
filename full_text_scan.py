#!/usr/bin/env python

"""Full text scan

Search full texts (as PDFs) for keywords.
"""

# Full text scan - Search full text pdfs for keywords.

# Copyright 2021, Christian Christiansen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "Christian Christiansen"
__copyright__ = "Copyright 2021, Christian Christiansen"

__license__ = "AGPL-3.0"
__version__ = "Development"
__maintainer__ = "Christian Christiansen"
__email__ = "christian dot l dot christiansen at gmail dot com"
__status__ = "Development"

from pathlib import Path # to find pdfs to extract text from
import argparse # to parse command-line arguments when run from the shell
import textract # to extract the text from pdf

default_keywords = [
    " peak ",
    "-peak",
    "peak-",
    "individual frequency",
    "mean frequency",
    "dominant frequency",
    "individual rhythm",
    "mean rhythm",
    "dominant rhythm",
    " paf",
    "ipaf",
    " apf",
    "iapf",
    "iaf",
    "pdr",
    "m.d.f",
    " pf ",
]

def keywords_count(text, keywords):
    """The total number of times keywords appear in a text."""
    return sum([text.count(keyword) for keyword in keywords])

def keyword_threshold(text, keywords, *, threshold=10):
    """Return True if more instances of keywords than threshold, else False."""
    return keywords_count(text, keywords) >= threshold

def sanity_check(text, *, check_threshold=10, checks=None):
    """Ensure the text behaves as expected."""
    if checks is None:
        checks = [" the ", " a "]
    return keyword_threshold(text, keywords=checks, threshold=check_threshold)

def sanitize_text(text):
    """Remove newlines and set all of the text to lowercase."""
    return text.replace("\n", " ").lower()

def full_text_scan(
        filename, *,
        language="eng", keywords=None, threshold=10, csv=False
):
    """Extract text from file. If the number of instances of keywords exceeds
    the threshold, output the filename of the file."""
    try:
        text = sanitize_text(
            textract.process(
                filename, method="pdftotext", language=language
            ).decode("utf-8")
        )
    except Exception:
        if csv:
            return f"{filename};-2\n"
        return False
    else:
        if sanity_check(text):
            if not keyword_threshold(
                    text=text, keywords=keywords, threshold=threshold
            ):
                if csv:
                    return (
                        f"{filename};"
                        f"{keywords_count(text, keywords=keywords)}\n"
                    )
                return False
            if csv:
                return f"{filename};{threshold}\n"
            return True
        if csv:
            return f"{filename};-1\n"
        return False

if __name__ == "__main__":
    output_csv = "filename;count\n"

    p = Path("/path/to/files")
    for pdf_filepath in p.rglob('*.pdf'):
        output_csv += full_text_scan(
            str(pdf_filepath), keywords=default_keywords, csv=output_csv
        )

    with open("results.csv", "w") as output_file:
        output_file.write(output_csv)
