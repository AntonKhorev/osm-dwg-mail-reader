from html.parser import HTMLParser

class DwgMailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.body = ""
        self.in_body = False
        self.div_stack = []
        self.started_output = False
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
            if not self.started_output:
                self.started_output = True
                self.body += '<div>\n' # trigger html mode until the end of the document, don't need to balance this tag
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
        if self.in_body:
            if tag == 'div' and len(self.div_stack) > 0:
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
