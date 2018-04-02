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

import json
from urllib import parse

import requests

from ksproj import config
from ksproj import exceptions

CONF = config.CONF


def get_redirect_url(redirect_uri):
    params = {
        'response_type': 'code',
        'client_id': CONF.oidc.client_id,
        'scope': 'openid email profile',
        'redirect_uri': redirect_uri
    }
    params = parse.urlencode(params)
    return '%s?%s' % (CONF.oidc.authorization_endpoint, params)


def get_logout_url(redirect_uri):
    params = {
        'redirect_uri': redirect_uri
    }
    params = parse.urlencode(params)
    return '%s?%s' % (CONF.oidc.logout_endpoint, params)


def get_access_token(authorization_code, redirect_uri):
    code = parse.unquote(authorization_code)
    r = requests.post(
        CONF.oidc.token_endpoint,
        data={
            'grant_type': 'authorization_code',
            'client_id': CONF.oidc.client_id,
            'client_secret': CONF.oidc.client_secret,
            'redirect_uri': redirect_uri,
            'code': code,
        }
    )
    if not r.status_code == 200:
        raise exceptions.OIDCAuthenticationException

    return json.loads(r.text)['access_token']
