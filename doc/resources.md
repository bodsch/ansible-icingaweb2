# Resources

creates `resources.ini`

```yaml
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
