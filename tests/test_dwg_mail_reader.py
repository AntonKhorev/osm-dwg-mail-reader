import unittest
import textwrap
import io
import email.mime.multipart
import email.mime.text

# https://stackoverflow.com/a/11158224
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from dwg_mail_reader import DwgMailReader

def make_mail(From, To, Subject, plain, html):
    # message = email.mime.multipart.MIMEMultipart(boundary='multipartboundary')
    message = email.mime.multipart.MIMEMultipart()
    message['From'] = From
    message['To'] = To
    message['Subject'] = Subject
    plain_message = email.mime.text.MIMEText(plain)
    html_message = email.mime.text.MIMEText(html, 'html')
    message.attach(plain_message)
    message.attach(html_message)
    # print(str(message))
    return message

def read_mail(From, To, Subject, plain, html):
    message = make_mail(From, To, Subject, plain, html)
    fp = io.StringIO(str(message))
    mail = DwgMailReader()
    mail.read_from_file(fp)
    return mail

def wrap_html(contents):
    dedented = textwrap.dedent(contents)
    return '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head><body>'+dedented+'</body></html>'

class TestDwgMailReader(unittest.TestCase):
    def testSimpleMail(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Some Username <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")',
            textwrap.dedent('''\
                # Header
                
                * one
                * two
                * three
            '''),
            wrap_html('''\
                <h1>Header</h1>
                <ul>
                <li>one
                <li>two
                <li>three
                </ul>
                </body></html>
            ''')
        )
        self.assertEqual(mail.osm_user_names, ['Some Username'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")')
        self.assertEqual(mail.body, textwrap.dedent('''\
                <div>
                <h1>Header</h1>
                <ul>
                <li>one
                <li>two
                <li>three
                </ul>
                </div>
        '''))
    def testCyrillicUtf8Base64(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Some Username <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")',
            'русский',
            wrap_html('<p>русский</p>')
        )
        self.assertEqual(mail.osm_user_names, ['Some Username'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p>русский</p>
            </div>
        '''))
