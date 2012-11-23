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

class HeadTags(Technique):
    """
    Extract info from standard HTML metatags like title, for example:

        <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
            <meta name="author" content="Will Larson" />
            <meta name="description" content="Will Larson&#39;s blog about programming and other things." />
            <meta name="keywords" content="Blog Will Larson Programming Life" />
            <link rel="alternate" type="application/rss+xml" title="Page Feed" href="/feeds/" />
            <link rel="canonical" href="http://lethain.com/digg-v4-architecture-process/">
            <title>Digg v4&#39;s Architecture and Development Processes - Irrational Exuberance</title>
        </head>

    This is usually a last-resort, low quality, but reliable parsing mechanism.
    """
    meta_name_map = {
        "description": "descriptions",
        "author": "authors",
        }

    def extract(self, html):
        "Extract data from meta, link and title tags within the head tag."
        extracted = {}
        soup = BeautifulSoup(html)
        # extract data from title tag
        title_tag = soup.find('title')
        if title_tag:
            extracted['titles'] = [title_tag.string]

        # extract data from meta tags
        for meta_tag in soup.find_all('meta'):
            if 'name' in meta_tag.attrs and 'content' in meta_tag.attrs:
                name = meta_tag['name']
                if name in self.meta_name_map:
                    name_dest = self.meta_name_map[name]
                    if name_dest not in extracted:
                        extracted[name_dest] = []
                    extracted[name_dest].append(meta_tag.attrs['content'])

        # extract data from link tags
        for link_tag in soup.find_all('link'):
            if 'rel' in link_tag.attrs:
                if ('alternate' in link_tag['rel'] or link_tag['rel'] == 'alternate') and 'type' in link_tag.attrs and link_tag['type'] == "application/rss+xml" and 'href' in link_tag.attrs:
                    if 'feeds' not in extracted:
                        extracted['feeds'] = []
                    extracted['feeds'].append(link_tag['href'])
                elif ('canonical' in link_tag['rel'] or link_tag['rel'] == 'canonical') and 'href' in link_tag.attrs:
                    if 'urls' not in extracted:
                        extracted['urls'] = []
                    extracted['urls'].append(link_tag['href'])
                    
        return extracted

    

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

