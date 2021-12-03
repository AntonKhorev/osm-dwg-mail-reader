#!/usr/bin/python3
# -*- coding: UTF8 -*-

import urllib3
import sys
import re
import email
import quopri

if (sys.version_info.major < 3):
    raise Exception("needs python 3")

parsed = email.message_from_file(sys.stdin)
to_header = ''
for s,e in email.header.decode_header(parsed.get('To')):
    if isinstance(s, str):
        to_header += s
    elif e:
        to_header += s.decode(e)
    else:
        to_header += s.decode('ASCII')

subject = ''
for s,e in email.header.decode_header(parsed.get('Subject')):
    if isinstance(s, str):
        subject += s
    elif e:
        subject += s.decode(e)
    else:
        subject += s.decode('ASCII')

osm_user_names=[]

for part in to_header.split(","):
    match = re.findall("^(.*) <", part)
    if match:
        osm_user_names.append(match[0].strip())

if not osm_user_names:
    raise Exception("To: header not parseable")

body=""
for part in parsed.walk():
    if part.get_content_type() == 'text/plain':
        body = part.get_payload()
        match = re.findall("quoted", part.get("Content-Transfer-Encoding", ""))
        if match:
           body = quopri.decodestring(body).decode("latin1")
#           print(body)
