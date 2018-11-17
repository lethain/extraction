"This file contains techniques for extracting data from HTML pages."
import bs4


def init_bs(html):
    return bs4.BeautifulSoup(html, features="html5lib")


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
        soup = init_bs(html)
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
                if ('canonical' in link_tag['rel'] or link_tag['rel'] == 'canonical') and 'href' in link_tag.attrs:
                    if 'urls' not in extracted:
                        extracted['urls'] = []
                    extracted['urls'].append(link_tag['href'])
                elif ('alternate' in link_tag['rel'] or link_tag['rel'] == 'alternate') and 'type' in link_tag.attrs and link_tag['type'] == "application/rss+xml" and 'href' in link_tag.attrs:
                     if 'feeds' not in extracted:
                         extracted['feeds'] = []
                     extracted['feeds'].append(link_tag['href'])
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
    key_attr = 'property'
    property_map = {
        'og:title': 'titles',
        'og:url': 'urls',
        'og:image': 'images',
        'og:description': 'descriptions',
        }

    def extract(self, html):
        "Extract data from Facebook Opengraph tags."
        extracted = {}
        soup = init_bs(html)
        for meta_tag in soup.find_all('meta'):
            if self.key_attr in meta_tag.attrs and 'content' in meta_tag.attrs:
                property = meta_tag[self.key_attr]
                if property in self.property_map:
                    property_dest = self.property_map[property]
                    if property_dest not in extracted:
                        extracted[property_dest] = []
                    extracted[property_dest].append(meta_tag.attrs['content'])

        return extracted


class TwitterSummaryCardTags(FacebookOpengraphTags):
    """
    Extract info from the Twitter SummaryCard meta tags.
    """
    key_attr = 'name'
    property_map = {
        'twitter:title': 'titles',
        'twitter:description': 'descriptions',
        'twitter:image': 'images',
    }


class HTML5SemanticTags(Technique):
    """
    The HTML5 `article` tag, and also the `video` tag give us some useful
    hints for extracting page information for the sites which happen to
    utilize these tags.
    
    This technique will extract information from pages formed like::

        <html>
          <body>
            <h1>This is not a title to HTML5SemanticTags</h1>
            <article>
              <h1>This is a title</h1>
              <p>This is a description.</p>
              <p>This is not a description.</p>
            </article>
            <video>
              <source src="this_is_a_video.mp4">
            </video>
          </body>
        </html>

    Note that `HTML5SemanticTags` is intentionally much more conservative than
    `SemanticTags`, as it provides high quality information in the small number
    of cases where it hits, and otherwise expects `SemanticTags` to run sweep
    behind it for the lower quality, more abundant hits it discovers.
    """
    
    def extract(self, html):
        "Extract data from HTML5 semantic tags."
        titles = []
        descriptions = []
        videos = []
        soup = init_bs(html)
        for article in soup.find_all('article') or []:
            title = article.find('h1')
            if title:
                titles.append(u" ".join(title.strings))
            desc = article.find('p')
            if desc:
                descriptions.append(u" ".join(desc.strings))

        for video in soup.find_all('video') or []:
            for source in video.find_all('source') or []:
                if 'src' in source.attrs:
                    videos.append(source['src'])

        return {'titles':titles, 'descriptions':descriptions, 'videos':videos}


class SemanticTags(Technique):
    """
    This technique relies on the basic tags themselves--for example,
    all IMG tags include images, most H1 and H2 tags include titles,
    and P tags often include text usable as descriptions.

    This is a true last resort technique.
    """
    # list to support ordering of semantics, e.g. h1
    # is higher quality than h2 and so on
    # format is ("name of tag", "destination list", store_first_n)
    extract_string = [('h1', 'titles', 3),
                      ('h2', 'titles', 3),
                      ('h3', 'titles', 1),
                      ('p', 'descriptions', 5),
                      ]
    # format is ("name of tag", "destination list", "name of attribute" store_first_n)
    extract_attr = [('img', 'images', 'src', 10)]
    
    def extract(self, html):
        "Extract data from usual semantic tags."
        extracted = {}
        soup = init_bs(html)
        
        for tag, dest, max_to_store in self.extract_string:
            for found in soup.find_all(tag)[:max_to_store] or []:
                if dest not in extracted:
                    extracted[dest] = []
                extracted[dest].append(u" ".join(found.strings))

        for tag, dest, attribute, max_to_store in self.extract_attr:
            for found in soup.find_all(tag)[:max_to_store] or []:
                if attribute in found.attrs:
                    if dest not in extracted:
                        extracted[dest] = []
                    extracted[dest].append(found[attribute])

        return extracted
    
    
