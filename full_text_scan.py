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

import argparse
from pathlib import Path
import os
import re
import textract  # to extract the text from pdf
from unidecode import unidecode


# DEFAULT_KEYWORDS = [
#     " peak ",
#     "-peak",
#     "peak-",
#     "individual frequency",
#     "mean frequency",
#     "dominant frequency",
#     "individual rhythm",
#     "mean rhythm",
#     "dominant rhythm",
#     " paf ",
#     " ipaf ",
#     " apf ",
#     "iapf",
#     " iaf ",
#     " pdr ",
#     " m.d.f. ",
#     " pf ",
#     " abp "
# ]


# Keywords that will be added to the total when they occur
DEFAULT_KEYWORDS = [
    " peak",
    "-peak",
    "peak-",
    "(peak",
    " peak)",
    "\"peak",
    " peak\"",
    "`peak",
    " peak'",
    "individual frequenc",
    "individual alpha frequenc",
    "mean frequenc",
    "mean alpha frequenc",
    "median frequenc",
    "median alpha frequenc"
    "dominant frequenc",
    "dominant alpha frequenc",
    "dominant rhythm",
    "dominant alpha rhythm",
    "paf",
    "ipaf",
    "apf",
    "iapf",
    "iaf",
    "pdr",
    " m.d.f. ",
    " pf ",
    " abp ",
    "iabp",
    "cf",
    "mdf"
]

# Keywords that will be subtracted from the total when they occur
IGNORE_KEYWORDS = [
    "peak power",
    "peak gamma",
    "gamma peak",
    "peak ERD",
    "ERD peak",
    "peak ERS",
    "ERS peak",
    "peak latenc",
    "peak amplitude",
    "peak plasma",
    "peak force",
    "peak velocity",
    "peak response",
    "peak growth",
]
#"negative peak","positive peak",

# Exclude article if these words appear and sum to more than 10
# (code -4 output)
EXCLUDE_MAJOR_KEYWORDS = [
    " poster session",
    " conference abstract",
    " conference schedule",
]

# Exclude article if one of these words appear and sum to more than 100
# (code -3 output)
EXCLUDE_MINOR_KEYWORDS = [
    " poster ",
    " abstract",
    " annual conference",
    " conference preceedings",
]


