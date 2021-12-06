from html.parser import HTMLParser

class _DwgMailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.body = ""
        self.in_body = False
        self.div_stack = []
    def handle_startendtag(self, tag, attrs):
        if self.in_body:
            self.body += self.get_starttag_text()
    def handle_starttag(self, tag, attrs):
        if self.in_body:
            if tag == 'div':
                for k,v in attrs:
                    if k == 'type' and v == 'cite':
                        self.div_stack.append('blockquote')
                        self.body += '<blockquote>'
                        return
                else:
                    self.div_stack.append('div')
            self.body += self.get_starttag_text()
        if tag == 'body':
            self.in_body = True
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
        if self.in_body:
            if tag == 'div':
                if len(self.div_stack) > 0: # make sure there aren't more closing divs than opening divs because need everything inside wrapper div
                    self.body += '</'+self.div_stack.pop()+'>'
            else:
                self.body += '</'+tag+'>'
    def handle_data(self, data):
        if self.in_body:
            self.body += data
    def handle_entityref(self, name):
        if self.in_body:
            self.body += '&'+name+';'
    def handle_charref(self, name):
        if self.in_body:
            self.body += '&#'+name+';'

class DwgMailParser(HTMLParser):
    def __init__(self):
        self.parser = _DwgMailParser()
    def feed(self,data):
        self.parser.feed(data)
    @property
    def body(self):
        if len(self.parser.body) <= 0:
            return ''
        result = '<div>' # trigger html mode in kramdown
        if self.parser.body[0] != '\n':
            result += '\n'
        result += self.parser.body
        if self.parser.body[-1] != '\n':
            result += '\n'
        result += '</div>\n'
        return result
