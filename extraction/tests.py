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



if __name__ == '__main__':
    unittest.main()
