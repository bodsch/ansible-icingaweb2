#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser

try:
    import pymysql as mysql_driver
#     _mysql_cursor_param = 'cursor'
except ImportError:
    try:
        import MySQLdb as mysql_driver
#         import MySQLdb.cursors
#         _mysql_cursor_param = 'cursorclass'
    except ImportError:
        mysql_driver = None

mysql_driver_fail_msg = 'The PyMySQL (Python 2.7 and Python 3.X) or MySQL-python (Python 2.X) module is required.'


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

        self.db_connect_timeout = 30

    def run(self):
        '''  ...  '''
        self.module.log(msg="-------------------------------------------------------------")
        self.module.log(msg="user         : {}".format(self.login_user))
        self.module.log(msg="password     : {}".format(self.login_password))
        self.module.log(msg="table_schema : {}".format(self.table_schema))
        self.module.log(msg="------------------------------")

        state, count = self._information_schema()

        res = dict(
            failed=False,
            changed=False,
            exists=state,
            count=count)

        self.module.log(msg="result: {}".format(res))
        self.module.log(msg="-------------------------------------------------------------")

        return res

    def _information_schema(self):
        ''' ... '''
        cursor, conn = self.__mysql_connect()

        query = "SELECT count(TABLE_NAME) FROM information_schema.tables where TABLE_SCHEMA = '{schema}'"
        query = query.format(schema=self.table_schema)

        self.module.log(msg="query : {}".format(query))

        try:
            cursor.execute(query)
        except mysql_driver.ProgrammingError as e:
            (errcode, message) = e.args

            self.module.fail_json(msg="Cannot execute SQL '%s' : %s" % (query, to_native(e)))

        exists, = cursor.fetchone()
        cursor.close()
        conn.close()

        if(int(exists) >= 4):
            return True, exists

        return False, 0

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

        self.module.log(msg="config : {}".format(config))

        try:
            db_connection = mysql_driver.connect(**config)

        except Exception as e:
            self.module.log(
                msg="unable to connect to database, check login_user and "
                "login_password are correct or %s has the credentials. "
                "Exception message: %s" % (config_file, to_native(e)))

        return db_connection.cursor(), db_connection

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
        ),
        supports_check_mode=False,
    )

    icingaweb = MysqlSchema(module)
    result = icingaweb.run()

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
