#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import (
    openstack_cloud_from_module,
    openstack_full_argument_spec,
    openstack_module_kwargs
)

import yaml


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: os_application_credentials
author:
  - Sofer Athlan-Guyot <sathlang@redhat.com>
version_added: '2.8'
short_description: create application credential.
notes: []
description:
  - create application credential
options:
  debug:
    description:
      - Whether or not debug is enabled.
    default: False
    required: False
    type: bool
  name:
    description:
      - name of the application.
    required: True
    type: str
  description:
    description:
      - description of application credential's purpose.
    default: None
    required: False
    type: str
  secret:
    description:
      - secret that application credential will be created with, if any.
        we cannot check if it has changed.  You need to destroy/create
        if you want to change it.
    default: None
    required: False
    type: str
  state:
    description:
      - which state: present, absent
    default: present
    required: False
    type: str
  project_id:
    description:
      - ID of the project
    required: True
    type: str
"""

EXAMPLES = """
- name: Special treatment for ovs upgrade.
  os_application_credentials:
    name: monitoring
"""

RETURN = """
json:
    description: json returned by the api
    returned: always
    type: json
changed:
    description: Was the ovs package update or not.
    returned: always
    type: bool
"""


def _exit(module, cloud, app_creds, diff, changed=True):
    redact_keys = ['secret']
    for k in redact_keys:
        if k in diff['before']:
            diff['before'][k] = '***'
        if k in diff['after']:
            diff['after'][k] = '***'

    module.exit_json(
        changed=changed,
        diff=diff,
        app_creds=app_creds,
        id=app_creds.get('id', None))


def _is_update_needed(module, app_creds):
    need_change = False
    options = yaml.safe_load(DOCUMENTATION)['options']
    # We don't have access to the secret from the api.
    for check in [x for x in options.keys()
                  if x not in ['debug', 'state', 'secret']]:
        if app_creds.get(check) != module.params[check]:
            need_change = True
            break
    return need_change


def _get_app_creds_vars(app_creds):
    return {
        'id': app_creds.id,
        'name': app_creds.name,
        'secret': app_creds.secret,
        'description': app_creds.description
    }


def _present_application_credentials(module, cloud):
    changed = False
    diff = {'before': '', 'after': ''}
    app_creds = cloud.identity.find_application_credential(
        cloud.current_user_id,
        module.params['name']
    )

    if not app_creds:
        app_creds = cloud.identity.create_application_credential(
            cloud.current_user_id,
            module.params['name'],
            secret=module.params['secret'],
            description=module.params['description'],
            project_id=module.params['project_id']
        )
        diff['after'] = _get_app_creds_vars(app_creds)

    if app_creds:
        diff['before'] = _get_app_creds_vars(app_creds)
        if _is_update_needed(module, app_creds):
            if module.check_mode:
                diff['after'] = {
                    'id': cloud.current_user_id,
                    'name': module.params['name'],
                    'secret': module.params['secret'],
                    'description': module.params['description'],
                }
            else:
                cloud.identity.delete_application_credential(
                    cloud.current_user_id,
                    app_creds
                )
                app_creds = cloud.identity.create_application_credential(
                    cloud.current_user_id,
                    module.params['name'],
                    secret=module.params['secret'],
                    description=module.params['description'],
                    project_id=module.params['project_id']
                )
                diff['after'] = _get_app_creds_vars(app_creds)

            changed = True

    _exit(module, cloud, app_creds, diff, changed)


def _delete_application_credentials(module, cloud):
    if module.check_mode:
        return True
    cloud.identity.delete_application_credential(
        cloud.current_user_id,
        module.params['name']
    )
    return True


def _absent_application_credentials(module, cloud):
    changed = False
    diff = {'before': '', 'after': ''}
    app_creds = cloud.identity.find_application_credential(
        cloud.current_user_id,
        module.params['name']
    )

    if app_creds:
        changed = _delete_application_credentials(module, cloud)

    module.exit_json(changed=changed, diff=diff, result='not present')


def main():
    module = AnsibleModule(
        openstack_full_argument_spec(
            **yaml.safe_load(DOCUMENTATION)['options']
        ),
        **openstack_module_kwargs()
    )
    state = module.params['state']

    result = dict(
        changed=False,
        success=False,
        json={},
    )
    sdk, cloud = openstack_cloud_from_module(module)

    try:
        if state == 'present':
            _present_application_credentials(module, cloud)
        if state == 'absent':
            _absent_application_credentials(module, cloud)
    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e), extra_data=e.extra_data)
    else:
        result['success'] = True
        module.exit_json(**result)


if __name__ == '__main__':
    main()
