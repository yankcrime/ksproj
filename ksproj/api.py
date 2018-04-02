# Copyright (c) 2017 Kristi Nikolla
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

import flask
from flask import redirect
import requests

from ksproj.app import app
from ksproj import config
from ksproj import exceptions
from ksproj import manager


@app.route('/invitations/<token>', methods=['GET', 'POST'])
def accept_ui(token):
        return flask.render_template('accept.html',
                                     invitation=token)


@app.route('/invitations/accept', methods=['POST'])
def accept_ui_post():
    # Mote(knikolla): Must store these in the cookies, as they will not be
    # preserved after the redirect back from keystone.
    accepted = flask.request.form.get(
        'accept_eula',
        flask.request.cookies.get('accept_eula', None)
    )
    if not accepted:
        return flask.render_template('accepted.html',
                                     response='Must accept EULA.')
    invitation = flask.request.form.get(
        'invitation',
        flask.request.cookies.get('invitation', None)
    )
    if not accepted:
        return flask.render_template('accepted.html',
                                     response='Must accept EULA.')
    if not invitation:
        return flask.render_template('accepted.html',
                                     response='No invitation.')

    token = flask.request.form.get('token', None)
    if not token:
        resp = flask.make_response(
            redirect(('https://kaizen.massopen.cloud:5000'
                      '/v3/auth/OS-FEDERATION/identity_providers/moc'
                      '/protocols/openid/websso'
                      '?origin=https://massopen.cloud'
                      '/kaizen/signup/invitations/accept'))
        )
        resp.set_cookie('accept_eula', accepted)
        resp.set_cookie('invitation', invitation)
        return resp

    r = requests.post('http://localhost:5000/api/invitations/%s' % invitation,
                      headers={'x-auth-token': token})
    if r.status_code == 204:
        response = 'Succesfully accepted invitation'
    else:
        response = r.text
    return flask.render_template('accepted.html', response=response)


@app.route('/api/projects/<project>/invitations/<email>', methods=['PUT'])
def invite(project, email):
    # TODO(knikolla): This try,except is the same for all, write a decorator.
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        invitation = m.invite(project, email, send_email=True)
        return json.dumps({'invitation': invitation})
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/projects/<project>/invitations', methods=['PATCH'])
def bulk_invite(project):
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        emails = json.loads(flask.request.data)
        m.bulk_invite(project, emails, send_email=True)
        return '', 204
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/invitations/<token>', methods=['POST'])
def accept(token):
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        m.accept(token)
        return '', 204
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/projects/<project>/invitations', methods=['GET'])
def list_invitations(project):
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        return json.dumps({'invitations': m.list_invitations(project)})
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/projects/<project>/invitations/<email>', methods=['GET'])
def get_invitation(project, email):
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        return json.dumps({'invitations': m.get_invitation(project, email)})
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/projects/<project>/invitations/<email>', methods=['DELETE'])
def delete_inviation(project, email):
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        m.delete_invitation(project, email)
        return '', 204
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/projects/<project>/users', methods=['GET'])
def list_users(project):
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        return json.dumps({'users': m.list_users(project)})
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


@app.route('/api/projects', methods=['GET'])
def list_projects():
    try:
        m = manager.Manager(flask.request.headers.get('x-auth-token', None))
        return json.dumps({'projects': m.list_projects()})
    except exceptions.InternalException as e:
        return e.MESSAGE, e.STATUS_CODE


if __name__ == '__main__':
    config.load_config()
    app.run(host='0.0.0.0', threaded=True)
