# ft-scan
Full text scan
Main objective: Search full-text pdfs for specified keywords.

There were too many articles to screen for the full-text screening phase of the
systematic review, predominant reason being that we don't know whether peak
alpha frequency (PAF) was looked at. Searching the texts for PAF related terms
means that some articles can be dropped before looking at the full text
manually.

To run this code you will need Python and two Python packages:
 - `textract`
 - `unidecode`

You will also need the `full_text_scan.py` code and a folder (e.g. ft-scan_example) containing 1) a bibtex of articles (e.g. ft-scan_example.bib) and 2)
a folder called 'files' with the attached PDFs inside. If you export a collection from Zotero, the format will be correct.

Run with the following command:

```python full_text_scan.py ft-scan_example/ft-scan_example.bib -m ft-scan_example/output_example.md -c csv_result_example.csv```

full_text_scan.py runs through the bibtex, finds the attached pdfs from the files folder, and scans the text for keywords.

The .csv produced contains the article title, author, year, and file location,
as well as keyword count number
- Default keywords are summed to produce a total of their occurrences, ignore
  words are summed and subtracted from this total.
- Files that do not pass a sanity check for readability (i.e. file does not
  contain >=10 occurrences of the words "the" and "a") are given a count of -1.
- Files that cannot be found or opened are given a code of -2.
- Files that include >=100 minor exclusion words are given a code of -3.
- Files that include >=10 major exclusion words are given a code of -4.

The .md file can be opened with a text editor or reader (e.g., Mark Text). The
.md file displays the key words found in each article with the surrounding
text. These are ordered by the keyword count total.
