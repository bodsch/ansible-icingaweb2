#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils.basic import AnsibleModule


__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: icingawweb_module.py
author:
    - 'Bodo Schulz'
short_description: enable / disable icingaweb modules.
description: ''
"""

EXAMPLES = """
- name: disable modules
  become: true
  icingaweb_module:
    state: absent
    module: dark_lord
"""


class IcingaWeb2Modules(object):
    """
    Main Class to implement the Icinga2 API Client
    """
    module = None

    def __init__(self):
        """
          Initialize all needed Variables
        """
        self.state = module.params.get("state")
        self.module = module.params.get("module")
        self.module_path = module.params.get("module_path")

    def run(self):
        res = dict(
            changed=False,
            failed=False,
            ansible_module_results="none"
        )

        # module.log(msg="Module: {} - {}".format(self.module, self.state))

        if(os.path.isdir(self.module_path)):
            """

            """
            source = os.path.join(self.module_path, self.module)
            destination = os.path.join('/etc/icingaweb2/enabledModules', self.module)

            if(os.path.isdir(source)):

                module.log(msg="module {} exists".format(self.module))

                if(self.state == 'present'):
                    """
                      create link from '/usr/share/icingaweb2/modules/$MODULE' to '/etc/icingaweb2/enabledModules/$MODULE'
                    """
                    if(os.path.islink(destination) and os.readlink(destination) == source):
                        # module.log(msg="link exists and is valid")
                        pass
                    else:
                        if(not os.path.islink(destination)):
                            self.create_link(source, destination)
                        else:
                            if(os.readlink(destination) != source):
                                module.log(msg="path '{}' is a broken symlink".format(destination))
                                self.create_link(source, destination, True)
                            else:
                                self.create_link(source, destination)

                        res['changed'] = True

                else:
                    if(os.path.islink(destination)):
                        os.remove(destination)
                        res['changed'] = True
        else:
            msg = "{} is no directory".format(self.module_path)

            res['ansible_module_results'] = msg
            res['failed'] = True
            module.log(msg=msg)

        return res

    def create_link(self, source, destination, force=False):
        module.log(msg="create_link({}, {}, {})".format(source, destination, force))

        if(force):
            os.remove(destination)
            os.symlink(source, destination)
        else:
            os.symlink(source, destination)

        pass


# ===========================================
# Module execution.
#


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["absent", "present"]),
            module=dict(required=True),
            module_path=dict(required=False, default='/usr/share/icingaweb2/modules'),
        ),
        supports_check_mode=False,
    )

    icingaweb = IcingaWeb2Modules()
    result = icingaweb.run()

    module.log(msg="= result : '{}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
