"""
This file includes an example of a custom Technique tailored around
parsing articles on my blog at lethain.com. Usage is::

    >>> import extraction, requests
    >>> url = "http://lethain.com/digg-v4-architecture-process/"
    >>> techniques = ["extraction.examples.LethainComTechnique"]
    >>> extractor = extraction.Extractor(techniques=techniques)
    >>> extracted = extractor.extract(requests.get(url))
    >>> extracted.title
    blah

This is also an example of returning additional metadata,
in this case it also extracts a date and tags from the page.
"""
from extraction.techniques import Technique
from bs4 import BeautifulSoup

class LethainComTechnique(Technique):
    """
    Extract data from articles on lethain.com, based on articles being structured like so::

        <div class="page">
            <h2><a href="/digg-v4-architecture-process">Digg v4&#39;s Architecture and Development Processes</a></h2>
            <span class="date">08/19/2012</span>
            <span class="tag"><a href="/tags/architecture/">architecture</a><span class="tagcount">(5)</span></span>
            <span class="tag"><a href="/tags/digg/">digg</a><span class="tagcount">(3)</span></span>
            <div class="text">
              <p>A month ago history reset with...</p>
            </div>
        </div>

    Depending on how many sites you're extracting data from, these techniques are either very
    useful or clinically insane. Perhaps both.
    """
    def extract(self, html):
        "Extract data from lethain.com."
        soup = BeautifulSoup(html, features="html5lib")
        page_div = soup.find('div', class_='page')
        text_div = soup.find('div', class_='text')
        return { 'titles': [page_div.find('h2').string],
                 'dates': [page_div.find('span', class_='date').string],
                 'descriptions': [" ".join(text_div.find('p').strings)],
                 'tags': [x.find('a').string for x in page_div.find_all('span', class_='tag')],
                 'images': [x.attrs['src'] for x in text_div.find_all('img')],
                 }

