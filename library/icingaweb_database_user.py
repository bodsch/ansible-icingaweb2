#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, print_function
import os
# import errno
import json
import crypt
import hashlib

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_native

try:
    import pymysql as mysql_driver
except ImportError:
    try:
        import MySQLdb as mysql_driver
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

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.state = module.params.get("state")
        self.username = module.params.get("username")
        self.password = module.params.get("password")
        self.preferences = module.params.get("preferences")
        self.force = module.params.get("force")

        self.database_name = module.params.get("database_name")
        self.database_config_file = module.params.get("database_config_file")
        self.database_login_host = module.params.get("database_login_host")
        self.database_login_port = module.params.get("database_login_port")
        self.database_login_socket = module.params.get("database_login_unix_socket")
        self.database_login_user = module.params.get("database_login_user")
        self.database_login_password = module.params.get("database_login_password")

        self.db_autocommit = True
        self.db_connect_timeout = 30

        self.state_directory = "/etc/icingaweb2/.ansible"

        try:
            # Create target Directory
            os.mkdir(self.state_directory)
        except OSError as e:
            pass

    def run(self):
        """
        """
        res = dict(
            changed=False,
            failed=False
        )

        if not mysql_driver:
            return dict(
                failed=True,
                error=mysql_driver_fail_msg
            )

        # self.module.log(msg="------------------------------")
        # self.module.log(msg="user: {}".format(self.username))
        # self.module.log(msg="------------------------------")

        file_name = "{}/user_{}.json".format(self.state_directory, self.username)

        password_hash = self.__password_hash(self.password)
        password_checksum = self.__checksum(self.password)
        preferences_checksum = self.__checksum(str(self.preferences))
        password_checksum_exists = ''
        preferences_checksum_exists = ''

        user_up2date = False
        preferences_up2date = False

        if(os.path.exists(file_name)):
            """
            """
            with open(file_name) as f:
                data = json.load(f)
                password_checksum_exists = data.get(self.username).get('checksum')
                preferences_checksum_exists = data.get(self.username).get('preferences_checksum', {})

        preferences_up2date = (preferences_checksum_exists == preferences_checksum)
        user_up2date = (password_checksum_exists == password_checksum)

        # self.module.log(msg="user_up2date       : {}".format(user_up2date))
        # self.module.log(msg="preferences_up2date: {}".format(preferences_up2date))
        # self.module.log(msg="force              : {}".format(self.force))

        if preferences_up2date and user_up2date and not self.force:
            msg = []
            if user_up2date:
                msg.append("user or password have not been changed")
            if preferences_up2date:
                msg.append("preference have not been changed")

            message = " / ".join(msg)

            # message="user or password and/or preference are not changed"
            self.module.log(msg=message)
            return dict(
                changed=False,
                failed=False,
                msg=message
            )

        state, error, error_message = self.__list_user(self.username)

        if error:
            return dict(
                failed=True,
                msg=error_message
            )

        if state:
            state, error, error_message = self.__update_user(self.username, password_hash)
        else:
            state, error, error_message = self.__insert_user(self.username, password_hash)

        if error:
            return dict(
                failed=True,
                msg=error_message
            )

        if self.preferences:
            state, error, error_message = self.__insert_preferences(self.username, self.preferences)
            if error:
                return dict(
                    failed=True,
                    msg=error_message
                )

        data = {
            self.username: {
                "hashed": password_hash,
                "checksum": password_checksum,
                "preferences_checksum": preferences_checksum
            }
        }

        if self.force:
            message = "user {} forced inserted".format(self.username)
        else:
            message = "user {} successful inserted".format(self.username)

        with open(file_name, 'w') as fp:
            json.dump(data, fp)

        return dict(
            changed=True,
            msg=message
        )

    # https://docs.python.org/3/library/crypt.html

    def __password_hash(sef, plaintext):
        """
        """
        return crypt.crypt(plaintext, crypt.METHOD_SHA256)

    def __checksum(self, plaintext):
        """
        """
        password_bytes = plaintext.encode('utf-8')
        password_hash = hashlib.sha256(password_bytes)
        return password_hash.hexdigest()

    def __list_user(self, user):
        """
        """
        number_of_rows = 0

        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return False, error, message

        q = "select name from icingaweb_user where name = '{}'"
        q = q.format(user)

        try:
            number_of_rows = cursor.execute(q)
            cursor.fetchone()
            cursor.close()

        except Exception as e:
            self.module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))

        if number_of_rows == 1:
            return True, False, ""
        else:
            return False, False, ""

    def __insert_user(self, username, password_hash):
        """

        """
        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return False, error, message

        q = "insert ignore into icingaweb_user (name, active, password_hash) VALUES ('{}', {}, '{}');"
        q = q.format(username, '1', password_hash)

        try:
            cursor.execute(q)
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))
        finally:
            cursor.close()

        return True, False, None

    def __update_user(self, username, password_hash):
        """

        """
        q = "update icingaweb_user set active = {}, password_hash = '{}' where name = '{}';"
        q = q.format(1, password_hash, username)

        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return None, error, message

        try:
            cursor.execute(q)
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))
        finally:
            cursor.close()

        conn.close()

        return True, False, None

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
            # for k in preferences.items():
            #     self.module.log(msg=" => {}".format(k))

            _auto_refresh = self.__int_from_bool(preferences.get('auto_refresh', False))
            _show_application_msg = self.__int_from_bool(preferences.get('show_application_state_messages', False))
            _show_benchmark = self.__int_from_bool(preferences.get('show_benchmark', False))
            _show_stacktraces = self.__int_from_bool(preferences.get('show_stacktraces', False))

            queries.append("delete from icingaweb_user_preference where username = {}".format(username))
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

            cursor, conn, error, message = self.__mysql_connect()

            self.module.log(msg="  - error: {0} | msg: {1}".format(error, message))

            if error:
                return False, error, message

            for q in queries:
                self.module.log(msg=" => {}".format(q))
                try:
                    cursor.execute(q)

                    if not self.db_autocommit:
                        conn.commit()

                except Exception as e:
                    if not self.db_autocommit:
                        conn.rollback()

                    cursor.close()
                    self.module.fail_json(msg="Cannot execute SQL '%s' : %s" % (q, to_native(e)))

            conn.close()

        return True, False, None

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

        self.module.log(msg="config : {}".format(config))

        try:
            db_connection = mysql_driver.connect(**config)

        except Exception as e:
            message = "unable to connect to database. "
            message += "check login_host, login_user and login_password are correct "
            message += "or {0} has the credentials. "
            message += "Exception message: {1}"
            message = message.format(config_file, to_native(e))

            self.module.log(msg=message)

            return None, None, True, message

        return db_connection.cursor(), db_connection, False, "successful connected"

    def __parse_from_mysql_config_file(self, cnf):
        cp = configparser.ConfigParser()
        cp.read(cnf)
        return cp


# ===========================================
# Module execution.
#


def main():
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

    icingaweb = IcingaWeb2DatabaseUser(module)
    result = icingaweb.run()

    module.log(msg="= result : '{}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
