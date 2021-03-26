#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os
import json
import crypt
import hashlib

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_native

try:
    import pymysql as mysql_driver
    _mysql_cursor_param = 'cursor'
except ImportError:
    try:
        import MySQLdb as mysql_driver
        import MySQLdb.cursors
        _mysql_cursor_param = 'cursorclass'
    except ImportError:
        mysql_driver = None

mysql_driver_fail_msg = 'The PyMySQL (Python 2.7 and Python 3.X) or MySQL-python (Python 2.X) module is required.'


__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}


class IcingaWeb2DatabaseUser(object):
    """
      Main Class to implement the Icinga2 API Client
    """
    module = None

    def __init__(self):
        """
          Initialize all needed Variables
        """
        self.state = module.params.get("state")
        self.username = module.params.get("username")
        self.password = module.params.get("password")
        self.preferences = module.params.get("preferences")
        self.force = module.params.get("force")

        self.db_autocommit = True
        self.db_connect_timeout = 30

    def run(self):
        res = dict(
            changed=False,
            failed=False,
            ansible_module_results="none"
        )

        module.log(msg="user: {}".format(self.username))
#        module.log(msg="      {}".format(self.preferences))
#        module.log(msg="      {}".format(str(self.preferences)))
#        module.log(msg="------------------------------")

        file_name = "/tmp/.icingaweb2_user_{}.json".format(self.username)

        password_hash = self.__password_hash(self.password)
        password_checksum = self.__checksum(self.password)
        preferences_checksum = self.__checksum(str(self.preferences))
        password_checksum_exists = ''
        preferences_checksum_exists = ''

#        module.log(msg="      {}".format(password_checksum))
#        module.log(msg="      {}".format(preferences_checksum))
#        module.log(msg="------------------------------")

        user_up2date = False
        preferences_up2date = False

        if(os.path.exists(file_name)):

            with open(file_name) as f:
                data = json.load(f)
                module.log(msg=json.dumps(data))
                password_checksum_exists = data.get(self.username).get('checksum')
                preferences_checksum_exists = data.get(self.username).get('preferences_checksum', {})

