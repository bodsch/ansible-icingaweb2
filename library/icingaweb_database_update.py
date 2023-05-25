#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, print_function
import os
import warnings
import re

from packaging.version import Version, parse as parseVersion
from packaging.version import InvalidVersion

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_native
from ansible.module_utils.mysql import (
    mysql_driver, mysql_driver_fail_msg
)

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: icingaweb_database_update.py
author:
    - 'Bodo Schulz'
short_description: handle user and they preferences in a mysql.
description: ''
"""

EXAMPLES = """
- name: import icingaweb users into database
  become: true
  icingaweb_database_update:
    database_login_host: database
    database_name: icingaweb_config
    database_config_file: /etc/icingaweb2/.my.cnf
    icingaweb_version: "2.11.3"
"""


class IcingaWeb2DatabaseUpdate(object):
    """
      Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.database_name = module.params.get("database_name")
        self.database_config_file = module.params.get("database_config_file")
        self.database_login_host = module.params.get("database_login_host")
        self.database_login_port = module.params.get("database_login_port")
        self.database_login_socket = module.params.get("database_login_unix_socket")
        self.database_login_user = module.params.get("database_login_user")
        self.database_login_password = module.params.get("database_login_password")
        self.icingaweb_version = module.params.get("icingaweb_version")
        self.icingaweb_upgrade_directory = module.params.get("icingaweb_upgrade_directory")

        self.database_table_name = "icingaweb_dbversion"
        self.db_autocommit = True
        self.db_connect_timeout = 30

        self.state_directory = "/etc/icingaweb2/.ansible"

        try:
            # Create target Directory
            os.mkdir(self.state_directory)
        except OSError:
            pass

    def run(self):
        """
        """
        _changed = False
        _failed = False
        _msg = "module init."

        if mysql_driver is None:
            self.module.fail_json(msg=mysql_driver_fail_msg)
        else:
            warnings.filterwarnings('error', category=mysql_driver.Warning)

        # first step:
        # create table (if needed)
        (state, db_error, message) = self.__create_table_schema()

        if db_error:
            return dict(
                failed=True,
                msg=message
            )

        # step two:
        # check current version
        (current_version, db_error, message) = self.__current_version()

        if db_error:
            return dict(
                failed=True,
                msg=message
            )

        _msg = f"  versions: {current_version} vs. {self.icingaweb_version}"
        self.module.log(_msg)

        if not current_version:
            (state, db_error, message) = self.__update_version(version=self.icingaweb_version)

            if db_error:
                _failed = True
                _msg = message

            if state:
                _changed = True
                _msg = "version successful updated."
        else:
            # version compare
            if Version(current_version) == Version(self.icingaweb_version):
                # self.module.log("versions equal.")
                return dict(
                    changed = False,
                    failed = False,
                    msg = "icingaweb database is up to date."
                )

            elif Version(current_version) < Version(self.icingaweb_version):
                self.module.log(f"upgrade to version {self.icingaweb_version} needed.")
                (state, db_error, message) = self.upgrade_database(from_version=current_version)

                # self.module.log(msg=f" - upgrade_database  : {state}, {db_error}, {message}")

                if db_error:
                    _failed = True

                if state:
                    _changed = True

                _msg = message

            else:
                return dict(
                    changed = False,
                    failed = False,
                    msg = f"icingaweb database downgrade are not supported. (current version are {current_version})"
                )

        return dict(
            changed = _changed,
            failed = _failed,
            msg = _msg
        )

    def __hash(self, plaintext):
        """
          https://docs.python.org/3/library/crypt.html
        """
        import crypt
        salt = ""
        try:
            salt = crypt.mksalt(crypt.METHOD_SHA512)
        except Exception:
            import random
            CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            salt = ''.join(random.choice(CHARACTERS) for i in range(16))
            # Use SHA512
            # return '$6$' + salt

        return crypt.crypt(
            plaintext,
            salt
        )

    def __checksum(self, plaintext):
        """
        """
        import hashlib
        _bytes = plaintext.encode('utf-8')
        _hash = hashlib.sha256(_bytes)
        return _hash.hexdigest()

    def __check_table_schema(self):
        """
            :return:
                - state (bool)
                - db_error(bool)
                - db_error_message = (str|none)
        """
        q = f"SELECT * FROM information_schema.tables WHERE table_name = '{self.database_table_name}'"

        number_of_rows = 0

        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return (False, error, message)

        try:
            number_of_rows = cursor.execute(q)
            cursor.fetchone()

        except Exception as e:
            self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")
            pass

        finally:
            cursor.close()

        if number_of_rows == 1:
            return (True, False, "")

        return (False, False, "")

    def __create_table_schema(self):
        """
            :return:
                - state (bool)
                - db_error(bool)
                - db_error_message = (str|none)
        """
        (table_state, db_state, db_msg) = self.__check_table_schema()

        _msg = None

        if not table_state:
            q = f"""CREATE TABLE `{self.database_table_name}` (
              `dbversion_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
              `name` varchar(10) CHARACTER SET latin1 DEFAULT '',
              `version` varchar(10) CHARACTER SET latin1 DEFAULT '',
              `create_time` timestamp DEFAULT CURRENT_TIMESTAMP,
              `modify_time` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`dbversion_id`),
              UNIQUE KEY `dbversion` (`name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

            cursor, conn, error, message = self.__mysql_connect()

            if error:
                return (False, error, message)

            try:
                cursor.execute(q)
                conn.commit()
                _msg = f"table {self.database_table_name} successful created."

            except Exception as e:
                conn.rollback()
                self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")

            finally:
                cursor.close()

        return (True, False, _msg)

    def __current_version(self):
        """
        """
        _version = None
        _msg = None

        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return (False, error, message)

        q = f"select version from {self.database_table_name}"

        try:
            cursor.execute(q)
            _version = cursor.fetchone()[0]

        except Exception as e:
            _msg = f"Cannot execute SQL '{q}' : {to_native(e)}"
            pass

        finally:
            cursor.close()

        if _version:
            _msg = f"found version: {_version}"
            self.module.log(_msg)

        return (_version, False, _msg)

    def __update_version(self, version):
        """
        """
        cursor, conn, db_error, db_message = self.__mysql_connect()

        if db_error:
            return False, db_error, db_message

        q = f"""replace INTO {self.database_table_name} (name, version, modify_time)
            VALUES ('icingaweb', '{version}', now())"""

        state = False
        db_error = False
        db_message = None

        try:
            cursor.execute(q)
            conn.commit()
            state = True
        except Exception as e:
            conn.rollback()
            state = False
            db_error = True
            db_message = f"Cannot execute SQL '{q}' : {to_native(e)}"

            self.module.log(msg=db_message)
        finally:
            cursor.close()

        return (state, db_error, db_message)

    def upgrade_database(self, from_version="2.0.0"):
        """
        """
        state = False
        db_error = False
        db_message = None

        result_state = {}

        upgrade_files = self.__read_database_upgrades(from_version=from_version)

        cursor, conn, db_error, db_message = self.__mysql_connect()

        if db_error:
            return False, db_error, db_message

        for upgrade in upgrade_files:
            """
            """
            file_name = os.path.basename(upgrade)
            file_version = file_name.replace(".sql", "")

            result_state[str(file_version)] = {}

            self.module.log(msg=f"upgrade database to version: {file_version}")

            sql_commands = []

            state = False
            db_error = False
            db_message = None
            _msg = None # f"file '{upgrade}' successful imported."

            with open(upgrade, encoding='utf8') as f:
                sql_commands = f.read().split(';\n')

                for command in sql_commands:
                    state = False
                    db_error = False
                    db_message = None

                    if command:
                        # self.module.log(msg=command.strip())
                        (state, db_error, db_message) = self.__db_execute(command.strip())
                        if db_error:
                            break

            if db_error:
                state = True
                _msg = f"Cannot import file '{upgrade}' : {to_native(db_message)}"
            else:
                _msg = f"file '{upgrade}' successful imported."

            result_state[file_version].update({
                "failed": state,
                "msg": _msg
            })

            if not db_error:
                self.__update_version(file_version)
            else:
                break

        failed = (len({k: v for k, v in result_state.items() if v.get('failed', False)}) > 0)

        if failed:
            state = False

        return (state, db_error, result_state)

    def __read_database_upgrades(self, from_version="2.0.0"):
        """
        """
        _versions = []
        upgrade_files = []
        upgrade_versions = []

        self.module.log(msg=f"search versions between {from_version} and {self.icingaweb_version}")

        for root, dirs, files in os.walk(self.icingaweb_upgrade_directory, topdown=False):
            # self.module.log(msg=f"  - root : {root}")
            # self.module.log(msg=f"  - dirs : {dirs}")
            # self.module.log(msg=f"  - files: {files}")
            if files:
                _versions = files

        for v in _versions:
            """
            """
            version_string = v.replace(".sql", "")

            if version_string.startswith("2.0.0") or Version(version_string) <= Version(from_version):
                continue
            if Version(version_string) > Version(from_version) or Version(version_string) <= Version(self.icingaweb_version):
                upgrade_versions.append(version_string)

        # version sort
        upgrade_versions.sort(key = parseVersion)

        for v in upgrade_versions:
            self.module.log(msg=f"  - {v}")
            upgrade_files.append(os.path.join(root, f"{v}.sql"))

        return upgrade_files

    def __mysql_connect(self):
        """

        """
        config = {}

        config_file = self.database_config_file

        if config_file and os.path.exists(config_file):
            config['read_default_file'] = config_file

        if self.database_login_socket:
            config['unix_socket'] = self.database_login_socket
        else:
            config['host'] = self.database_login_host
            config['port'] = self.database_login_port

        # If login_user or login_password are given, they should override the
        # config file
        if self.database_login_user is not None:
            config['user'] = self.database_login_user
        if self.database_login_password is not None:
            config['passwd'] = self.database_login_password

        config['db'] = self.database_name

        try:
            db_connection = mysql_driver.connect(**config)

        except Exception as e:
            message = "unable to connect to database. "
            message += "check login_host, login_user and login_password are correct "
            message += f"or {config_file} has the credentials. "
            message += f"Exception message: {to_native(e)}"

            self.module.log(msg=message)

            return (None, None, True, message)

        return (db_connection.cursor(), db_connection, False, "successful connected")

    def __parse_from_mysql_config_file(self, cnf):
        cp = configparser.ConfigParser()
        cp.read(cnf)
        return cp

    def __db_execute(self, query, rollback=True):
        """
        """
        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return (False, error, message)

        state = False
        db_error = False
        db_message = None

        try:
            # pass
            cursor.execute(query)
            conn.commit()
            state = True
            # state = False
            # db_error = True
            # db_message = "test fehler"

        except mysql_driver.Warning as e:
            error_id = e.args[0]
            error_msg = e.args[1]
            self.module.log(msg=f"WARNING: {error_id} - {error_msg}")

        except (mysql_driver.Error) as e:
            error_id = e.args[0]
            error_msg = e.args[1]

            if error_id == 1050:  # Table '...' already exists
                self.module.log(msg=f"WARNING: {error_msg}")

        except Exception as e:
            db_error = True
            db_message = f"Cannot execute SQL '{query}' : {to_native(e)}"

            if rollback:
                conn.rollback()

            pass

        finally:
            cursor.close()

        return (state, db_error, db_message)


# ===========================================
# Module execution.
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            database_login_user=dict(type='str'),
            database_login_password=dict(type='str', no_log=True),
            database_login_host=dict(type='str', default='localhost'),
            database_login_port=dict(type='int', default=3306),
            database_login_unix_socket=dict(type='str'),
            database_config_file=dict(type='path'),
            database_name=dict(required=True, type='str'),
            icingaweb_version=dict(required=True, type='str'),
            icingaweb_upgrade_directory=dict(required=True, type='str'),



        ),
        supports_check_mode=False,
    )

    icingaweb = IcingaWeb2DatabaseUpdate(module)
    result = icingaweb.run()

    module.log(msg="= result : '{}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
