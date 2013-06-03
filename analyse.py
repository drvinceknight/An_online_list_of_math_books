#!/usr/bin/env python

"""

Script to analyse the downloaded data set of books.

"""

from __future__ import division
import pickle
import sys
import nltk
import collections
import matplotlib.pyplot as plt


def RemoveCommon(dict):
    """
    A function to remove common English words from a word frequency dictionary

    Args:
        dict: a dictionary with strings as keys
    """
    commonwords = [e.upper() for e in set(nltk.corpus.stopwords.words('english'))]
    for key in dict.keys():
        if key.upper() in commonwords:
            del dict[key]
    return dict


def PlotDict(dict, title, xlabel, width=1):
    """
    A function to plot bar plot of distribution of counts in a dictionary

    Args:
        dict: A dictionary with numeric values
        title: A title for the plot (which will also be used as the title for the png file that is output
        xlable: A title for the x label
        width: width of the bins
    """
    plt.figure()
    x = [len(e) for e in dict.values()]
    plt.hist(x, bins=[e - width / 2 for e in range(max(x) + 2)], normed=True)
    plt.xlabel(xlabel)
    plt.ylabel("Probability")
    plt.xlim(width / 2, max(x) + width / 2)
    plt.title(title)
    plt.savefig("./images/" + title.replace(" ", "_") + ".png")


def PlotFreqDict(dict, title, xlabel, numberofwords=50, width=.1):
    """
    A function to plot bar plot of distribution of frequency

    Args:
        dict: A dictionary with numeric values
        title: A title for the plot (which will also be sued as the title for the png file that is output
        xlabel: A title for the x label
        numberofwords: The number of most popular words
        width: width of the bins
    """
    x = [e - width for e in range(1, 2 * numberofwords + 1, 2)]
    plt.figure()
    plt.bar(x, dict.values()[:numberofwords], width=width, align="center")
    plt.xticks(x, dict.keys()[:numberofwords], rotation=90)
    plt.xlabel("Word")
    plt.ylabel("Frequency")
    plt.title(title + "\n(%s most common words)" % numberofwords)
    plt.savefig("./images/" + title.replace(" ", "_") + ".png", bbox_inches='tight')


class Book():
    """
    A class for a book entry.
    """
    def __init__(self, row):
        self.title = row[0]
        self.authors = [e.lstrip().rstrip().upper() for e in row[1].replace(",", " and").replace("And", "and").replace("/", " and ").split(" and ")]
        if self.authors == ['']:
            self.authors = ['Unkown']
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
        f = open(picklefile, "rb")  # The data is a pickled list created with another script that automatically downloads the spreadsheet from google drive.
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
            for author in row.authors:
                if author in self.authors:
                    self.authors[author].append(row.title)
                else:
                    self.authors[author] = [row.title]

    def CreateFreqDistOfTarget(self, removecommon=False):
        """Returns a dictionary of the word frequency in the target

        Args:
            removecommon: If set to True, will remove common words as defined by the nltk.corpus.stopwords.words set.
        """
        targets = ""
        for row in self.records:
            targets += row.target
        self.targetfrq = collections.OrderedDict(nltk.FreqDist([e.upper() for e in targets.replace(".", " ").replace("!", " ").replace(",", " ").replace(")", "").replace("(", "").replace("'", "").replace("`", "").split()]))  # Creates a sorted dictionary which is useful for plotting.
        if removecommon:
            RemoveCommon(self.targetfrq)

    def CreateFreqDistOfOverview(self, removecommon=False):
        """Returns a dictionary of the word frequency in the overiews

        Args:
            removecommon: If set to True, will remove common words as defined by the nltk.corpus.stopwords.words set.
        """
        overviews = ""
        for row in self.records:
            overviews += row.overview
        self.overviewfrq = collections.OrderedDict(nltk.FreqDist([e.upper() for e in overviews.replace(".", " ").replace("!", " ").replace(",", " ").replace(")", "").replace("(", "").replace("'", "").split()]))  # Creates a sorted dictionary which is useful for plotting.
        if removecommon:
            RemoveCommon(self.overviewfrq)


