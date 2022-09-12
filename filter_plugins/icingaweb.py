# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.utils.display import Display

import json
import crypt

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html
# https://blog.oddbit.com/post/2019-04-25-writing-ansible-filter-plugins/

display = Display()


class FilterModule(object):
    """
        Ansible file jinja2 tests
    """

    def filters(self):
        return {
            'type': self.var_type,
            'create_password_hash': self.password_hash,
            'dict_from_list': self.dict_from_list,
            'module_version': self.module_version,
        }

    def var_type(self, var):
        """
          Get the type of a variable
        """
        return type(var).__name__

    def password_hash(self, data):
        """
        """
        password_hash = ''

        count = len(data.keys())
        type_ = type(data.keys())

        display.vv("found: {} ({}) entries".format(count, type_))
        display.vvv(json.dumps(data, indent=2, sort_keys=False))

        if (count != 0):
            for key in data.keys():
                password = data.get(key, {}).get('password')

                if (password):
                    password_hash = self.__password_hash(password)

                    _ = data[key].pop('password')

                data[key]['hashed'] = password_hash

        display.vvv(json.dumps(data, indent=2, sort_keys=False))

        with open("/tmp/icingaweb2_users.json", 'w') as fp:
            json.dump(data, fp)

        return data

    def dict_from_list(self, data, search):
        """
        """
        display.v("dict_from_list({}, {})".format(data, search))

        result = next((item for item in data if item.get('name') == search), {})

        display.v("result : {}".format(result))

        return result

    def module_version(self, data, module):
        """
        """
        version = None

        for d in data:
            if d.get("name") == module:
                version = d.get("version")

        return version

    # https://docs.python.org/3/library/crypt.html
    def __password_hash(sef, plaintext):
        result = crypt.crypt(plaintext, crypt.METHOD_MD5)

        return result
