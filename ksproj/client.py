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
import os


class Client(object):
    def __init__(self, url, session):
        """Initialize ksproj client.

        :param: url: string with url of ksproj API
        :param session: keystoneauth1.session.Session
        """
        self.url = url
        self.session = session

    def construct_url(self, *args):
        return os.path.join(self.url, os.path.join(*args))

    @staticmethod
    def prepare_response(response):
        if response.text:
            return json.loads(response.text)

    def accept(self, token):
        path = self.construct_url('invitations', token)
        return self.prepare_response(self.session.post(path))

    def invite(self, project, email):
        path = self.construct_url('projects', project, 'invitations', email)
        return self.prepare_response(self.session.put(path))

    def cancel_invite(self, project, email):
        path = self.construct_url('projects', project, 'invitations', email)
        return self.prepare_response(self.session.delete(path))

    def view_invite(self, project, email):
        path = self.construct_url('projects', project, 'invitations', email)
        return self.prepare_response(self.session.get(path))

    def bulk_invite(self, project, email_list):
        path = self.construct_url('projects', project, 'invitations')
        return self.prepare_response(self.session.post(path, body=email_list))

    def list_invitations(self, project):
        path = self.construct_url('projects', project, 'invitations')
        return self.prepare_response(self.session.get(path))

    def list_users(self, project):
        path = self.construct_url('projects', project, 'users')
        return self.prepare_response(self.session.get(path))

    # Note(knikolla): This makes an API call to keystone rather than ksproj.
    def list_projects(self):
        path = os.path.join(self.session.auth.auth_url, 'auth', 'projects')
        return json.loads(self.session.get(path))['projects']
