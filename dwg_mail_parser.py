from html.parser import HTMLParser

class _DwgMailParser(HTMLParser):
    def __init__(self, body_depth=0):
        super().__init__(convert_charrefs=False)
        self.body = ""
        self.body_depth = body_depth
        self.body_count = 0
        self.div_stack = []
    def handle_startendtag(self, tag, attrs):
        if self.body_depth > 0:
            self.body += self.get_starttag_text()
    def handle_starttag(self, tag, attrs):
        if self.body_depth > 0:
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
            self.body_depth += 1
            self.body_count += 1
    def handle_endtag(self, tag):
        if tag == 'body':
            self.body_depth -= 1
        if self.body_depth > 0:
            if tag == 'div':
                if len(self.div_stack) > 0: # make sure there aren't more closing divs than opening divs because need everything inside wrapper div
                    self.body += '</'+self.div_stack.pop()+'>'
            else:
                self.body += '</'+tag+'>'
    def handle_data(self, data):
        if self.body_depth > 0:
            self.body += data
    def handle_entityref(self, name):
        if self.body_depth > 0:
            self.body += '&'+name+';'
    def handle_charref(self, name):
        if self.body_depth > 0:
            self.body += '&#'+name+';'

class DwgMailParser(HTMLParser):
    def __init__(self):
        self.parser = _DwgMailParser()
        self.parser_no_body = _DwgMailParser(1)
    def feed(self,data):
        self.parser.feed(data)
        self.parser_no_body.feed(data)
    @property
    def body(self):
        def wrap_with_div(input):
            if len(input) <= 0:
                return ''
            result = '<div>' # trigger html mode in kramdown
            if input[0] != '\n':
                result += '\n'
            result += input
            if input[-1] != '\n':
                result += '\n'
            result += '</div>\n'
            return result
        if self.parser.body_count > 0:
            return wrap_with_div(self.parser.body)
        else:
            return wrap_with_div(self.parser_no_body.body)
