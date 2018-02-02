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

import datetime

from flask_sqlalchemy import SQLAlchemy

from ksproj.app import app
from ksproj import exceptions

db = SQLAlchemy(app)


class Invitation(db.Model):
    __tablename__ = 'invitations'
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(60), nullable=False)  # Note: not exposed yet
    token = db.Column(db.String(60), nullable=False)
    invited_by = db.Column(db.String(60), nullable=False)
    invited_on = db.Column(db.DateTime, nullable=False)
    accepted_by = db.Column(db.String(60))
    accepted_on = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint('project', 'email', name='uix_1'),)

    def __init__(self, project, email, role, token, invited_by):
        self.project = project
        self.email = email
        self.role = role
        self.token = token
        self.invited_by = invited_by
        self.invited_on = datetime.datetime.now()

    def set_accepted(self, user):
        self.accepted_by = user
        self.accepted_on = datetime.datetime.now()
        db.session.commit()

    def to_dict(self):
        return {
            'email': self.email,
            'project': self.project,
            'role': self.role,
            'token': self.token,
            'invited_by': self.invited_by,
            'invited_on': str(self.invited_on),
            'status': 'PENDING' if not self.accepted_by else 'ACCEPTED',
            'accepted_by': self.accepted_by,
            'accepted_on': str(self.accepted_on),
            'links': {
                'self': 'HOSTNAME/projects/%s/invitations/%s' % (self.project,
                                                                 self.email),
                'accept': 'HOSTNAME/invitations/%s' % self.token
            }
        }

    @classmethod
    def list_by_project(cls, project):
        return cls.query.filter_by(project=project).all()

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter_by(token=token).first()

    @classmethod
    def find_by_project_and_email(cls, project, email):
        return cls.query.filter_by(
            project=project,
            email=email
        ).first()

    @classmethod
    def add(cls, invitation):
        existing = cls.query.filter_by(project=invitation.project,
                                       email=invitation.email,
                                       role=invitation.role).first()
        if existing:
            raise exceptions.DuplicateError
        add(invitation)


def add(entity):
    db.session.add(entity)
    db.session.commit()


def delete(entity):
    db.session.delete(entity)
    db.session.commit()


db.create_all()
