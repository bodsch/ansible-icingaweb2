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
    """
    """
    def __init__(self, module):

        self.module = module

        self.state = module.params.get("state")
        self.package_name = module.params.get("package_name")

        (self.distribution, self.version, self.codename) = distro.linux_distribution(
            full_distribution_name=False
        )

    def run(self):
        """
        """
        result = dict(
            failed=False,
            msg="unknown or unsupported distribution: '{0}'.format(self.distribution)",
            version=""
        )

        if self.distribution.lower() in ["centos", "oracle", "redhat", "fedora"]:
            """
              redhat based
            """
            result = self._search_yum()

        if self.distribution.lower() in ["debian", "ubuntu"]:
            """
              debain based
            """
            result = self._search_apt()

        if self.distribution.lower() in ["arch", "artix"]:
            """
              arch based
            """
            result = self._search_pacman()

        return result

    def _search_apt(self):
        """
          support apt
        """
        import apt

        cache = apt.cache.Cache()

        # try:
        #     cache.update()
        # except SystemError as error:
        #     self.module.log(msg=f"error         : {error}")
        #     raise FetchFailedException(error)
        # if not res and raise_on_error:
        #     self.module.log(msg="FetchFailedException()")
        #     raise FetchFailedException()
        # else:
        #     cache.open()

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

        return result

    def _search_yum(self):
        """
          support yum ore dnf
        """
        package_mgr = self.module.get_bin_path('yum', False)

        if(not package_mgr):
            package_mgr = self.module.get_bin_path('dnf', True)

        if(not package_mgr):
            return True, "", "no valid package manager (yum or dnf) found"

        self.module.log(msg="  use package manager '{0}'".format(package_mgr))

        args = []
        args.append(package_mgr)
        args.append("list")
        args.append("installed")
        args.append("--cacheonly")
        args.append("*{0}*".format(self.package_name))

        rc, out, err = self.module.run_command(args, check_rc=False)

        pattern = re.compile(
            r"^{0}[0-9+].*\.x86_64.*(?P<version>[0-9]+\.[0-9]+)\..*@(?P<repo>.*)".format(self.package_name),
            re.MULTILINE
        )

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

        return result

    def _search_pacman(self):
        """
            pacman support

            pacman --noconfirm --sync --search php7 | grep -E "^(extra|world)\\/php7 (.*)\\[installed\\]" | cut -d' ' -f2
        """
        # self.module.log(msg="= _search_pacman()")

        # pattern for matching
        #  - local/php 8.0.21-1 and
        #  - local/php7 7.4.24-1
        # (?P<repository>extra|world|local)\/php[0-9\s]*(?P<version>\d\.\d).*-.*

        pattern = re.compile(
            r'^(?P<repository>extra|world|local)\/{}[0-9\s]*(?P<version>\d\.\d).*-.*'.format(self.package_name),
            re.MULTILINE
        )

        # pattern = re.compile(r'^(?P<repository>extra|world)\/{}[\w -](?P<version>\d\.\d).*-.*'.format(self.package_name), re.MULTILINE)

        pacman_bin = self.module.get_bin_path('pacman', True)

        # pacman --query --search php*

        results = []
        args = []
        args.append(pacman_bin)

        if self.state == "installed":
            """
              installed
            """
            args.append("--query")
        else:
            """
              available
            """
            args.append("--noconfirm")
            args.append("--sync")

        args.append("--search")
        args.append(self.package_name)

        rc, out, err = self._pacman(args)

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

        return result

    def _pacman(self, cmd):
        """
          support pacman
        """
        self.module.log(msg="cmd: {}".format(cmd))

        rc, out, err = self.module.run_command(cmd, check_rc=False)
        # self.module.log(msg="  rc : '{}'".format(rc))
        self.module.log(msg="  out: '{}' ({})".format(out, type(out)))
        # self.module.log(msg="  err: '{}'".format(err))
        return rc, out, err

# ---------------------------------------------------------------------------------------
# Module execution.
#


def main():
    ''' ... '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                choices=[
                    "installed",
                    "available",
                ],
                default="installed"
            ),
            package_name=dict(
                required=True,
                type='str'
            ),
        ),
        supports_check_mode=False,
    )

    result = PackageVersion(module).run()

    module.log(msg="= result : '{0}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
