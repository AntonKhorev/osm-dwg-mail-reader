import re
from html.parser import HTMLParser

ESCAPED_CHAR_RE = r'''(\$\$|[\\*_`\[\]\{"'|])|^[ ]{0,3}(:)'''
def kramdown_replace(matchobj):
    return "\\" + (matchobj.group(1) or matchobj.group(2))

def is_span_level(tag):
    return tag in '''
        a abbr acronym b big bdo br button cite code del dfn em i img input
        ins kbd label option q rb rbc rp rt rtc ruby samp select small span
        strong sub sup textarea tt var
    '''

class DwgMailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.body = ""
        self.inBody = False
        self.divStack = []
    def prepend_to_starttag(self, tag):
        if len(self.body) <= 0:
            return
        if self.body[-1] == '\n':
            return
        if not is_span_level(tag):
            self.body += '\n'
    def append_to_endtag(self, tag):
        if not is_span_level(tag):
            self.body += '\n'
    def handle_startendtag(self, tag, attrs):
        if self.inBody:
            self.prepend_to_starttag(tag)
            self.body += self.get_starttag_text()
            self.append_to_endtag(tag)
    def handle_starttag(self, tag, attrs):
        if self.inBody:
            self.prepend_to_starttag(tag)
            if tag == 'div':
                for k,v in attrs:
                    if k == 'type' and v == 'cite':
                        self.divStack.append('blockquote')
                        self.body += '<blockquote>'
                        return
                else:
                    self.divStack.append('div')
            self.body += self.get_starttag_text()
        if tag == 'body':
            self.inBody = True
    def handle_endtag(self, tag):
        if tag == 'body':
            self.inBody = False
        if self.inBody:
            if tag == 'div' and len(self.divStack) > 0:
                self.body += '</'+self.divStack.pop()+'>'
            else:
                self.body += '</'+tag+'>'
            self.append_to_endtag(tag)
    def handle_data(self, data):
        if self.inBody:
            space_collapsed_data = re.sub(r"\s+", ' ', data)
            escaped_data = re.sub(ESCAPED_CHAR_RE, kramdown_replace, space_collapsed_data)
            self.body += escaped_data
    def handle_entityref(self, name):
        if self.inBody:
            self.body += '&'+name+';'
    def handle_charref(self, name):
        if self.inBody:
            self.body += '&#'+name+';'
