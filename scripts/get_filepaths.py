import sys

def get_bibtex():
    try:
        bibtex_filename = sys.argv[1]
    except IndexError:
        exit("Please include the bibtex file to be read.")
    else:
        with open(bibtex_filename) as bibtex_file:
            bibtex = bibtex_file.readlines()
        return bibtex

def main():
    bibtex = get_bibtex()
    filenames = [
        row for row in bibtex if row.startswith("\tfile = {Attachment")
    ]
    not_pdfs = [row for row in filenames if "application/pdf" not in row]
    for pdf in not_pdfs:
        print(pdf)

if __name__ == "__main__":
    main()
