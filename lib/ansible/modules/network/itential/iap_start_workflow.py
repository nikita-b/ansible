#!/usr/bin/python

# Copyright: (c) 2018, Itential <opensource@itential.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This module provides the ability to start a workflow from Itential Automation Platform
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: iap_start_workflow
version_added: "2.8"
author: "Itential (@cma0) <opensource@itential.com>"
short_description: Start a workflow in the Itential Automation Platform
description:
  - This will start a specified workflow in the Itential Automation Platform with given arguments.
options:
  iap_port:
    description:
      - Provide the port number for the Itential Automation Platform
    required: true
    type: str
    default: null

  iap_fqdn:
    description:
      - Provide the fqdn for the Itential Automation Platform
    required: true
    type: str
    default: null

  token_key:
    description:
      - Token key generated by iap_token module for the Itential Automation Platform
    required: true
    type: str
    default: null

  workflow_name:
    description:
      - Provide the workflow name
    required: true
    type: str
    default: null

  description:
    description:
      - Provide the description for the workflow
    required: true
    type: str
    default: null

  variables:
    description:
      - Provide the values to the job variables
    required: true
    type: dict
    default: null

  https:
    description:
      - Use HTTPS to connect
      - By default using http
    type: bool
    default: False

  validate_certs:
    description:
      - If C(no), SSL certificates for the target url will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    type: bool
    default: False
'''

EXAMPLES = '''
- name: Start a workflow in the Itential Automation Platform
  iap_start_workflow:
    iap_port: 3000
    iap_fqdn: localhost
    token_key: "DFSFSFHFGFGF[DSFSFAADAFASD%3D"
    workflow_name: "RouterUpgradeWorkflow"
    description: "OS-Router-Upgrade"
    variables: {"deviceName":"ASR9K"}
  register: result

- debug: var=result
'''

RETURN = '''
response:
    description: The result contains the response from the call
    type: dict
    returned: always
msg:
    description: The msg will contain the error code or status of the workflow
    type: str
    returned: always
'''

# Ansible imports
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

# Standard library imports
import json


def start_workflow(module):
    """
    :param module:
    :return: response and msg
    """
    # By default this will be http.
    # By default when using https, self signed certificate is used
    # If https needs to pass certificate then use validate_certs as true
    if module.params['https']:
        transport_protocol = 'https'
    else:
        transport_protocol = 'http'

    application_token = str(module.params['token_key'])
    url = str(transport_protocol) + "://" + str(module.params['iap_fqdn']) + ":" + str(module.params[
        'iap_port']) + "/workflow_engine/startJobWithOptions/" \
        + str(module.params['workflow_name']) + "?token=" + str(application_token)
    options = {
        "variables": module.params['variables'],
        "description": str(module.params['description'])
    }

    payload = {
        "workflow": module.params['workflow_name'],
        "options": options
    }

    json_body = module.jsonify(payload)
    headers = dict()
    headers['Content-Type'] = 'application/json'

    # Using fetch url instead of requests
    response, info = fetch_url(module, url, data=json_body, headers=headers)
    response_code = str(info['status'])
    if info['status'] not in [200, 201]:
        module.fail_json(msg="Failed to connect to Itential Automation Platform. Response code is " + response_code)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    jsonResponse = json.loads(response.read().decode('utf-8'))
    module.exit_json(changed=True, msg={"workflow_name": module.params['workflow_name'], "status": "started"},
                     response=jsonResponse)


def main():
    """
    :return: response and msg
    """
    # define the available arguments/parameters that a user can pass to
    # the module
    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=dict(
            iap_port=dict(type='str', required=True),
            iap_fqdn=dict(type='str', required=True),
            token_key=dict(type='str', required=True),
            workflow_name=dict(type='str', required=True),
            description=dict(type='str', required=True),
            variables=dict(type='dict', required=False),
            https=(dict(type='bool', default=False)),
            validate_certs=dict(type='bool', default=False)
        )
    )
    start_workflow(module)


if __name__ == '__main__':
    main()
