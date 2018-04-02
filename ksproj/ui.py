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

import os
from urllib import parse

import flask
import requests
from keystoneauth1 import identity
from keystoneauth1 import session

from ksproj.app import app
from ksproj import client
from ksproj import config
from ksproj import exceptions
from ksproj import oidc


# TODO(knikolla): Opportunity for caching the session.
def init_client(user_token, project=None):
    auth = identity.v3.Token(
        auth_url='https://192.168.0.8',
        token=user_token,
        project=project
    )
    return client.Client('http://localhost:50001', session.Session(auth))


def redirect_to_auth(return_to=None):
    return flask.redirect(
        os.path.join(flask.request.base_url,
                     'auth?%s' % parse.urlencode(return_to))
    )


@app.route('/auth', methods=['GET'])
def auth_view():
    token = flask.request.cookies.get('token', None)
    code = flask.request.args.get('code', None)

    redirect_uri = 'http://localhost:5000/auth'
    return_to = flask.request.args.get('return_to', None)
    if return_to:
        redirect_uri = '%s?return_to=%s' % (redirect_uri, return_to)
    if not token and not code:
        return flask.redirect(oidc.get_redirect_url(redirect_uri))
    elif code:
        try:
            access_token = oidc.get_access_token(code, redirect_uri)
        except exceptions.OIDCAuthenticationException:
            return flask.render_template('accepted.html', response="Error Authenticating.")

        #u = identity.UserIdentity.from_access_token(access_token)
        resp = flask.make_response(
            flask.redirect(return_to)
        )
        resp.set_cookie('token', u.session.get_token())
        resp.set_cookie('access_token', access_token)
        return resp


@app.route('/logout', methods=['GET'])
def logout():
    resp = flask.make_response(
        flask.redirect(oidc.get_logout_url('http://localhost:5000/projects'))
    )
    resp.set_cookie('token', '', expires=0)
    resp.set_cookie('access_token', '', expires=0)
    return resp


@app.route('/projects', methods=['GET'])
def project_list_view():
    token = flask.request.cookies.get('token', None)
    if not token:
        return redirect_to_auth('projects')

    client = init_client(token)
    projects = client.list_projects()

    if not projects:
        flask.abort(401)

    return flask.render_template('project.html',
                                 project=None,
                                 projects=projects)


@app.route('/projects/<project>', methods=['GET'])
def project_view(project):
    token = flask.request.cookies.get('token', None)
    if not token:
        return flask.redirect('../auth?return_to=projects/%s' % project)

    session = identity.UserIdentity(token=token, project=project)
    admin_session = identity.client()

    users = admin_session.get_users_in_project()
    projects = session.get_projects()

    return flask.render_template('project.html',
                                 project=project,
                                 projects=projects,
                                 users=users)


@app.route('/projects/invite', methods=['POST'])
def invite():
    token = flask.request.cookies.get('token', None)
    if not token:
        return flask.redirect('../auth?redirect_url=projects/')

    project = flask.request.form('project')
    email = flask.request.form('email')
    r = requests.put('http://localhost:5000/api/projects/%s/invitations/%s' % (project, email),
                     headers={'x-auth-token': token})


if __name__ == '__main__':
    config.load_config()
    app.run(host='0.0.0.0', threaded=True)
