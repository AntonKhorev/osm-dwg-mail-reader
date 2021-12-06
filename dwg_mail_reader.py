import re
import email
from dwg_mail_parser import DwgMailParser

class DwgMailReader:
    def read_from_file(self, fp):
        message = email.message_from_file(fp)
        to_header = ''
        for s,e in email.header.decode_header(message.get('To')):
            if isinstance(s, str):
                to_header += s
            elif e:
                to_header += s.decode(e)
            else:
                to_header += s.decode('ASCII')

        self.subject = ''
        for s,e in email.header.decode_header(message.get('Subject')):
            if isinstance(s, str):
                self.subject += s
            elif e:
                self.subject += s.decode(e)
            else:
                self.subject += s.decode('ASCII')

        self.osm_user_names=[]

        for part in to_header.split(","):
            match = re.findall("^(.*) <", part)
            if match:
                self.osm_user_names.append(match[0].strip())

        if not self.osm_user_names:
            raise Exception("To: header not parseable")

        body=""
        for part in message.walk():
            if part.get_content_type() == 'text/html':
                charset = part.get_content_charset()
                if not charset:
                    charset = "utf-8"
                body = part.get_payload(decode=True).decode(charset)
        
        body_parser = DwgMailParser()
        body_parser.feed(body)
        self.body = body_parser.body
