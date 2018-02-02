# Copyright (c) 2018 Kristi Nikolla
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from email.mime import text
import email.utils
import smtplib

from ksproj import config

CONF = config.CONF

EMAIL = """Welcome,

You've been invited to join the {project} project in kaizen.massopen.cloud

To accept click the following link and login:
{link}

Best,
MOC Team
"""

author = CONF.email.author
password = CONF.email.password


def get_server():
    s = smtplib.SMTP_SSL(host=CONF.email.smtp)
    s.set_debuglevel(True)
    s.ehlo()
    # Note(knikolla): Our SMPT server is lying. It doesn't support CRAM-MD5
    s.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
    s.login(author, password)
    return s


def get_message(address, token, project):
    link = 'https://massopen.cloud/kaizen/signup/invitations/%s' % token
    msg = text.MIMEText(EMAIL.format(link=link, project=project))
    msg['To'] = address
    msg['From'] = email.utils.formataddr(('MOC Team', author))
    msg['Subject'] = 'MOC Project Invitation'
    return msg


def send(address, token, project):
    s = get_server()
    msg = get_message(address, token, project)

    try:
        s.sendmail(author, [address], msg.as_string())
    finally:
        s.quit()