if __name__ == "__main__":
    picklefile = "book_list.pickle"  # Default file to read in.
    if len(sys.argv) > 1:
        if ".pickle" in sys.argv[1]:
            picklefile = sys.argv[1]
    Books = Table()  # Create table instance
    Books.ReadFile(picklefile)  # Read in empty instance

    # Analyse contributors

    Books.CreateContributorsDict()  # Create contributors dictionary
    PlotDict(Books.contributors, "Distribution of number of contributions", "Number of contributions")  # Plot distribution of contributors

    # Find contributor with most books

    mostprolificcontributor = Books.contributors.keys()[0]
    for key in Books.contributors.keys()[1:]:
        if len(Books.contributors[key]) > len(Books.contributors[mostprolificcontributor]):
            mostprolificcontributor = key
    print "Most prolific contributor is:", mostprolificcontributor
    for e in Books.contributors[mostprolificcontributor]:
        print "\t", e

    # Analyse authors

    Books.CreateAuthorsDict()  # Create Authors dictionary
    PlotDict(Books.authors, "Distribution of number of books by author", "Number of books")  # Plot distribution of authors

    # Find author with most books

    mostprolificauthor = Books.authors.keys()[0]
    for key in Books.authors.keys()[1:]:
        if len(Books.authors[key]) > len(Books.authors[mostprolificauthor]):
            mostprolificauthor = key
    print "Most prolific author is:", mostprolificauthor
    for e in Books.authors[mostprolificauthor]:
        print "\t", e

    # Some basic nl processing

    # For Overview

    Books.CreateFreqDistOfOverview(removecommon=True)  # Create distribution of words in overview, removing common words
    PlotFreqDict(Books.overviewfrq, "Word count in overview", "word")  # Plot distribution

    # For Target

    Books.CreateFreqDistOfTarget(removecommon=True)  # Create distribution of words in tart, removing common words
    PlotFreqDict(Books.targetfrq, "Word count in target", "word")  # Plot distribution

    # Write index.html with the list of books

    f = open("index.md", "wr")
    f.write("""
# A online (open) list of Mathematics Books
## Introduction
This site contains a list of books based on the [spreadsheet](https://docs.google.com/spreadsheet/ccc?key=0AvXhcaIlhi4udEFIN1ZSUTRpakotUEZ6QmlEOWNua3c&hl=en&forcehl=1#gid=0) put up by [+James Noble](https://plus.google.com/102137382870708304914/posts).

[The spreadsheet is completely open and contains a list of books as well as well as a list of other lists](https://docs.google.com/spreadsheet/ccc?key=0AvXhcaIlhi4udEFIN1ZSUTRpakotUEZ6QmlEOWNua3c&hl=en&forcehl=1#gid=0)

The list has been contributed to by %s different contributors. As this page was compiled automatically and some of the contributors have left their email address (others their G+ page and/or twitter handle) I won't list them here in case it causes more spam but do go take a look at the spreadsheet :).

**Go ahead and add any book you have to the list!**

## Some initial analysis

I wrote some code to analyse (and in fact write the html behind this site) some aspects of the data set which (last time I checked) contains %s books.

### Contributors

The list is completely open but some people seem to contribute more than others. Here's the distribution of the number of guesses:

![Distribution of the number of guesses](./images/Distribution_of_number_of_contributions.png)

### Authors

Similarly for the authors, here's the distribution of the number of books by author:

![Number of books](./images/Distribution_of_number_of_books_by_author.png)

The most prolific author is %s with %s books in the list.

### Overview

The list contains a data field allowing people to describe the book. Here is a plot of the frequency of the 50 most used "uncommon" words (using the [nltk](http://nltk.org/) python library).

![Words used in the overview](./images/Word_count_in_overview.png)

### Target

There is also a field briefly describing the target audience for the book. Here is a similar frequency count to above:

![Words used in the target](./images/Word_count_in_target.png)

## The Books

Here is the actual list of books:
            """ % (len(Books.contributors), len(Books), mostprolificauthor, len(Books.authors[mostprolificauthor])))

    k = 0
    for book in Books.records:
        k += 1
        f.write("\n%s . [%s](%s)\n" % (k, book.title, book.link))
        f.write("\n **Authored** by %s" % book.authors[0])
        if len(book.authors) > 1:
            for a in book.authors[1:]:
                f.write(", %s" % a)
        f.write("""\n**Overview:**\n
> '%s'
                """ % book.overview)
        f.write("""\n**Target:**\n
> '%s'
                """ % book.target)

    f.write("""
## Contributing

If you would like to add a book to the list go ahead to the google spreadsheet [here](https://docs.google.com/spreadsheet/ccc?key=0AvXhcaIlhi4udEFIN1ZSUTRpakotUEZ6QmlEOWNua3c&hl=en&forcehl=1#gid=0) and feel free to add to it. This website itself is not dynamic so if I don't update soon after you add to the list, feel free to give me a nudge on G+: my profile is [here](https://plus.google.com/110464871801965858778/posts).

            If you would like to take a look at the code used to analyse the data and write this site (and please do improve it) the github repo is [here](https://github.com/drvinceknight/An_online_list_of_math_books).

## License Information

This work is licensed under a [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/us/) license.  You are free to:

* Share: copy, distribute, and transmit the work,
* Remix: adapt the work

Under the following conditions:

* Attribution: You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work).
* Share Alike: If you alter, transform, or build upon this work, you may distribute the resulting work only under the same or similar license to this one.

When attributing this work, please include me.
            """)
