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


icingaweb_resources:
  db:
    icingaweb-mysql-tcp:
      db: mysql
      host: 127.0.0.1
      port: 3306
      username: icingaweb
      password: icingaweb
      dbname: icingaweb
    icingaweb-mysql-socket:
      db: mysql
      host: /var/run/mysql.socket
      port: 3306
      username: icingaweb
      password: icingaweb
      dbname: icingaweb

  ldap:
    ldap_matrix:
      hostname: localhost
      port: 389
      root_dn: dc=ldap,dc=cm,dc=local
      bind_dn: cn=Manager,dc=ldap,dc=cm,dc=local
      bind_pw: "{{ vault__openldap__rootpw }}"
      encryption: none
      timeout: 5
    ap_foo:
      hostname: localhost
      port: 389
      root_dn: "ou=people,dc=icinga,dc=org"
      bind_dn: "cn=admin,ou=people,dc=icinga,dc=org"
      bind_pw: admin
      encryption: none
      timeout: 5

  ssh:
    ssh-user:
      user: ssh-user
      private_key: /etc/icingaweb2/ssh/ssh-user
```
