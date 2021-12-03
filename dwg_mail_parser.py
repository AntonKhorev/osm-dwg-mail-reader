import re
from html.parser import HTMLParser

class DwgMailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.body = ""
        self.inBody = False
        self.divStack = []
    def handle_startendtag(self, tag, attrs):
        if self.inBody:
            self.body += self.get_starttag_text()
    def handle_starttag(self, tag, attrs):
        if self.inBody:
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
    def handle_data(self, data):
        ESCAPED_CHAR_RE = r'''(\$\$|[\\*_`\[\]\{"'|])|^[ ]{0,3}(:)'''
        def kramdown_escape(matchobj):
            return "\\" + (matchobj.group(1) or matchobj.group(2))
        if self.inBody:
            space_collapsed_data = re.sub(r"\s+", ' ', data)
            escaped_data = re.sub(ESCAPED_CHAR_RE, kramdown_escape, space_collapsed_data)
            self.body += escaped_data
    def handle_entityref(self, name):
        if self.inBody:
            self.body += '&'+name+';'
    def handle_charref(self, name):
        if self.inBody:
            self.body += '&#'+name+';'
