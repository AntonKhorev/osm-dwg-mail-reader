import unittest

# https://stackoverflow.com/a/11158224
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from dwg_mail_parser import DwgMailParser

def wrap_html(contents):
    return '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head><body>'+contents+'</body></html>'

class TestDwgMailParser(unittest.TestCase):
    def testEmptyBody(self):
        self.assertHtmlBody("","")
    def testBodyWithNewlines(self):
        self.assertHtmlBody("\nyes\n","<div>\nyes\n</div>\n")
    # def testAsterisk(self):
    #     self.assertHtmlBody("* whatever","\\* whatever")
    # def testTwoAsterisks(self):
    #     self.assertHtmlBody("* one\n* two","\\* one \\* two")
    # def testSpaces(self):
    #     self.assertHtmlBody("    indent"," indent") 
    def testBlockquote(self):
        self.assertHtmlBody(
            '<div style="border:none; border-left:solid blue 1.5pt; padding:0cm 0cm 0cm 4.0pt" type="cite">wat</div>',
            '<div>\n<blockquote>wat</blockquote>\n</div>\n'
        )
    def testHtmlBlock(self):
        self.assertHtmlBody(
            'here comes h3: <h3>header</h3>',
            '<div>\nhere comes h3: <h3>header</h3>\n</div>\n'
        )
    def testBrokenClosingDiv(self):
        self.assertHtmlBody(
            '</div>\n- haha\n- owned',
            '<div>\n- haha\n- owned\n</div>\n'
        )
    def assertHtmlBody(self,contents,expected):
        parser = DwgMailParser()
        parser.feed(wrap_html(contents))
        self.assertEqual(parser.body, expected)
