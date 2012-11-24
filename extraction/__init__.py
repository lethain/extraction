"""
Retrieve and extract data from HTML documents.

    >>> import extraction
    >>> import requests
    >>> extr = Extractor()
    >>> html = requests.get("http://lethain.com/").text
    >>> resp = extr.extract(html)
    >>> print resp
"""
import urlparse
import importlib

class Extracted(object):
    "Contains data extracted from a page."

    def __init__(self, titles=None, descriptions=None, images=None, urls=None, feeds=None, **kwargs):
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
        if feeds is None:
           feeds = []

        assert type(titles) in (list, tuple), "titles must be a list or tuple"
        assert type(descriptions) in (list, tuple), "descriptions must be a list or tuple"
        assert type(images) in (list, tuple), "images must be a list or tuple"
        assert type(urls) in (list, tuple), "urls must be a list or tuple"
        assert type(feeds) in (list, tuple), "urls must be a list or tuple"

        self.titles = titles
        self.descriptions = descriptions
        self.images = images
        self.urls = urls
        self.feeds = feeds

        # stores unexpected and uncaptured values to avoid crashing if
        # a technique returns additional types of data
        self._unexpected_values = kwargs

    def __repr__(self):
        "String representation of extracted results."
        details = (("title", self.titles),
                   ("url", self.urls),
                   ("image", self.images),
                   ("feed", self.feeds),
                   ("description", self.descriptions),
                   )

        details_strs = []
        max_shown = 50
        for name, values, in details:
            if values:
                value = values[0]
                count = len(values)
                if count -1 > 0:
                    details_strs.append("(%s: '%s', %s more)" % (name, value[:max_shown], count-1))
                else:
                    details_strs.append("(%s: '%s')" % (name, value[:max_shown]))

        return "<%s: %s>" % (self.__class__.__name__, ", ".join(details_strs))

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

    @property
    def feed(self):
        "Return the best feed, if any."
        if self.feeds:
            return self.feeds[0]
        else:
            return None


class Extractor(object):
    "Extracts title, summary and image(s) from an HTML document."
    techniques = ["extraction.techniques.FacebookOpengraphTags",
                  "extraction.techniques.HTML5SemanticTags",
                  "extraction.techniques.HeadTags",
                  "extraction.techniques.SemanticTags",
                  ]
    extracted_class = Extracted

    # for determining which cleanup mechanisms to apply
    text_types = ["titles", "descriptions"]
    url_types = ["images", "urls", "feeds"]

    def __init__(self, techniques=None, extracted_class=None, *args, **kwargs):
        "Extractor."
        if techniques:
            self.techniques = techniques
        if extracted_class:
            self.extracted_class = extracted_class

        super(Extractor, self).__init__(*args, **kwargs)

    def run_technique(self, technique, html):
        """
        Run a given technique against the HTML.

        Technique is a string including the full module path
        and class name for the technique, for example::

            extraction.techniques.FacebookOpengraphTags

        HTML is a string representing an HTML document.
        """
        technique_path_parts = technique.split('.')
        assert len(technique_path_parts) > 1, "technique_path_parts must include a module and a class"
        technique_module_path = ".".join(technique_path_parts[:-1])
        technique_class_name = technique_path_parts[-1]
        technique_module = importlib.import_module(technique_module_path)
        technique_inst = getattr(technique_module, technique_class_name)(extractor=self)
        return technique_inst.extract(html)

    def cleanup_text(self, value):
        "Cleanup text values like titles or descriptions."
        return " ".join(value.split())

    def cleanup_url(self, value_url, source_url=None):
        """
        Transform relative URLs into absolute URLs if possible.

        If the value_url is already absolute, or we don't know the
        source_url, then return the existing value. If the value_url is
        relative, and we know the source_url, then try to rewrite it.
        """
        value = urlparse.urlparse(value_url)
        if value.netloc or not source_url:
            return value_url
        else:
            return urlparse.urljoin(source_url, value_url)

    def cleanup(self, results, html, source_url=None):
        """
        Allows standardizing extracted contents, at this time:

        1. removes multiple whitespaces
        2. rewrite relative URLs as absolute URLs if source_url is specified
        3. filter out duplicate values
        """
        cleaned_results = {}
        for data_type, data_values in results.items():
            if data_type in self.text_types:
                data_values = [self.cleanup_text(x) for x in data_values]
            if data_type in self.url_types:
                data_values = [self.cleanup_url(x, source_url=source_url) for x in data_values]

            # filter out duplicate values
            unique_values = []
            for data_value in data_values:
                if data_value not in unique_values:
                    unique_values.append(data_value)

            cleaned_results[data_type] = unique_values
        
        return cleaned_results

    def extract(self, html, source_url=None):
        """
        Extract contents from a string representing an HTML document.

            >>> from extraction import Extractor
            >>> import requests
            >>> html = requests.get("http://lethain.com/").text
            >>> extracted = Extractor().extract(html)
            >>> print extracted

        `source_url` is optional, but allows for a certain level of
        cleanup to be performed, such as converting relative URLs
        into absolute URLs and such.
        """
        extracted = {}
        for technique in self.techniques:
            technique_extracted = self.run_technique(technique, html)
            for data_type, data_values in technique_extracted.items():
                if data_values:
                    if data_type not in extracted:
                        extracted[data_type] = []
                    extracted[data_type] += data_values

        return self.extracted_class(**self.cleanup(extracted, html, source_url=source_url))
