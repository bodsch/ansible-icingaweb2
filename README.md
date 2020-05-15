# ansible role for icingaweb2

## examples

```
icingaweb_auth_backend:
  icingaweb:
    type: db
    db: mysql
    host: 192.168.130.10
    port: 3306
    dbname: "{{ icingaweb_auth_dba_database }}"
    username: "{{ icingaweb_auth_dba_username }}"
    password: "{{ icingaweb_auth_dba_password }}"
    prefix: icingaweb_
    charset: utf8

  icinga_ido:
    type: db
    db: mysql
    host: 192.168.130.10
    port: 3306
    dbname: "{{ icinga2_ido_database }}"
    username: "{{ icinga2_ido_username }}"
    password: "{{ icinga2_ido_password }}"
    charset: utf8


icingaweb_commandtransport:
  master-1:
    transport: api
    host: 192.168.130.20
    port: 5665
    username: icingaweb
    password: S0mh1TuFJI
  master-2:
    transport: api
    host: 192.168.130.21
    port: 5665
    username: icingaweb
    password: S0mh1TuFJI


icingaweb_module:
  monitoring:
    security:
      protected_customvars:
        - '*http_auth_pair*'
        - '*password*'
```
