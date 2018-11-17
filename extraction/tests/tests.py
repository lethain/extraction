import unittest
import extraction
from extraction.tests.data import *
from extraction.examples.new_return_type import AddressExtractor

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.extractor = extraction.Extractor()

    def test_rewriting_relative_urls(self):
        "Test rewriting relative URLs as absolute URLs if source_url is specified."
        self.extractor.techniques = ["extraction.examples.custom_technique.LethainComTechnique"]

        # without source_url, stays as a relative URL
        extracted = self.extractor.extract(LETHAIN_COM_HTML)
        self.assertEqual(extracted.image, "/static/blog/digg_v4/initial_org.png")

        # with source_url, should rewrite as an absolute path
        extracted = self.extractor.extract(LETHAIN_COM_HTML, source_url="http://lethain.com/digg-v4-architecture-process/")
        # rewrites /static/blog/digg_v4/initial_org.png
        self.assertEqual(extracted.images[0], "http://lethain.com/static/blog/digg_v4/initial_org.png")
        # rewrites ../digg_v4/initial_org.png
        self.assertEqual(extracted.images[1], "http://lethain.com/digg_v4/initial_org.png")

    def test_removing_duplicate_values(self):
        "We shouldn't suggest the same extracted value multiple times."
        extracted = self.extractor.extract(DUPLICATES_HTML)
        self.assertEqual(extracted.titles, ["Hi"])
        self.assertEqual(extracted.descriptions, ["This is awesome."])

    def test_default_techniques(self):
        """
        Test running the default techniques list with a simple page.

        This is a bit of a high-level test to ensure that the default
        techniques aren't completely broken.
        """
        extracted = self.extractor.extract(LETHAIN_COM_HTML, source_url="http://lethain.com/digg-v4-architecture-process/")
        self.assertTrue(extracted.titles)
        self.assertTrue(extracted.urls)
        self.assertTrue(extracted.descriptions)
        self.assertTrue(extracted.feeds)

    def test_default_techniques_on_empty_page(self):
        """
        Test running the default techniques list against an empty HTML document.

        This is useful for ensuring the defaut techniques fail sanely when they
        encounter blank/empty documents.
        """
        extracted = self.extractor.extract("")
        self.assertFalse(extracted.titles)
        self.assertFalse(extracted.urls)
        self.assertFalse(extracted.descriptions)
        self.assertFalse(extracted.feeds)

    def test_technique_facebook_meta_tags(self):
        # make sure the shuffled sequence does not lose any elements
        self.extractor.techniques = ["extraction.techniques.FacebookOpengraphTags"]
        extracted = self.extractor.extract(FACEBOOK_HTML)
        self.assertEqual(extracted.title, "The Rock")
        self.assertEqual(extracted.titles, ["The Rock"])
        self.assertEqual(extracted.url, "http://www.imdb.com/title/tt0117500/")
        self.assertEqual(extracted.image, "http://ia.media-imdb.com/rock.jpg")
        self.assertEqual(extracted.images, ["http://ia.media-imdb.com/rock.jpg"])
        self.assertTrue(extracted.description, "A group of U.S. Marines, under command of a renegade general, take over Alcatraz and threaten San Francisco Bay with biological weapons.")
        self.assertEqual(len(extracted.descriptions), 1)

    def test_technique_twitter_meta_tags(self):
        # make sure the shuffled sequence does not lose any elements
        self.extractor.techniques = ["extraction.techniques.TwitterSummaryCardTags"]
        extracted = self.extractor.extract(TWITTER_HTML)
        self.assertEqual(extracted.title, "Parade of Fans for Houston's Funeral")
        self.assertEqual(extracted.titles, ["Parade of Fans for Houston's Funeral"])
        self.assertEqual(extracted.url, None)
        self.assertEqual(extracted.image, "http://graphics8.nytimes.com/images/2012/02/19/us/19whitney-span/19whitney-span-article.jpg")
        self.assertEqual(extracted.images, ["http://graphics8.nytimes.com/images/2012/02/19/us/19whitney-span/19whitney-span-article.jpg"])
        self.assertTrue(extracted.description, "NEWARK - The guest list and parade of limousines with celebrities emerging from them seemed more suited to a red carpet event in Hollywood or New York than than a gritty stretch of Sussex Avenue near the former site of the James M. Baxter Terrace public housing project here.")
        self.assertEqual(len(extracted.descriptions), 1)

    def test_technique_head_tags(self):
        "Test extracting page information from HTML head tags (meta, title, ...)."
        self.extractor.techniques = ["extraction.techniques.HeadTags"]
        extracted = self.extractor.extract(LETHAIN_COM_HTML, source_url="http://lethain.com/digg-v4-architecture-process/")
        self.assertEqual(extracted.title, "Digg v4's Architecture and Development Processes - Irrational Exuberance")
        self.assertEqual(extracted.url, "http://lethain.com/digg-v4-architecture-process/")
        self.assertEqual(extracted.image, None)
        self.assertEqual(extracted.description, "Will Larson's blog about programming and other things.")
        self.assertEqual(extracted.feed, "http://lethain.com/feeds/")
        self.assertEqual(extracted._unexpected_values['authors'], ["Will Larson"])

    def test_technique_semantic_tags(self):
        "Test extracting data from basic HTML tags like H1, H2, P, and IMG."
        self.extractor.techniques = ["extraction.techniques.SemanticTags"]
        extracted = self.extractor.extract(LETHAIN_COM_HTML)
        self.assertEqual(extracted.title, "Irrational Exuberance")
        self.assertEqual(extracted.url, None)
        self.assertEqual(extracted.image, "/static/blog/digg_v4/initial_org.png")
        self.assertEqual(len(extracted.images), 2)
        self.assertEqual(extracted.description.split(), "A month ago history reset with the second launch of Digg v1 , and memories are starting to fade since much of the Digg team joined SocialCode four months ago, so it seemed like a good time to describe the system and team architecture which ran and developed Digg.com from May 2010 until May 2012.".split())

    def test_technique_html_semantic_tags(self):
        "Test extracting data from an HTML5 page."
        self.extractor.techniques = ["extraction.techniques.HTML5SemanticTags"]
        extracted = self.extractor.extract(HTML5_HTML)
        self.assertEqual(extracted.title, 'This is a title')
        self.assertEqual(extracted.description, 'This is a description.')
        self.assertEqual(extracted.video, "this_is_a_video.mp4")
        self.assertEqual(extracted.videos, ["this_is_a_video.mp4"])

    def test_example_lethain_com_technique(self):
        "Test extracting data from lethain.com with a custom technique in extraction.examples."
        self.extractor.techniques = ["extraction.examples.custom_technique.LethainComTechnique"]
        extracted = self.extractor.extract(LETHAIN_COM_HTML)
        self.assertEqual(extracted.title, "Digg v4's Architecture and Development Processes")
        self.assertEqual(extracted.url, None)
        self.assertEqual(extracted._unexpected_values['tags'], [u'architecture', u'digg'])
        self.assertEqual(extracted._unexpected_values['dates'], [u'08/19/2012'])
        self.assertEqual(extracted.image, "/static/blog/digg_v4/initial_org.png")
        self.assertEqual(len(extracted.images), 2)
        self.assertEqual(extracted.description.split(), "A month ago history reset with the second launch of Digg v1 , and memories are starting to fade since much of the Digg team joined SocialCode four months ago, so it seemed like a good time to describe the system and team architecture which ran and developed Digg.com from May 2010 until May 2012.".split())

    def test_example_new_return_type(self):
        "Test returning a non-standard datatype, in this case addresses."
        self.extractor = AddressExtractor()
        self.extractor.techniques = ["extraction.examples.new_return_type.AddressTechnique"]
        extracted = self.extractor.extract(WILLARSON_COM_HTML)
        self.assertEqual(extracted.address, "Cole Valley San Francisco, CA USA")
        self.assertEqual(extracted.url, None)
        self.assertEqual(extracted.title, None)
        self.assertEqual(extracted.description, None)
        self.assertEqual(extracted.image, None)

    def test_empty_title(self):
        "Test that HTML with an empty title sets first h1 heading as title."
        extracted = self.extractor.extract(EMPTY_TITLE_HTML)
        self.assertEqual(extracted.title, "H1")

if __name__ == '__main__':
    unittest.main()
