"""
Retrieve and extract data from HTML documents.

    >>> import extraction
    >>> import requests
    >>> extr = Extractor()
    >>> html = requests.get("http://lethain.com/").text
    >>> resp = extr.extract(html)
    >>> print resp
"""
import importlib

class Extracted(object):
    "Contains data extracted from a page."

    def __init__(self, titles=None, descriptions=None, images=None, urls=None, **kwargs):
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

        assert type(titles) in (list, tuple), "titles must be a list or tuple"
        assert type(descriptions) in (list, tuple), "descriptions must be a list or tuple"
        assert type(images) in (list, tuple), "images must be a list or tuple"
        assert type(urls) in (list, tuple), "urls must be a list or tuple"

        self.titles = titles
        self.descriptions = descriptions
        self.images = images
        self.urls = urls

        # stores unexpected and uncaptured values to avoid crashing if
        # a technique returns additional types of data
        self._unexpected_values = kwargs

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

    def __init__(self, techniques=None, *args, **kwargs):
        "Extractor."
        if techniques:
            self.techniques = techniques
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

    def cleanup(self, results, html, source_url=None):
        """
        Allows standardizing extracted contents, at this time:

        1. removes multiple whitespaces
        2. rewrite relative URLs as absolute URLs if source_url is specified
        """

        # TODO: rewrite images/urls if source_url is specified
        cleaned_results = {}
        for data_type, data_values in results.items():
            if data_type in ('descriptions','titles'):
                data_values = [" ".join(x.split()) for x in data_values]
            cleaned_results[data_type] = data_values
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

        return Extracted(**self.cleanup(extracted, html, source_url=source_url))
