# ft-scan
Full text scan
Main objective: Search full-text pdfs for specified keywords.

There were too many articles to screen for the full-text screening phase of the systematic review, predominant reason being that we don't know whether peak alpha frequency (PAF) was looked at. Searching the texts for PAF related terms means that some articles can be dropped before looking at the full text manually. 

To run this code you will need python, the `textract` package in python, the `full_text_scan.py` code and a bibtex of articles with related PDFs in a 'files' folder. Organise these as follows:

- ft-scan folder containing: `full_text_scan.py`, and two folders called 'TA_Yes' and 'TA_Maybe'
- Within each of these folders, put the appropriate bibtex (e.g. 'TA-Maybe_1946-2013_clean_with_files_to_scan.bib') with associated 'files' folder, both exported from the Zotero reference manager. 

From within the TA-Maybe folder, run with the following command:

```python ../../full_text_scan.py TA-Maybe_1946-2013_clean_with_files_to_scan.bib csv_results_TA_Maybe_test.csv output_TA_Maybe_test.md```

full_text_scan.py runs through the bibtex, finds the related pdf from the files folder, and scans the text for keywords. 

The .csv produced contains the article title, author, year, and file location, as well as count number
- Default keywords are summed to produce a total of their occurances, ignore words are summed and subtracted from this total. 
- Files that do not pass a sanity check for readability (i.e. file does not contain >=10 occurances of the words "the" and "a" are given a count of -1
- Files that cannot be found or opened are given a code of -2
- Files that include >=100 minor exclusion words are given a code of -3
- Files that include >=10 major exclusion words are given a code of -4

The .md file can be opened with a text editor or reader (e.g., Mark Text). The .md file displays the key words found in each article with the surrounding text. These are ordered by the count total. 