#                module.log(msg="password checksum    : {}".format(password_checksum_exists))
#                module.log(msg="preferences checksum : {}".format(preferences_checksum_exists))

        if(preferences_checksum_exists == preferences_checksum):
            preferences_up2date = True
            module.log(msg="pref data are fine")

        if(password_checksum_exists == password_checksum):
            user_up2date = True
            module.log(msg="user data are fine")

        if(preferences_up2date and user_up2date and not self.force):
            module.log(msg="no force")
            return res

        state = self.__insert_user(self.username, password_hash)
        self.__insert_preferences(self.username, self.preferences)

        data = {
            self.username: {
                "hashed": password_hash,
                "checksum": password_checksum,
                "preferences_checksum": preferences_checksum
            }
        }

        res['changed'] = state
        res['failed'] = not state

        # module.log(msg="write json")
        with open(file_name, 'w') as fp:
            json.dump(data, fp)

        return res

    # https://docs.python.org/3/library/crypt.html

    def __password_hash(sef, plaintext):
        result = crypt.crypt(plaintext, crypt.METHOD_SHA256)

        return result

    def __checksum(self, plaintext):
        password_bytes = plaintext.encode('utf-8')
        password_hash = hashlib.sha256(password_bytes)
        checksum = password_hash.hexdigest()

        return checksum

    def __insert_user(self, username, password_hash):
        """

        """
        q = "insert ignore into icingaweb_user (name, active, password_hash) VALUES ('{}', {}, '{}');".format(username, '1', password_hash)

        cursor, conn = self.__mysql_connect()

        try:
            cursor.execute(q)
        except Exception as e:
            if not self.db_autocommit:
                conn.rollback()

            cursor.close()
            module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))

        conn.close()

        return True

    def __update_user(self, username, password_hash):
        """

        """
        q = "update icingaweb_user set password_hash = '{}' where name = '{}';".format(password_hash, username)

        module.log(msg=" => {}".format(q))

        cursor, conn = self.__mysql_connect()

        try:
            cursor.execute(q)
        except Exception as e:
            if not self.db_autocommit:
                conn.rollback()

            cursor.close()
            module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))

        conn.close()

        return True

    def __int_from_bool(self, value=False):

        if value:
            return '1'
        else:
            return '0'

    def __insert_preferences(self, username, preferences):
        """


        """
        queries = []
        q = "insert ignore into icingaweb_user_preference (username, section, name, value) values ('{}', 'section', '{}', '{}')"

        if(preferences):
            #            for k in preferences.items():
            #                module.log(msg=" => {}".format(k))

            _auto_refresh = self.__int_from_bool(preferences.get('auto_refresh', False))
            _show_application_msg = self.__int_from_bool(preferences.get('show_application_state_messages', False))
            _show_benchmark = self.__int_from_bool(preferences.get('show_benchmark', False))
            _show_stacktraces = self.__int_from_bool(preferences.get('show_stacktraces', False))

            queries.append(q.format(username, 'auto_refresh', _auto_refresh))
            queries.append(q.format(username, 'show_application_state_messages', _show_application_msg))
            queries.append(q.format(username, 'show_benchmark', _show_benchmark))
            queries.append(q.format(username, 'show_stacktraces', _show_stacktraces))
            if(preferences.get('language')):
                queries.append(q.format(username, 'language', preferences.get('language')))
            if(preferences.get('timezone')):
                queries.append(q.format(username, 'timezone', preferences.get('timezone')))
            if(preferences.get('default_page_size')):
                queries.append(q.format(username, 'default_page_size', preferences.get('default_page_size')))

            cursor, conn = self.__mysql_connect()

            for q in queries:
                #                module.log(msg=" => {}".format(q))
                try:
                    cursor.execute(q)
                except Exception as e:
                    if not self.db_autocommit:
                        conn.rollback()

                    cursor.close()
                    module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))

            conn.close()

        return True

    def __mysql_connect(self):
        """

        """
        config = {}

        config_file = module.params.get("database_config_file")

        if config_file and os.path.exists(config_file):
            config['read_default_file'] = config_file
# TODO
#            cp = self.__parse_from_mysql_config_file(config_file)

        if module.params.get("database_login_unix_socket"):
            config['unix_socket'] = module.params.get("database_login_unix_socket")
        else:
            config['host'] = module.params.get("database_login_host")
            config['port'] = module.params.get("database_login_port")

        # If login_user or login_password are given, they should override the
        # config file
        if module.params.get("database_login_user") is not None:
            config['user'] = module.params.get("database_login_user")
        if module.params.get("database_login_password") is not None:
            config['passwd'] = module.params.get("database_login_password")

        config['db'] = module.params.get("database_name")

        module.log(msg="config : {}".format(config))

        try:
            db_connection = mysql_driver.connect(**config)

        except Exception as e:

            module.log(msg="unable to connect to database, check login_user and "
                           "login_password are correct or %s has the credentials. "
                           "Exception message: %s" % (config_file, to_native(e)))

        if self.db_autocommit:
            db_connection.autocommit(True)

        return db_connection.cursor(), db_connection

    def __parse_from_mysql_config_file(self, cnf):
        cp = configparser.ConfigParser()
        cp.read(cnf)
        return cp


# ===========================================
# Module execution.
#


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["absent", "present"]),
            username=dict(required=True, no_log=False),
            password=dict(required=True, no_log=True),
            preferences=dict(required=False, type="dict"),
            force=dict(required=False, default=False, type="bool"),
            database_login_user=dict(type='str'),
            database_login_password=dict(type='str', no_log=True),
            database_login_host=dict(type='str', default='localhost'),
            database_login_port=dict(type='int', default=3306),
            database_login_unix_socket=dict(type='str'),
            database_config_file=dict(type='path'),
            database_name=dict(required=True, type='str'),
        ),
        supports_check_mode=False,
    )

    icingaweb = IcingaWeb2DatabaseUser()
    result = icingaweb.run()

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
