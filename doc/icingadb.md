# IcingaDB

[upstream dokumentation](https://icinga.com/docs/icinga-db/latest/icinga-db-web)

In order to use *icingadb*, several parameters are required:

- We need a resource
- The module must be installed
- And of course configured

## Resource definition

```yaml
icingaweb_resources:

  icingadb:
    type: db
    db: mysql
    host: database
    port: 3306
    dbname: "{{ icingadb_database.database }}"
    username: "{{ icingadb_database.user }}"
    password: "{{ icingadb_database.password }}"
    charset: utf8
```

## Installation

```yaml
icingaweb_icingadb:

  module:
    enabled: true
    src: https://github.com/Icinga/icingadb-web
    version: v1.0.0-rc2
```

## Configuration

```yaml
icingaweb_icingadb:

  database: icingadb
  commandtransports:
    master-1:
      transport: api
      host: icinga2
      port: 5665
      username: icingaweb
      password: S0mh1TuFJI  
  redis:
    tls: false
    primary:
      host: icingadb
      port: 6379
    secondary: {}
```

`database` refers to the database defined under `icingaweb_resources`.

`commandtransports` has the same structure as `icingaweb_commandtransport`. 
If a configuration already exists there, you can also reuse it:

```yaml
icingaweb_icingadb:

  commandtransports: "{{ icingaweb_commandtransport }}"
```

Under `redis` you can configure whether TLS should be used and which Redis instances you want to use.
Currently you can define 2 hosts here:

```yaml
icingaweb_icingadb:

  redis:

    primary:
      host: icingadb-1
      port: 6379
    secondary:
      host: icingadb-2
      port: 6379
```

### Full example

```yaml
icingaweb_icingadb:
  module:
    enabled: false
    src: https://github.com/Icinga/icingadb-web
    version: v1.0.0-rc2
  database: icingadb
  commandtransports:
    master-1:
      transport: api
      host: icinga2
      port: 5665
      username: icingaweb
      password: S0mh1TuFJI
  redis:
    tls: false
    primary:
      host: ""
      port: 6380
    secondary: {}
```
