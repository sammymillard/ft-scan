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

DEFAULT_KEYWORDS = [
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

class Article:
    def __init__(self, raw_data, keywords=None):
        self.__raw_data = raw_data
        self.keywords = keywords if keywords is not None else []
        self.__author = None
        self.__title = None
        self.__year = None
        self.__filename = None
        self.__text = None
        self.__sanitized_text = None
        self.__keywords_count = None

    @property
    def author(self):
        def get_author(text):
            try:
                return re.search(
                    r"(?<=author = \{).+?(?=\},)",
                    text
                ).group(0).strip().replace("\n", " ").replace(";", ",")
            except:
                return ""
        if self.__author is None:
            self.__author = get_author(self.__raw_data)
        return self.__author

    @property
    def title(self):
        def get_title(text):
            try:
                return re.search(
                    r"(?<=title = \{).+?(?=\},)",
                    text
                ).group(0).
                strip().
                replace("\n", " ").
                replace(";",",").
                replace("\"","").
                replace("'", "").
                replace("{","").
                replace("}","")
            except:
                return ""
        if self.__title is None:
            self.__title = get_title(self.__raw_data)
        return self.__title

    @property
    def year(self):
        def get_year(text):
            try:
                return int(
                    re.search(
                        r"(?<=year = \{).+?(?=\},)", text
                    ).group(0).strip()
                )
            except:
                return 0
        if self.__year is None:
            self.__year = get_year(self.__raw_data)
        return self.__year

    @property
    def filename(self):
        def get_filename(text):
            try:
                return re.search(
                    r"(?<=file = \{).+?(?=\},)",
                    text
                ).group(0)
            except:
                return ""
        if self.__filename is None:
            self.__filename = get_filename(self.__raw_data)
        return self.__filename

    @property
    def text(self):
        def get_text(filename):
            try:
                return textract.process(
                    filename, method="pdftotext"
                ).decode("utf-8")
            except Exception:
                return ""
        if self.__text is None:
            self.__text = get_text(self.__filename)
        return self.__text

    @property
    def sanitized_text(self):
        def sanitize_text(text):
            """Remove newlines and set all of the text to lowercase."""
            return text.replace("\n", " ").lower()
        if self.__sanitized_text is None:
            self.__sanitized_text = sanitize_text(self.text)
        return self.__sanitized_text

    @property
    def keywords_count(self):
        if self.__keywords_count is None:
            self.__keywords_count = sum([
                self.text.count(keyword) for keyword in self.keywords
            ])
        return self.__keywords_count

    def as_markdown(self):
        def keyword_sentences(text, keywords):
            def highlight(line, keyword):
                return (
                    line[:line.index(keyword)]+
                    "**"+keyword+"**"+
                    line[line.index(keyword)+len(keyword):]
                )
            sentences = ""
            for line in text.split("\n"):
                for keyword in keywords:
                    if keyword in line.lower():
                        sentences+=highlight(line, keyword)
                        break
            return sentences

        return (
            f"# Title: {self.title}\n"
            f"## Author: {self.author}\n"
            f"## Year: {self.year}\n"
            f"## Filename: {self.filename}\n"
            f"## Keywords count: {self.keywords_count}\n\n"
            f"{self.keyword_sentences}\n"
        )


def main(bibtex_filename):
    def article_sort(article):
        return (
            article.keywords_count(DEFAULT_KEYWORDS),
            article.year,
            article.author,
            article.title
        )

    with open(bibtex_filename) as bibtex_file:
        bib = bibtex_file.read()

    articles = sorted(
        [
            Article(article, keywords=DEFAULT_KEYWORDS)
            for article in bib.split("\n}\n")[:-1]
        ],
        key=article_sort
    )

    print("\n".join(article.as_markdown() for article in articles))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit("Please give the path to a bibtex file.")
    main(bibtex_filename=sys.argv[1])
