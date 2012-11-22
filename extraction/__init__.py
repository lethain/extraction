"""
Retrieve and extract data from HTML documents.

    >>> import extraction
    >>> import requests
    >>> extr = Extractor()
    >>> html = requests.get("http://lethain.com/").text
    >>> resp = extr.extract(html)
    >>> print resp
"""

class Extracted(object):
    "Contains data extracted from a page."
    def __init__(self, titles=None, descriptions=None, images=None, urls=None):
        """
        Initialize Extracted instance.

        Extracted always internally stores titles, descriptions, images and
        canonical urls as lists, which can be accessed as properties::

            >>> print x.titles, x.urls, x.images

        The lists should be helpful For situations where you have a editor
        or user who is picking through possible options. For situations where
        you're without a curation mechanism, you can always get the best option
        using associated non-plural properties::

            >>> print x.title, x.url, x.image

        `urls` is a list of strings representing the best-guess canonical
        url for this piece of content as extracted from the HTML document.
        Sometimes there is no canonical URL referenced in the HTML, and in
        that case the using code will need to default to the url it fetched
        the HTML from (which the Extractor  doesn't know about, as it is
        agnostic to the source of information)::
        
            >>> import requests
            >>> from extraction import Extractor
            >>> url = "http://lethain.com/"
            >>> html = requests.get("url).text
            >>> extracted = Extractor().extract(html)
            >>> canonical_url = extracted.url if extract.url else url

        Titles, descriptions and images should all be lists.
        The lists should be ordered best to worst.        
        """
        if titles is None:
            titles = []
        if descriptions is None:
            descriptions = []
        if images is None:
            images = []
        if urls is None:
            urls = []

        assert(type(titles) in (list, tuple))
        assert(type(descriptions) in (list, tuple))
        assert(type(images) in (list, tuple))
        assert(type(urls) in (list, tuple))

        self.titles = titles
        self.descriptions = descriptions
        self.images = images
        self.urls = urls

    @property
    def title(self):
        "Return the best title, if any."
        if self.titles:
            return self.titles[0]
        else:
            return None

    @property
    def image(self):
        "Return the best image, if any."
        if self.images:
            return self.images[0]
        else:
            return None
        
    @property
    def description(self):
        "Return the best description, if any."
        if self.descriptions:
            return self.descriptions[0]
        else:
            return None

    @property
    def url(self):
        "Return the best url, if any."
        if self.urls:
            return self.urls[0]
        else:
            return None
      
        
class Extractor(object):
    "Extracts title, summary and image(s) from an HTML document."
    techniques = ["extraction.techniques.FacebookOpengraphTags"]

    def __init__(self, techniques=None):
        "Extractor."
        if techniques:
            self.techniques = techniques

        print self.techniques

    def extract(self, html):
        """
        Extract contents from a string representing an HTML document.

            >>> from extraction import Extractor
            >>> import requests
            >>> html = requests.get("http://lethain.com/").text
            >>> extracted = Extractor().extract(html)
            >>> print extracted

        """
        urls = []
        titles = []
        descriptions = []
        images = []
        

        extracted = Extracted(titles=titles, descriptions=descriptions, images=images, urls=urls)
        return extracted