class Article:
    """An article, as defined in a bibtex file."""
    def __init__(
            self, raw_data, *,
            keywords=None, ignore_keywords=None,
            exclude_major_keywords=None, exclude_minor_keywords=None,
    ):
        """An article is instantiated from the contents of a bibtex file."""
        self.__raw_data = raw_data
        self.keywords = keywords if keywords is not None else []
        if ignore_keywords is not None:
            self.ignore_keywords = ignore_keywords
        else:
            self.ignore_keywords = []
        if exclude_major_keywords is not None:
            self.exclude_major_keywords = exclude_major_keywords
        else:
            self.exclude_major_keywords = []
        if exclude_minor_keywords is not None:
            self.exclude_minor_keywords = exclude_minor_keywords
        else:
            self.exclude_minor_keywords = []
        self.__author = None
        self.__title = None
        self.__year = None
        self.__filename = None
        self.__text = None
        self.__sanitized_text = None
        self.__keywords_count = None

        # self.text # Initialise getting the text

    @property
    def author(self):
        """Author of the article."""
        def get_author(text):
            try:
                return re.search(
                    r"(?<=author = {).+?(?=},)",
                    text
                ).group(0).strip().replace("\n", " ").replace(";", ",")
            except:
                return ""
        if self.__author is None:
            self.__author = get_author(self.__raw_data)
        return self.__author

    @property
    def title(self):
        """Title of the article."""
        def get_title(text):
            try:
                return (
                    re.search(
                        r"(?<=title = {).+?(?=},)",
                        text
                    ).group(0)
                    .strip()
                    .replace("\n", " ")
                    .replace(";", ",")
                    .replace("\"", "")
                    .replace("'", "")
                    .replace("{", "")
                    .replace("}", "")
                )
            except:
                return ""
        if self.__title is None:
            self.__title = get_title(self.__raw_data)
        return self.__title

    @property
    def year(self):
        """Year the article was published. If unknown, 0."""
        def get_year(text):
            try:
                if "year = {" in text:
                    return int(
                        re.search(
                            r"(?<=year = {).+?(?=})", text
                        ).group(0).strip()
                    )
                elif "date = {" in text:
                    return int(
                        re.search(
                            r"(?<=date = {).+?(?=})", text
                        ).group(0).strip()[:4]
                    )
            except:
                return 0
        if self.__year is None:
            self.__year = get_year(self.__raw_data)
        return self.__year

    @property
    def filename(self):
        """Returns the filename of the attachment. If multiple attachments,
        it returns the filename of the first attachment.
        """
        def get_filename(text):
            try:
                filename = re.search(
                    r"(?<=file = {).+?(?=},)",
                    text
                ).group(0)
                filename = filename.split(":")[1]
                return filename
            except:
                return ""
        if self.__filename is None:
            self.__filename = get_filename(self.__raw_data)
        return self.__filename

    @filename.setter
    def filename(self, new_filename):
        """Make sure the filename is a string."""
        if isinstance(new_filename, str):
            if new_filename.endswith(".pdf"):
                self.__filename = new_filename
            else:
                raise ValueError("Currently only PDFs are supported.")
        else:
            raise TypeError("A filename should be a string.")

    @property
    def text(self):
        """The text from the attachment."""
        def get_text(filename):
            try:
                return textract.process(
                    filename, method="pdftotext"
                ).decode("utf-8")
            except Exception:
                return ""
        if self.__text is None:
            self.__text = get_text(self.filename)
        return self.__text

    @property
    def sanitized_text(self):
        """Sanitize the text for the computer."""
        def sanitize_text(text):
            """Remove newlines and set all of the text to lowercase."""
            return unidecode(text).replace("\n", " ").lower()
        if self.__sanitized_text is None:
            self.__sanitized_text = sanitize_text(self.text)
        return self.__sanitized_text

    @property
    def keywords_count(self):
        """How many instances of keywords appear in the text?"""
        def get_kw_count(text, keywords):
            return sum([
                text.count(keyword) for keyword in keywords
            ])

        def sanity_check(text):
            return get_kw_count(text, [" the ", " a "]) >= 10

        if self.__keywords_count is None:
            if get_kw_count(
                self.sanitized_text, self.exclude_major_keywords
            ) >= 10:
                self.__keywords_count = -4
            elif get_kw_count(
                self.sanitized_text, self.exclude_minor_keywords
            ) >= 100:
                self.__keywords_count = -3
            else:
                self.__keywords_count = get_kw_count(
                    self.sanitized_text, self.keywords
                ) - get_kw_count(
                    self.sanitized_text, self.ignore_keywords
                )
                if self.__keywords_count == 0:
                    if self.text == "":
                        self.__keywords_count = -2
                    elif not sanity_check(self.sanitized_text):
                        self.__keywords_count = -1
        return self.__keywords_count

    def as_markdown(self):
        """Output in a markdown format, showing all sentences that include
        keywords.
        """
        def keyword_sentences(text, keywords):
            def is_highlight(line, keyword):
                """Determine if there's a keyword to be highlighted in the
                line.
                """
                line = line.replace("**"+keyword.lower()+"**", "").lower()
                if keyword in line:
                    return True
                else:
                    False

            def highlight(line, keyword):
                def add_highlight(line, start, end):
                    return "".join([
                        line[:start],
                        "**", line[start:end], "**",
                        line[end:]
                    ])

                for _ in range(line.lower().count(keyword)):
                    start = line.lower().index(keyword.lstrip())
                    end = start + len(keyword.strip())
                    try:
                        if line[start-2:start] != "**":
                            line = add_highlight(line, start, end)
                    except IndexError:
                        line = add_highlight(line, start, end)
                return line

            sentences = ""
            for line in text.split("\n"):
                add_line = False
                line_to_add = line
                for keyword in keywords:
                    if is_highlight(line_to_add, keyword):
                        add_line = True
                        line_to_add = highlight(line_to_add, keyword)
                if add_line:
                    sentences += line_to_add+"\n\n"
            return sentences

        return (
            f"# Title: {self.title}\n"
            f"**Author:** {self.author}\n"
            f"**Year:** {self.year}\n"
            f"**Filename:** {self.filename}\n"
            f"**Keywords count:** {self.keywords_count}\n\n"
            f"{keyword_sentences(self.text, self.keywords)}\n"
        )

    def as_csv(self):
        return (
            f"{self.title};"
            f"{self.author};"
            f"{self.year};"
            f"{self.filename};"
            f"{self.keywords_count}"
        )

    def as_bibtex(self):
        def replace_filename(self, line):
            if self.filename and "\tfile = {" in line:
                return "\tfile = {Attachment:"+self.filename+":applicaton/pdf},"
            return line
        
        return "\n".join([
            replace_filename(self, line)
            for line in self.__raw_data.split("\n")
        ])+"\n}\n"


def main(bibtex_filename, markdown=None, csv=None):
    def article_sort(article):
        return (
            article.keywords_count,
            article.year,
            article.author,
            article.title
        )

    with open(bibtex_filename, encoding='utf-8') as bibtex_file:
        bib = bibtex_file.read()

    old_cwd = os.getcwd()
    p = Path(bibtex_filename)
    os.chdir(p.parent.absolute())

    articles = sorted(
        [
            Article(
                article,
                keywords=DEFAULT_KEYWORDS,
                ignore_keywords=IGNORE_KEYWORDS,
                exclude_major_keywords=EXCLUDE_MAJOR_KEYWORDS,
                exclude_minor_keywords=EXCLUDE_MINOR_KEYWORDS,
            )
            for article in bib.split("\n}")[:-1]
        ],
        key=article_sort
    )

    os.chdir(old_cwd)

    if markdown:
        with open(markdown, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(
                "\n".join(article.as_markdown() for article in articles)
            )

    if csv:
        with open(csv, "w", encoding="utf-8") as csv_file:
            csv_output = "title;author;year;filename;count\n"
            csv_output += "\n".join(article.as_csv() for article in articles)
            csv_file.write(csv_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search full texts for keywords."
    )
    parser.add_argument(
        'bibtex',
        metavar='BibTeX input',
        type=str,
        help='BibTex input filename'
    )
    parser.add_argument(
        "-m",
        "--markdown",
        help="Markdown output",
        default=None
    )
    parser.add_argument(
        "-c",
        "--csv",
        help="CSV output",
        default=None
    )
    args = parser.parse_args()
    main(bibtex_filename=args.bibtex, markdown=args.markdown, csv=args.csv)
