import email
import email.policy
from dwg_mail_parser import DwgMailParser

class DwgMailReader:
    def read_from_file(self,fp):
        message = email.message_from_file(fp, policy=email.policy.default)
        self.subject = message['Subject']
        self.osm_user_names = [a.display_name for a in message['To'].addresses]

        if not self.osm_user_names:
            raise Exception("To: header not parseable")

        body=""
        for part in message.walk():
            if part.get_content_type() == 'text/html':
                body += part.get_content()

        body_parser = DwgMailParser()
        body_parser.feed(body)
        self.body = body_parser.body
