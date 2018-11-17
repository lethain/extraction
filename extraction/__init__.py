"""
Retrieve and extract data from HTML documents.

    >>> import extraction
    >>> import requests
    >>> extr = Extractor()
    >>> html = requests.get("http://lethain.com/").text
    >>> resp = extr.extract(html)
    >>> print resp
"""
import urllib.parse
import importlib


# This is a debugging mechanism, and if enabled will add a hash
# to crawled URLS showing which Technique extracted the data.
# Should be True or False. Usually should be False.
MARK_TECHNIQUE = False


class Extracted(object):
    "Contains data extracted from a page."

    def __init__(self, titles=None, descriptions=None, images=None, videos=None, urls=None, feeds=None, **kwargs):
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
        if videos is None:
            videos = []
        if urls is None:
            urls = []
        if feeds is None:
            feeds = []

        assert type(titles) in (list, tuple), "titles must be a list or tuple"
        assert type(descriptions) in (list, tuple), "descriptions must be a list or tuple"
        assert type(images) in (list, tuple), "images must be a list or tuple"
        assert type(videos) in (list, tuple), "videos must be a list or tuple"
        assert type(urls) in (list, tuple), "urls must be a list or tuple"
        assert type(feeds) in (list, tuple), "feeds must be a list or tuple"

        self.titles = titles
        self.descriptions = descriptions
        self.images = images
        self.urls = urls
        self.feeds = feeds
        self.videos = videos

        # stores unexpected and uncaptured values to avoid crashing if
        # a technique returns additional types of data
        self._unexpected_values = kwargs

    def __repr__(self):
        "String representation of extracted results."
        details = (("title", self.titles),
                   ("url", self.urls),
                   ("image", self.images),
                   ("videos", self.videos),
                   ("description", self.descriptions),
                   ("feed", self.feeds),
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
    def video(self):
        "Return the best video, if any."
        if self.videos:
            return self.videos[0]
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


class DictExtractor(object):
    """
    Extracts title, image and description from an HTML document.

    Returns extracted data as a dictionary. If you want to return
    the results as an ``Extracted``, then use ``Extractor`` instead
    of ``DictExtractor``.
    """
    techniques = [
        "extraction.techniques.FacebookOpengraphTags",
        "extraction.techniques.TwitterSummaryCardTags",
        "extraction.techniques.HeadTags",
        "extraction.techniques.HTML5SemanticTags",
        "extraction.techniques.SemanticTags"
    ]

    # for determining which cleanup mechanisms to apply
    url_types = ["images", "urls", "feeds", "videos"]
    text_types = ["titles", "descriptions"]

    def __init__(self, techniques=None, strict_types=False, *args, **kwargs):
        "Extractor."
        self.strict_types = strict_types
        if techniques:
            self.techniques = techniques

        super(DictExtractor, self).__init__(*args, **kwargs)

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
        technique_class = getattr(technique_module, technique_class_name)
        technique_inst = technique_class(extractor=self)
        return technique_inst.extract(html)

    def cleanup_text(self, value, mark):
        "Cleanup text values like titles or descriptions."
        text = u" ".join(value.strip().split())
        if mark:
            text = u"%s %s" % (mark, text)
        return text

    def cleanup_url(self, value_url, source_url, mark):
        """
        Transform relative URLs into absolute URLs if possible.

        If the value_url is already absolute, or we don't know the
        source_url, then return the existing value. If the value_url is
        relative, and we know the source_url, then try to rewrite it.
        """
        value = urllib.parse.urlparse(value_url)
        if value.netloc or not source_url:
            url = value_url
        else:
            url = urllib.parse.urljoin(source_url, value_url)
        if url.startswith('//'):
            url = 'http:' + url # MissingSchema fix
        if mark:
            url = url + mark
        return url

    def cleanup(self, results, source_url=None, technique=""):
        """
        Allows standardizing extracted contents, at this time:

        1. removes multiple whitespaces
        2. rewrite relative URLs as absolute URLs if source_url is specified
        3. filter out duplicate values
        4. marks the technique that produced the result
        5. returns only specified text_types and url_types depending on self.strict_types
        """
        cleaned_results = {}
        mark = MARK_TECHNIQUE and u"#" + technique.split('.')[-1]

        for data_type, data_values in results.items():
            if data_type in self.text_types:
                data_values = [self.cleanup_text(x, mark) for x in filter(None, data_values)]
            elif data_type in self.url_types:
                data_values = [self.cleanup_url(x, source_url, mark) for x in data_values]
            elif self.strict_types:
                continue

            # filter out duplicate values
            unique_values = []
            for data_value in data_values:
                if data_value not in unique_values:
                    unique_values.append(data_value)

            cleaned_results[data_type] = unique_values

        return cleaned_results

    def extract(self, html, source_url=None):
        """
        Extracts contents from an HTML document.

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
            technique_cleaned = self.cleanup(technique_extracted, source_url=source_url, technique=technique)
            for data_type, data_values in technique_cleaned.items():
                if data_values:
                    if data_type not in extracted:
                        extracted[data_type] = []

                    # don't include duplicate values
                    unique_data_values = [x for x in data_values if x not in extracted[data_type]]
                    extracted[data_type] += unique_data_values
        return extracted


class Extractor(DictExtractor):
    """
    Subclass of ``DictExtractor`` which wraps results in a
    subclass of ``Extracted`` for greater control.
    """
    extracted_class = Extracted

    def __init__(self, extracted_class=None, *args, **kwargs):
        "Initialize Extractor instance."
        super(Extractor, self).__init__(*args, **kwargs)
        if extracted_class:
            self.extracted_class = extracted_class

    def extract(self, *args, **kwargs):
        "Extract contents from an HTML document."
        extract_dict = super(Extractor, self).extract(*args, **kwargs)
        return self.extracted_class(**extract_dict)


class SvvenExtractor(DictExtractor):
    "Example subclass for Svven news aggregator."
    url_types = ["images", "urls"]
    text_types = ["titles", "descriptions"]

    def __init__(self, *args, **kwargs):
        "Extractor which defaults to strict_types being true."
        kwargs.setdefault('strict_types', True)
        super(SvvenExtractor, self).__init__(*args, **kwargs)
