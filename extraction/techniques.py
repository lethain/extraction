"This file contains techniques for extracting data from HTML pages."
from bs4 import BeautifulSoup


class Technique(object):
    def __init__(self, extractor=None, *args, **kwargs):
        """
        Capture the extractor this technique is running within,
        if any.
        """
        self.extractor = extractor
        super(Technique, self).__init__(*args, **kwargs)

    def extract(self, html):
        "Extract data from a string representing an HTML document."
        return {'titles': [],
                'descriptions': [],
                'images': [],
                'urls': [],
                }


class FacebookOpengraphTags(Technique):
    """
    Extract info from html Facebook Opengraph meta tags.

    Facebook tags are ubiquitous on high quality sites, and tend to be higher quality
    than more manual discover techniques. Especially for picking high quality images,
    this is probably your best bet.

    Some example tags from `the Facebook opengraph docs <https://developers.facebook.com/docs/opengraphprotocol/>`::

        <meta property="og:title" content="The Rock"/>
        <meta property="og:type" content="movie"/>
        <meta property="og:url" content="http://www.imdb.com/title/tt0117500/"/>
        <meta property="og:image" content="http://ia.media-imdb.com/rock.jpg"/>
        <meta property="og:site_name" content="IMDb"/>
        <meta property="fb:admins" content="USER_ID"/>
        <meta property="og:description"
            content="A group of U.S. Marines, under command of
                     a renegade general, take over Alcatraz and
                     threaten San Francisco Bay with biological
                     weapons."/>

    There are a bunch of other opengraph tags, but they don't seem
    useful to extraction's intent at this point.
    """
    property_map = {
        'og:title': 'titles',
        'og:url': 'urls',
        'og:image': 'images',
        'og:description': 'descriptions',
        }

    def extract(self, html):
        "Extract data from Facebook Opengraph tags."
        extracted = {}
        soup = BeautifulSoup(html)
        for meta_tag in soup.find_all('meta'):
            if 'property' in meta_tag.attrs and 'content' in meta_tag.attrs:
                property = meta_tag['property']
                if property in self.property_map:
                    property_dest = self.property_map[property]
                    if property_dest not in extracted:
                        extracted[property_dest] = []
                    extracted[property_dest].append(meta_tag.attrs['content'])

        return extracted

