import email.mime.multipart
import email.mime.text

message = email.mime.multipart.MIMEMultipart(boundary='multipartboundary')
message['From']='Data Working Group <data@otrs.openstreetmap.org>'
message['To']='Some Username <fwd@dwgmail.info>'
message['Subject']='Re: [Ticket#2021112500000000] Issue #11111 (User "Other Username")'
plaintext_message = email.mime.text.MIMEText('''# Header

* one
* two
* three''')
html_message = email.mime.text.MIMEText('''<h1>Header</h1>
<ul>
<li>one
<li>two
<li>three
</ul>''')
message.attach(plaintext_message)
message.attach(html_message)
print(str(message))
