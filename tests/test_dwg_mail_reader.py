import unittest
import textwrap
import io
import quopri
import email.mime.multipart
import email.mime.text
import email.policy
import email.headerregistry

# https://stackoverflow.com/a/11158224
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from dwg_mail_reader import DwgMailReader

# osm usernames can contain anything but these chars /;.,?%#

def make_quopri_message(text, subtype='plain', charset='utf-8'):
    message = email.mime.text.MIMEText('', subtype, charset)
    message.set_payload(quopri.encodestring(text.encode(charset)))
    del message['Content-Transfer-Encoding']
    message['Content-Transfer-Encoding'] = 'quoted-printable'
    return message

def make_mail(From, To, Subject, plain, html):
    # message = email.mime.multipart.MIMEMultipart(boundary='multipartboundary')
    message = email.mime.multipart.MIMEMultipart(policy=email.policy.default)
    if From: message['From'] = From
    if To: message['To'] = To
    if Subject: message['Subject'] = Subject
    if isinstance(plain, str):
        plain_message = email.mime.text.MIMEText(plain, policy=email.policy.default)
    else:
        plain_message = plain
    if isinstance(html, str):
        html_message = email.mime.text.MIMEText(html, 'html', policy=email.policy.default)
    else:
        html_message = html
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
    def testMultipleTos(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Fred <fwd@dwgmail.info>, John <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111',
            'OK',
            wrap_html('<p>OK</p>')
        )
        self.assertEqual(mail.osm_user_names, ['Fred','John'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p>OK</p>
            </div>
        '''))
    def testToWithAngleBrackets(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            email.headerregistry.Address('LOL <owned>', 'fwd', 'dwgmail.info'),
            'Re: [Ticket#2021112500000000] Issue #11111',
            'OK',
            wrap_html('<p>OK</p>')
        )
        self.assertEqual(mail.osm_user_names, ['LOL <owned>'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p>OK</p>
            </div>
        '''))
    def testCyrillicUtf8Base64(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Some Username <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111',
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
    def testCyrillicUtf8Quopri(self):
        plain_message = email.mime.text.MIMEText('','plain','utf-8')
        plain_message.set_payload(quopri.encodestring(
            '*русский* language'.encode('utf-8')
        ))
        del plain_message['Content-Transfer-Encoding']
        plain_message['Content-Transfer-Encoding']='quoted-printable'
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Some Username <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")',
            make_quopri_message('*русский* language'),
            make_quopri_message(wrap_html('<p><em>русский</em> language</p>'),'html')
        )
        self.assertEqual(mail.osm_user_names, ['Some Username'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p><em>русский</em> language</p>
            </div>
        '''))
    def testCyrillicHeaders(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Вася <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111 (User "Петя")',
            'OK',
            wrap_html('<p>OK</p>')
        )
        self.assertEqual(mail.osm_user_names, ['Вася'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111 (User "Петя")')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p>OK</p>
            </div>
        '''))
    def testAccentedHeaders(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Iváns <fwd@dwgmail.info>',
            'Re: [Ticket#2021112500000000] Issue #11111',
            'OK',
            wrap_html('<p>OK</p>')
        )
        self.assertEqual(mail.osm_user_names, ['Iváns'])
        self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p>OK</p>
            </div>
        '''))
    # def testMissingTo(self):
    #     mail = read_mail(
    #         'Data Working Group <data@otrs.openstreetmap.org>',
    #         None,
    #         'Re: [Ticket#2021112500000000] Issue #11111',
    #         'OK',
    #         wrap_html('<p>OK</p>')
    #     )
    #     self.assertEqual(mail.osm_user_names, [])
    #     self.assertEqual(mail.subject, 'Re: [Ticket#2021112500000000] Issue #11111')
    #     self.assertEqual(mail.body, textwrap.dedent('''\
    #         <div>
    #         <p>OK</p>
    #         </div>
    #     '''))
    def testMissingSubject(self):
        mail = read_mail(
            'Data Working Group <data@otrs.openstreetmap.org>',
            'Some Username <fwd@dwgmail.info>',
            None,
            'OK',
            wrap_html('<p>OK</p>')
        )
        self.assertEqual(mail.osm_user_names, ['Some Username'])
        # self.assertEqual(mail.subject, '')
        self.assertEqual(mail.body, textwrap.dedent('''\
            <div>
            <p>OK</p>
            </div>
        '''))

if __name__ == "__main__":
    unittest.main()
