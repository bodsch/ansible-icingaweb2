# Authentication

creates `authentication.ini`

```
icingaweb_auth_backend: "{{ icingaweb_resources.db.icingaweb }}" 

icingaweb_authentication:
  auth_db:
    backend: db
    resource: icingaweb

  auth_ldap:
    resource: ldap
    user_class: inetOrgPerson
    user_name_attribute: uid
    backend:  ldap
    base_dn: dc=ldap,dc=cm,dc=local
    domain: ldap.cm.local
```
