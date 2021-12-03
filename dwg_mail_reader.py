import re
import email
import quopri
from dwg_mail_parser import DwgMailParser

class DwgMailReader:
    def readFromFile(self,fp):
        parsed = email.message_from_file(fp)
        to_header = ''
        for s,e in email.header.decode_header(parsed.get('To')):
            if isinstance(s, str):
                to_header += s
            elif e:
                to_header += s.decode(e)
            else:
                to_header += s.decode('ASCII')

        self.subject = ''
        for s,e in email.header.decode_header(parsed.get('Subject')):
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
        for part in parsed.walk():
            if part.get_content_type() == 'text/html':
                body = part.get_payload()
                match = re.findall("quoted", part.get("Content-Transfer-Encoding", ""))
                if match:
                    body = quopri.decodestring(body).decode("utf-8")
        
        body_parser = DwgMailParser()
        body_parser.feed(body)
        self.body = body_parser.body
