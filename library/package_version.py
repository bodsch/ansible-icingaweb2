#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import print_function
import re

from ansible.module_utils import distro
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: package_version.py
author:
    - 'Bodo Schulz'
short_description: tries to determine the version of a package to be installed.
description: ''
"""

EXAMPLES = """
- name: get version of installed php-fpm
  package_version:
    package_name: "php-fpm"
  register: package_version
"""


class PackageVersion(object):

    def __init__(self, module):

        self.module = module

        self.package_name = module.params.get("package_name")

    def run(self):

        result = dict(
            changed=False,
            failed=True,
            msg="initial"
        )

        (distribution, version, codename) = distro.linux_distribution(full_distribution_name=False)

        self.module.log(msg="distribution       : '{0}'".format(distribution))

        if(distribution.lower() in ["centos", "oracle", "redhat", "fedora"]):
            """
              redhat based
            """
            package_mgr = self.module.get_bin_path('yum', False)

            if(not package_mgr):
                package_mgr = self.module.get_bin_path('dnf', True)

            if(not package_mgr):
                return True, "", "no valid package manager (yum or dnf) found"

            self.module.log(msg="  '{0}'".format(package_mgr))

            rc, out, err = self.module.run_command(
                [package_mgr, "list", "installed", "--cacheonly", "*{0}*".format(self.package_name)],
                check_rc=False)

            pattern = re.compile(r".*{0}.*(?P<version>[0-9]+\.[0-9]+)\..*@(?P<repo>.*)".format(self.package_name))

            version = re.search(pattern, out)

            if(version):
                version_string = version.group('version')
                version_string_compressed = version_string.replace('.', '')

                result = dict(
                    failed=False,
                    version=version_string,
                    version_compressed=version_string_compressed
                )
            else:
                result = dict(
                    failed=False,
                    msg="package {0} is not installed".format(self.package_name),
                )

        elif(distribution.lower() in ["debian", "ubuntu"]):
            """
              debain based
            """
            import apt

            cache = apt.cache.Cache()
            cache.update()
            cache.open()

            try:
                pkg = cache[self.package_name]

                # debian:10 / buster:
                #  [php-fpm=2:7.3+69]
                # ubuntu:20.04 / focal
                #  [php-fpm=2:7.4+75]
                if(pkg):
                    pkg_version = pkg.versions[0]
                    version = pkg_version.version
                    pattern = re.compile(r'^\d:(?P<version>\d.+)\+.*')
                    version = re.search(pattern, version)

                    version_string = version.group('version')
                    version_string_compressed = version_string.replace('.', '')

                result = dict(
                    failed=False,
                    version=version_string,
                    version_compressed=version_string_compressed
                )
            except KeyError as error:
                self.module.log(msg="error         : {0}".format(error))

                result = dict(
                    failed=False,
                    msg="package {0} is not installed".format(self.package_name),
                )

        else:
            """
              all others
            """
            result = dict(
                failed=False,
                msg="unknown distribution: {0}".format(distribution),
                version=""
            )

        return result


# ---------------------------------------------------------------------------------------
# Module execution.
#

def main():
    ''' ... '''
    module = AnsibleModule(
        argument_spec=dict(
            package_name=dict(required=True, type='str'),
        ),
        supports_check_mode=False,
    )

    result = PackageVersion(module).run()

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
