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


icingaweb_themes:
  - unicorn:
    name: unicorn
    src: https://github.com/Mikesch-mp/icingaweb2-theme-unicorn.git
    version: v1.0.2
    image: { name: "unicorn.png", "url": "http://i.imgur.com/SCfMd.png" }
  - batman-dark:
    name: batman-dark
    src: https://github.com/jschanz/icingaweb2-theme-batman-dark.git
    version: v1.0.0



# if users should not be allowed to change their theme
icingaweb_themes_disabled: true

# Can be set to 'Icinga', 'high-contrast', 'Winter', ‘colorblind’ or your own installed theme
icingaweb_themes_default: Icinga

icingaweb_external_modules:

  - audit:
    enabled: false
    name: audit
    src: https://github.com/Icinga/icingaweb2-module-audit.git
    version: v1.0.1
    # configuration:
    #   log:
    #     # file / syslog / none
    #     type: file
    #     # ident = "web-ident"
    #     # facility = "authpriv"
    #     path: /var/log/icingaweb2/audit.log
    #   stream:
    #     # none / json
    #     format: json
    #     path: /var/log/icingaweb2/json.log

  - graphite:
    enabled: false
    name: graphite
    src: https://github.com/Icinga/icingaweb2-module-graphite.git
    version: v1.1.0
    # url: https://github.com/Icinga/icingaweb2-module-graphite/archive/v1.1.0.zip
    configuration:
      host: localhost
      port: 2003
      # host: tsdb-1.icinga.local
      # port: 8088
      user: ''
      password: ''
      # ui:
      #   default_time_range: 12
      #   default_time_range_unit: hours
      # advanced:
      #   # graphite_writer_host_name_template: host.tpl
      #   # graphite_writer_service_name_template: ''
      #   # customvar_obscured_check_command: ''

  - grafana:
    enabled: false
    name: grafana
    src: https://github.com/Mikesch-mp/icingaweb2-module-grafana.git
    version: v1.3.6


# /etc/icingaweb2/authentication.ini
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


```
icingaweb_log_level: DEBUG

icingaweb_resources:
  db:
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

icingaweb_auth_backend: "{{ icingaweb_resources.db.icingaweb }}"

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

icinga2_api:
  user:
    icingaweb:
      password: S0mh1TuFJI

```
