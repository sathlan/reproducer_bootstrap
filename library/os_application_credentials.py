#!/usr/bin/python
# coding: utf-8 -*-

# Copyright (c) 2020, Sofer Athlan-Guyot <sathlang@redhat.com>
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule

import yaml


DOCUMENTATION = '''
---
module: os_application_credentials
short_description: Manage application credentials in openstack.
author: OpenStack Ansible SIG
description:
  - Manage application credentials in openstack.
options:
  name:
    description:
    - name of the application credential.
    required: true
    type: str
  description:
    description:
    - description of application credential's purpose.
    default: None
    required: false
    type: str
  secret:
    description:
    - secret that application credential will be created with, if
      any. we cannot check if it has changed.  You need to
      destroy/create if you want to change it.
    default: None
    required: false
    type: str
  state:
    description:
    - which state: present, absent
    default: present
    required: false
    type: str
  project_id:
    description:
    - ID of the project
    required: false
    default: None
    type: str

requirements:
  - "python >= 3.6"
  - "openstacksdk"

extends_documentation_fragment:
  - openstack.cloud.openstack
'''

RETURN = '''
json:
  description: json returned by the api
  returned: always
  type: json
changed:
  description: Was the ovs package update or not.
  returned: always
  type: bool

'''

EXAMPLES = '''
# What modules does for example
- os_application_credentials:
    action: pause
    auth:
      auth_url: https://identity.example.com
      username: admin
      password: admin
      project_name: admin
    server: vm1
    timeout: 200
'''


class OsApplicationCredentialsModule(OpenStackModule):

    argument_spec = yaml.safe_load(DOCUMENTATION)['options']
    module_kwargs = dict(
        required_if=[
            ["state", "present", ["name", "project_id"]],
            ["state", "absent", ["name"]],
        ],
        supports_check_mode=True,
    )

    # you main funciton is here
    def run(self):
        """Create, delete or update the application credentials. """
        self.diff = {}

        self.app_creds = self.conn.identity.find_application_credential(
            self.conn.current_user_id,
            self.params['name']
        )
        # check if we need to run or the resource is in desired state already
        must_run = self.check_mode_test()
        if not must_run:
            return {'diff': self.diff,
                    'changed': False}

        return self.execute()

    def check_mode_test(self):
        # check the idempotency - does module should do anything or
        # it's already in the desired state?
        must_run = False

        if not self.app_creds:
            # No application credential found.
            self.diff['before'] = {}
            if self.params['state'] == 'absent':
                self.diff['after'] = {}
            else:
                must_run = True
        else:
            # Application credential found.
            self.diff['before'] = self._get_app_creds_vars(self.app_creds)
            if self._need_update():
                must_run = True
            else:
                self.diff['after'] = self._get_app_creds_vars(self.app_creds)

        # Take check_mode into account.
        if must_run and self.ansible.check_mode:
            self.diff['after'] = self._get_app_creds_vars(self.params)
            must_run = False

        return must_run

    def execute(self):
        actions_map = {
            'present': self._present_resource,
            'absent': self._absent_resource,
        }
        actions_map[self.params['state']]()
        self.diff['after'] = self._get_app_creds_vars(self.app_creds)
        return {'changed': True,
                'diff': self.diff,
                'app_creds': self.app_creds,
                'id': self.app_creds['id']}

    def _present_resource(self):
        params = [self.conn.current_user_id, self.params['name']]
        kwargs = {
            'secret': self.params['secret'],
            'description': self.params['description'],
            'project_id': self.params['project_id']
        }
        if self.app_creds:
            # Update, done by delete/create
            self._absent_resource()

        self.app_creds = self.conn.identity.create_application_credential(
            *params, **kwargs,
        )

    def _absent_resource(self):
        # We reach here only if the resource already exist.
        self.conn.identity.delete_application_credential(
            self.conn.current_user_id,
            self.app_creds['id']
        )

    def _need_update(self):
        need_update = False
        options = yaml.safe_load(DOCUMENTATION)['options']
        for check in [x for x in options.keys()
                      if x not in ['state', 'secret']]:
            if self.app_creds.get(check) != self.params[check]:
                need_update = True
                break
        return need_update

    @staticmethod
    def _get_app_creds_vars(app_creds):
        info = {}
        for col in ['description', 'id', 'name', 'project_id']:
            if col in app_creds:
                info.update({col: app_creds.get(col)})
        if 'secret' in app_creds:
            info.update({'secret': '***'})
        return info


def main():
    module = OsApplicationCredentialsModule()
    module()


if __name__ == '__main__':
    main()
