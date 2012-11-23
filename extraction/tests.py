import unittest
import extraction

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.extractor = extraction.Extractor()

    def test_parse_facebook(self):
        # make sure the shuffled sequence does not lose any elements
        html = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
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
</head>
<body>
<h1>A Rock</h1>
</body>
</html>
"""
        self.extractor.techniques = ["extraction.techniques.FacebookOpengraphTags"]
        extracted = self.extractor.extract(html)
        self.assertEqual(extracted.title, "The Rock")
        self.assertEqual(extracted.titles, ["The Rock"])
        self.assertEqual(extracted.url, "http://www.imdb.com/title/tt0117500/")
        self.assertEqual(extracted.image, "http://ia.media-imdb.com/rock.jpg")
        self.assertEqual(extracted.images, ["http://ia.media-imdb.com/rock.jpg"])
        self.assertTrue(extracted.description, "A group of U.S. Marines, under command of a renegade general, take over Alcatraz and threaten San Francisco Bay with biological weapons.")
        self.assertEqual(len(extracted.descriptions), 1)

    def test_example_lethain_com_technique(self):
        "Test extracting data from lethain.com with a custom technique in extraction.examples."
        html = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<meta name="author" content="Will Larson" />
<meta name="description" content="Will Larson&#39;s blog about programming and other things." />
<meta name="keywords" content="Blog Will Larson Programming Life" />
<link rel="alternate" type="application/rss+xml" title="Page Feed" href="/feeds/" />
<link rel="canonical" href="http://lethain.com/digg-v4-architecture-process/">
<title>Digg v4&#39;s Architecture and Development Processes - Irrational Exuberance</title>
</head>
<body>
<div class="container container_12">
<div id="hd">
  <div class="grid_4">
    <h1><a href="/">Irrational Exuberance</a></h1>
  </div>
  <ul id="nav" class="grid_4 prefix_1">
    <li><a href="http://github.com/lethain">Projects</a></li>
    <li><a href="http://www.linkedin.com/pub/will-larson/3/b54/a44">Resume</a></li>
    <li><a href="/will-larson/">About</a></li>
    <li><a href="/feeds/">RSS</a></li>
  </ul>
    <form action="/search/" method="GET" class="grid_3">
      <input id="searchbox" name="q" value="">
      <input id="searchbutton" type="submit" value="Search">
    </form>
<br class="clear">
<ul id="tagnav" class="grid_12">
<li><a href="/tags/django/">django (73)</a></li><li><a href="/tags/python/">python (46)</a></li><li><a href="/tags/japan/">japan (43)</a></li><li><a href="/tags/jet/">jet (30)</a></li><li><a href="/tags/writing/">writing (20)</a></li><li><a href="/tags/lifeflow/">lifeflow (20)</a></li><li><a href="/tags/erlang/">erlang (20)</a></li><li><a href="/tags/javascript/">javascript (18)</a></li>
<li><a href="/tags/">&hellip;</a></li>
</ul>
</div>
<div class="grid_9">
  <div id="body">
<div class="page">
  <h2><a href="/digg-v4-architecture-process">Digg v4&#39;s Architecture and Development Processes</a></h2>
  <span class="date">08/19/2012</span>
  <span class="tag"><a href="/tags/architecture/">architecture</a><span class="tagcount">(5)</span></span>
  <span class="tag"><a href="/tags/digg/">digg</a><span class="tagcount">(3)</span></span>
  <br class="clear">
   <div class="text">
     <p>A month ago history reset with <a href="http://blog.digg.com/post/27628665720/v1">the second launch of Digg v1</a>,
and memories are starting to fade since
    <a href="http://www.washingtonpost.com/business/technology/socialcode-hires-15-employees-from-diggcom/2012/05/10/gIQAP2xBFU_story.html">much of the Digg team joined SocialCode</a>
four months ago, so it seemed like a good time to describe the system and team architecture
which ran and developed <a href="http://digg.com/">Digg.com</a> from May 2010 until May 2012.</p>
    <p>There won't be controversy here, not even much of a narrative,
just a description of how we were working and the architecture
we built out.</p>
    <h2 id="team_structure_size_and_organization">Team Structure, Size and Organization</h2>
    <p>We have to start with a bit of context surrounding
the company's size, how the teams were organized, and how the structure was impacted
by a series of layoffs and subsequent hiring.</p>
    <p><img alt="The starting team architecture." src="/static/blog/digg_v4/initial_org.png" /></p>
    <p>For focus I'm not covering the Sales, Finance, Ad Management, Design,
HR, BD teams and such; they were important pieces of the company and how
it functioned, just not central to this particular story.</p>
      </div>
    </div>
  </body>
</html>
"""
        self.extractor.techniques = ["extraction.examples.custom_technique.LethainComTechnique"]
        extracted = self.extractor.extract(html)
        self.assertEqual(extracted.title, "Digg v4's Architecture and Development Processes")
        self.assertEqual(extracted.url, None)
        self.assertEqual(extracted._unexpected_values['tags'], [u'architecture', u'digg'])
        self.assertEqual(extracted._unexpected_values['dates'], [u'08/19/2012'])
        self.assertEqual(extracted.image, "/static/blog/digg_v4/initial_org.png")
        self.assertEqual(len(extracted.images), 1)
        self.assertEquals(extracted.description.split(), "A month ago history reset with the second launch of Digg v1 , and memories are starting to fade since much of the Digg team joined SocialCode four months ago, so it seemed like a good time to describe the system and team architecture which ran and developed Digg.com from May 2010 until May 2012.".split())



if __name__ == '__main__':
    unittest.main()
