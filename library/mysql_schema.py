#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os
import warnings

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser
from ansible.module_utils.mysql import (
    mysql_driver, mysql_driver_fail_msg
)


DOCUMENTATION = """
---
module: mysql_schema.py
author:
    - 'Bodo Schulz'
short_description: check it the named schema exists in a mysql.
description: ''
"""

EXAMPLES = """
- name: ensure, table_schema is present
  mysql_schema:
    login_host: ::1
    login_user: root
    login_password: password
    table_schema: icingaweb2
"""

# ---------------------------------------------------------------------------------------


class MysqlSchema(object):
    """
      Main Class to implement the Icinga2 API Client
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.login_user = module.params.get("login_user")
        self.login_password = module.params.get("login_password")
        self.login_host = module.params.get("login_host")
        self.login_port = module.params.get("login_port")
        self.login_unix_socket = module.params.get("login_unix_socket")
        self.database_config_file = module.params.get("database_config_file")
        self.table_schema = module.params.get("table_schema")
        self.table_name = module.params.get("table_name")

        self.db_connect_timeout = 30

        self.module.log(msg="-------------------------------------------------------------")
        self.module.log(msg="user         : {}".format(self.login_user))
        self.module.log(msg="password     : {}".format(self.login_password))
        self.module.log(msg="table_schema : {}".format(self.table_schema))
        self.module.log(msg="table_name   : {}".format(self.table_name))
        self.module.log(msg="-------------------------------------------------------------")

    def run(self):
        """
        """

        if mysql_driver is None:
            self.module.fail_json(msg=mysql_driver_fail_msg)
        else:
            warnings.filterwarnings('error', category=mysql_driver.Warning)

        if not mysql_driver:
            return dict(
                failed=True,
                error=mysql_driver_fail_msg
            )

        state, error, error_message = self._information_schema()

        if error:
            res = dict(
                failed=True,
                changed=False,
                msg=error_message
            )
        else:
            res = dict(
                failed=False,
                changed=False,
                exists=state
            )

        self.module.log(msg="result: {}".format(res))
        self.module.log(msg="-------------------------------------------------------------")

        return res

    def _information_schema(self):
        """
          get informations about schema

          return:
            state: bool (exists or not)
            count: int
            error: boot (error or not)
            error_message string  error message
        """
        cursor, conn, error, message = self.__mysql_connect()

        # self.module.log(msg="  - error: {0} | msg: {1}".format(error, message))

        if error:
            return None, error, message

        query = "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables where TABLE_SCHEMA = '{0}'"
        query = query.format(self.table_schema)

        # self.module.log(msg="query : {}".format(query))

        try:
            cursor.execute(query)

        except mysql_driver.ProgrammingError as e:
            (errcode, message) = e.args

            message = "Cannot execute SQL '{0}' : {1}".format(query, to_native(e))
            self.module.log(msg="ERROR: {}".format(message))

            return False, True, message

        records = cursor.fetchall()
        cursor.close()
        conn.close()
        exists = len(records)

        # self.module.log(msg="{0} {type(0)} {1}".format(records, exists))

        if self.table_name is not None:
            table_names = []
            for e in records:
                table_names.append(e[1])

            if self.table_name in table_names:
                self.module.log(msg="  - table name {0} exists in table schema".format(self.table_name))

                return True, False, None

        else:
            self.module.log(msg="  - table schema exists")

            if (int(exists) >= 4):
                return True, False, None

        return False, False, None

    def __mysql_connect(self):
        """

        """
        config = {}

        config_file = self.database_config_file

        if config_file and os.path.exists(config_file):
            config['read_default_file'] = config_file

        # TODO
        # cp = self.__parse_from_mysql_config_file(config_file)

        if self.login_unix_socket:
            config['unix_socket'] = self.login_unix_socket
        else:
            config['host'] = self.login_host
            config['port'] = self.login_port

        # If login_user or login_password are given, they should override the
        # config file
        if self.login_user is not None:
            config['user'] = self.login_user
        if self.login_password is not None:
            config['passwd'] = self.login_password

        # self.module.log(msg="config : {}".format(config))

        if mysql_driver is None:
            self.module.fail_json(msg=mysql_driver_fail_msg)

        try:
            db_connection = mysql_driver.connect(**config)

        except Exception as e:
            message = "unable to connect to database. "
            message += "check login_host, login_user and login_password are correct "
            message += "or {0} has the credentials. "
            message += "Exception message: {1}"
            message = message.format(config_file, to_native(e))

            self.module.log(msg=message)

            return (None, None, True, message)

        # return (db_connection.cursor(**{_mysql_cursor_param: mysql_driver.cursors.DictCursor}), db_connection, False, "successful connected")

        return db_connection.cursor(), db_connection, False, "successful connected"

    def __parse_from_mysql_config_file(self, cnf):
        cp = configparser.ConfigParser()
        cp.read(cnf)
        return cp


# ---------------------------------------------------------------------------------------
# Module execution.
#

def main():
    ''' ... '''
    module = AnsibleModule(
        argument_spec=dict(
            login_user=dict(type='str'),
            login_password=dict(type='str', no_log=True),
            login_host=dict(type='str', default='127.0.0.1'),
            login_port=dict(type='int', default=3306),
            login_unix_socket=dict(type='str'),
            database_config_file=dict(required=False, type='path'),
            table_schema=dict(required=True, type='str'),
            table_name=dict(required=False, type='str'),
        ),
        supports_check_mode=False,
    )

    icingaweb = MysqlSchema(module)
    result = icingaweb.run()

    module.log(msg="= result : '{0}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
