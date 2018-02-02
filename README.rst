======
ksproj
======

User invitation system for OpenStack.

Ksproj allows cloud administrators and users with the ``project_admin`` role on
an OpenStack project to invite users via their email address.

The invited user will be emailed a unique link, containing an invitation
token. Upon visiting the link they will be prompted to log in to OpenStack
with their credentials, and to accept the terms of service, after which
the account with which they will log in with, will be assigned a role
on the project they were invited on.

Invitation tokens are single use, and an email cannot be invited more than
once.

API
===

All API operations require an OpenStack token in the ``x-auth-token`` header.
To get a token, use ``openstack token issue -f value -c id`` or instantiate
a ``keystoneauth1`` session.

.. code-block::

    # CRUD for invitations
    PUT     /api/projects/<project_name_or_id>/invitations/<email>
    GET     /api/projects/<project_name_or_id>/invitations/<email>
    DELETE  /api/projects/<project_name_or_id>/invitations/<email>

    # Batch invite, request body is json dictionary of emails (see example)
    PATCH   /api/projects/<project_name_or_id>/invitations

    # List all invitations
    GET     /api/projects/<project_name_or_id>/invitations

    # Accept an invitation
    POST    /api/invitations/<invitation_token>


A simple UI for browser usage is also provided for accepting invitations.

.. code-block::

    GET     /invitations/<invitation_token>


Sample Usage
============

.. code-block::

    # Invite test@example.com to admin project
    curl -X PUT -H 'x-auth-token: <OS_TOKEN>' <host>/api/projects/admin/invitations/test@example.com
    # Sample Response
    {"invitation": {
        "project": "91710cf57c65463b915fd91b12c88a7d",
        "invited_on": "2018-01-26 21:52:52.178542",
        "token": "f190a3fb6798441b92e3bc4d9c7850c3",
        "role": "Member",
        "links": {"self": "HOSTNAME/projects/91710cf57c65463b915fd91b12c88a7d/invitations/test@example.com",
                  "accept": "HOSTNAME/invitations/f190a3fb6798441b92e3bc4d9c7850c3"},
        "accepted_on": "None", "status": "PENDING",
        "email": "test@example.com",
        "accepted_by": null,
        "invited_by": "0086e585719644b68fe8fb0685c53a4b"
    }}

    # Invite multiple emails to project
    curl -X PATCH -H 'x-auth-token: <OS_TOKEN>' -d '["1@example.com", "2@example.com"]' \
        <host>/api/projects/admin/invitations/test@example.com
