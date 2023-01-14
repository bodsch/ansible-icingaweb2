#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, print_function
# import os
import re

from ansible.module_utils.basic import AnsibleModule


__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}


class IcingaCLI(object):
    """
    Main Class to implement the Icinga2 API Client
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self._icingacli = module.get_bin_path('icingacli', True)

        self.state = module.params.get("state")
        self.command = module.params.get("command")
        self.module_name = module.params.get("module_name")

    def run(self):
        """
        """
        result = dict(
            failed=False,
            changed=False,
            msg="none"
        )

        state = self._list_modules(self.module_name)

        # self.module.log(msg="  - '{}' {}'".format(self.module_name, state))

        if self.state == "enable" and state:
            return dict(
                changed=False,
                msg=f"module {self.module_name} is already enabled"
            )

        if self.state == "disable" and not state:
            return dict(
                changed=False,
                msg=f"module {self.module_name} is already disabled"
            )

        if self.state == "enable" or self.state == "disable":

            args_list = [
                self.command,
                self.state,
                self.module_name
            ]

            rc, out, err = self._exec(args_list)

            if rc == 0:
                result = dict(
                    failed=False,
                    changed=True,
                    msg=f"module {self.module_name} is successful {self.state}d"
                )
            else:
                result = dict(
                    failed=True,
                    changed=False,
                    msg=f"module {self.module_name} is not successful {self.state}d"
                )
        else:
            result = dict(
                changed=False,
                failed=True,
                msg=f"unsupported state: '{self.state}'"
            )

        return result

    def _list_modules(self, module):
        """
          returns True if the module listed
          otherwise returns False
        """
        args_list = [
            self.command,
            "list"
        ]

        rc, out, err = self._exec(args_list)

        found = False
        for line in out.splitlines():
            if line.startswith(module):
                line = re.sub(r"\s+", "|", line)
                module_name = line.split("|")[0]
                state = line.split("|")[2]

                self.module.log(msg=f" - {module_name} in state {state}")
                found = True
                break

        return found

    def _exec(self, args):
        """
        """
        cmd = [self._icingacli] + args

        rc, out, err = self.module.run_command(cmd, check_rc=True)

        # self.module.log(msg="  rc : '{}'".format(rc))
        # self.module.log(msg="  out: '{}'".format(out))
        # self.module.log(msg="  err: '{}'".format(err))

        return rc, out, err


# ===========================================
# Module execution.
#


def main():
    """

    """
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(default="module", choices=["module", "version", "web"]),
            state=dict(default="enable", choices=[
                "enable", "disable", "install", "list", "permissions",
                "purge", "remove", "restrictions", "search"]),
            module_name=dict(required=True),
        ),
        supports_check_mode=False,
    )

    icingacli = IcingaCLI(module)
    result = icingacli.run()

    module.log(msg=f"= result : '{result}'")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
