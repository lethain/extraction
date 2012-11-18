"""
Retrieve and extract data from HTML documents.

    >>> import extraction
    >>> x = Extractor(html_as_string)




"""
import requests


class Extractor(object):
    "Extractor which takes an HTML string."
    def __init__(self, html):
        "Accepts a string to extract data from."


class FetchingExtractor(Extractor):
    "Extractor which fetches the data to extract and then extracts it."
