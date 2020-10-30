# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.utils.display import Display

import json
import crypt
import hashlib

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html
# https://blog.oddbit.com/post/2019-04-25-writing-ansible-filter-plugins/

display = Display()


class FilterModule(object):
    """
        Ansible file jinja2 tests
    """

    def filters(self):
        return {
            'create_password_hash': self.password_hash,
        }

    def password_hash(self, data):
        """

        """
        password_hash = ''

        temp_file = "/tmp/icingaweb2_users.json"

        count = len(data.keys())
        type_ = type(data.keys())

        display.vv("found: {} ({}) entries".format(count, type_))
        display.vv(json.dumps(data, indent=2, sort_keys=False))

        if(count != 0):
            for key in data.keys():
                password = data.get(key, {}).get('password')

                password_bytes = password.encode('utf-8')
                password_hash = hashlib.sha256(password_bytes)
                checksum = password_hash.hexdigest()

                if(password):
                    password_hash = self.__password_hash(password)

                    _ = data[key].pop('password')

                data[key]['hashed'] = password_hash
                data[key]['checksum'] = checksum

        display.vv(json.dumps(data, indent=2, sort_keys=False))

        with open("/tmp/icingaweb2_users.json", 'w') as fp:
            json.dump(data, fp)

        return data

    # https://docs.python.org/3/library/crypt.html
    def __password_hash(sef, plaintext):
        result = crypt.crypt(plaintext, crypt.METHOD_MD5)

        return result
