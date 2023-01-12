#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, print_function
import os
import warnings
import json

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
module: icingawweb_database_groups.py
author:
    - 'Bodo Schulz'
short_description: handle groups in mysql.
description: ''
"""

EXAMPLES = """
- name: import icingaweb database groups
  become: true
  icingaweb_database_group:
    state: present
    groupname: admins
    parent: ""
    members:
      - webadmin
    force: false
    database_login_host: database
    database_name: icingaweb_config
    database_config_file: /etc/icingaweb2/.my.cnf
"""


class IcingaWeb2DatabaseGroup(object):
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
        self.groupname = module.params.get("groupname")
        self.parent = module.params.get("parent", None)
        self.members = module.params.get("members")
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
        except OSError:
            pass

    def run(self):
        """
        """
        if mysql_driver is None:
            self.module.fail_json(msg=mysql_driver_fail_msg)
        else:
            warnings.filterwarnings('error', category=mysql_driver.Warning)

        if self.state == "absent":
            return self._delete_group()
        else:
            return self._create_group()

    def _delete_group(self):
        """
        """
        changed = False
        file_name = f"{self.state_directory}/group_{self.groupname}.json"

        group_id = self.__delete_all_members(self.groupname)

        if group_id:
            changed = True
            _ = self.__delete_group(self.groupname)

        if os.path.isfile(file_name):
            changed = True
            os.remove(file_name)

        if changed:
            message = "group and his members are successful removed"
        else:
            message = "nothing to do. have a nice day"

        return dict(
            changed=changed,
            failed=False,
            msg=message
        )

    def _create_group(self):
        """
        """
        file_name = f"{self.state_directory}/group_{self.groupname}.json"

        members_checksum = self.__checksum(str(self.members))

        members_checksum_exists = ''
        # group_up2date = False
        members_up2date = False

        # first step:
        # take a lock into the database
        group_exists, error, error_message = self.__list_group(self.groupname)

        if error:
            return dict(
                failed=True,
                msg=error_message
            )
        # second step:
        # check checksum file
        local_checksum_file = os.path.exists(file_name)

        if not group_exists and local_checksum_file:
            """
              hupps!?
            """
            self.module.log(msg=f" WARNING group '{self.groupname}' exists not in database but has a local checksum file")
            os.remove(file_name)
            local_checksum_file = False

        # ------------------------------------------------------------

        if local_checksum_file:
            """
            """
            with open(file_name) as f:
                data = json.load(f)
                # group_checksum_exists = data.get(self.groupname).get('checksum')
                members_checksum_exists = data.get(self.groupname).get('members_checksum', {})

        members_up2date = (members_checksum_exists == members_checksum)

        if members_up2date and not self.force:
            msg = []
            if members_up2date:
                msg.append("group and group members have not been changed")

            message = "".join(msg)

            # message="user or password and/or preference are not changed"
            self.module.log(msg=message)
            return dict(
                changed=False,
                failed=False,
                msg=message
            )

        if group_exists:
            state, error, error_message = self.__update_group(self.groupname)
        else:
            state, error, error_message = self.__insert_group(self.groupname)

        if error:
            return dict(
                failed=True,
                msg=error_message
            )

        if self.members:
            state, error, error_message = self.__insert_members(self.groupname, self.members)
            if error:
                return dict(
                    failed=True,
                    msg=error_message
                )

        data = {
            self.groupname: {
                # "checksum": password_checksum,
                "parent": self.parent,
                "members": self.members,
                "members_checksum": members_checksum
            }
        }

        if self.force:
            message = f"group {self.groupname} forced inserted"
        else:
            state_msg = "inserted"

            if group_exists:
                state_msg = "updated"

            message = f"group {self.groupname} successful {state_msg}"

        data_file = open(file_name, 'w')
        data_file.write(json.dumps(data, indent=2))
        data_file.close()

        return dict(
            changed=True,
            msg=message
        )

    def __checksum(self, plaintext):
        """
        """
        # self.module.log(msg="- __checksum({})".format(plaintext))

        import hashlib
        _bytes = plaintext.encode('utf-8')
        _hash = hashlib.sha256(_bytes)
        return _hash.hexdigest()

    def __list_group(self, group):
        """
        """
        number_of_rows = 0

        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return False, error, message

        # q = "select name from icingaweb_group where name = '{}'"

        q = "select g.id, g.name, m.group_id from icingaweb_group as g \
            left  JOIN icingaweb_group_membership as m \
            on m.group_id = g.id where g.name = '{}'"

        q = q.format(group)

        try:
            number_of_rows = cursor.execute(q)
            cursor.fetchone()
            cursor.close()

        except Exception as e:
            self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")

        if number_of_rows == 1:
            return True, False, ""
        else:
            return False, False, ""

    def __insert_group(self, groupname):
        """
        """
        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return False, error, message

        if not self.parent:
            q = f"insert ignore into icingaweb_group (name, parent, ctime, mtime) values ('{groupname}', NULL, now(), now());"
        else:
            q = f"insert ignore into icingaweb_group (name, parent, ctime, mtime) values ('{groupname}', '{self.parent}', now(), now());"

        try:
            warnings.filterwarnings('ignore', category=mysql_driver.Warning)
            cursor.execute(q)
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")
        finally:
            cursor.close()

        return True, False, None

    def __update_group(self, groupname):
        """
        """
        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return None, error, message

        if not self.parent:
            q = f"update icingaweb_group set parent = NULL, mtime = now() where name = '{groupname}';"
        else:
            q = f"update icingaweb_group set parent = '{self.parent}', mtime = now() where name = '{groupname}';"

        try:
            cursor.execute(q)
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")
        finally:
            cursor.close()

        conn.close()

        return True, False, None

    def __insert_members(self, groupname, members):
        """
        """
        queries = []

        if self.members:
            group_id = self.__delete_all_members(groupname)

            # cursor, conn, error, message = self.__mysql_connect()
            #
            # if error:
            #     return None, error, message

            if group_id:
                for member in self.members:
                    queries.append(
                        f"insert ignore into icingaweb_group_membership (group_id, username, ctime, mtime) values ('{group_id}', '{member}', now(), now())"
                    )

            for q in queries:
                try:
                    cursor, conn, error, message = self.__mysql_connect()
                    if error:
                        return None, error, message

                    cursor.execute(q)
                    conn.commit()

                except Exception as e:
                    conn.rollback()
                    self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")

                finally:
                    cursor.close()

        else:
            _ = self.__delete_all_members(groupname)

        return True, False, None

    def __delete_all_members(self, groupname):
        """
        """
        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return None, error, message

        group_id = None

        q = f"select id from icingaweb_group where name = '{groupname}'"

        try:
            cursor.execute(q)
            group_id = cursor.fetchone()[0]
            # cursor, conn, error, message = self.__mysql_connect()
        except Exception:
            # nothing found
            pass
            # self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")

        if group_id:
            self.module.log(msg=f"found group id: {group_id} {type(group_id)}")

            q = f"delete from icingaweb_group_membership where group_id = {group_id}"

            try:
                cursor.execute(q)

            except Exception as e:
                conn.rollback()
                self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")

        conn.commit()
        conn.close()

        return group_id

    def __delete_group(self, groupname):
        """
        """
        cursor, conn, error, message = self.__mysql_connect()

        if error:
            return None, error, message

        q = f"delete from icingaweb_group where name = '{groupname}'"

        try:
            cursor.execute(q)

        except Exception as e:
            conn.rollback()
            self.module.fail_json(msg=f"Cannot execute SQL '{q}' : {to_native(e)}")

        conn.commit()
        conn.close()

        return True

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

        # self.module.log(msg="config : {}".format(config))

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


# ===========================================
# Module execution.
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["absent", "present"]),
            groupname=dict(required=True),
            parent=dict(required=False,),
            members=dict(required=False, default=True, type="list"),
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

    dba_group = IcingaWeb2DatabaseGroup(module)
    result = dba_group.run()

    module.log(msg=f"= result : '{result}'")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
