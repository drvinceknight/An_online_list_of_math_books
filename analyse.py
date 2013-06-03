#!/usr/bin/env python

"""

Script to analyse the downloaded data set of books.

"""

import pickle
import sys
import nltk


class Book():
    """
    A class for a book entry.
    """
    def __init__(self, row):
        self.title = row[0]
        self.authors = row[1]
        self.link = row[2]
        self.overview = row[3]
        self.target = row[4]
        self.addedby = row[5]
        if row[5] == "":
            self.addedby = "Anonymous"


class Table():
    """
    Represents a data set as a list of objects
    """
    def __init__(self):
        self.records = []

    def __len__(self):
        return len(self.records)

    def ReadFile(self, picklefile):
        """Reads a pickledfile

        Args:
            picklefile: name (including path) of a pickled data file.
        """
        f = open(picklefile, "rb")
        self.rawdata = pickle.load(f)
        f.close()
        for row in self.rawdata:
            self.AddRow(Book(row))

    def AddRow(self, book):
        """Adds a row to this table

        Args:
            book: an abject of type book
        """
        self.records.append(book)

    def CreateContributorsDict(self):
        """Returns the contributors to the list as keys to a dictionary"""
        self.contributors = {}
        for row in self.records:
            if row.addedby in self.contributors:
                self.contributors[row.addedby].append(row.title)
            else:
                self.contributors[row.addedby] = [row.title]

    def CreateAuthorsDict(self):
        """Returns the authors of the list as keys to a dictionary"""
        self.authors = {}
        for row in self.records:
            if row.authors in self.authors:
                self.authors[row.authors].append(row.title)
            else:
                self.authors[row.authors] = [row.title]


if __name__ == "__main__":
    picklefile = "book_list.pickle"
    if len(sys.argv) > 1:
        if ".pickle" in sys.argv[1]:
            picklefile = sys.argv[1]
    Books = Table()
    Books.ReadFile(picklefile)
    print len(Books)
#    Books.CreateContributorsDict()
#    for contributor in Books.contributors:
#        print contributor + ":"
#        for e in Books.contributors[contributor]:
#            print "\t", e
#    Books.CreateAuthorsDict()
#    for author in Books.authors:
#        print author + ":"
#        for e in Books.authors[author]:
#            print "\t", e
