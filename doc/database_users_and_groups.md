# Users and groups in database

The simplest way to define users and groups is to store them in the database.

You can use the following variables to do this:

- `icingaweb_db_groups`
- `icingaweb_db_users`

# Groups


In addition to a group, you can also define the corresponding members and - if desired - specify a parent group:

```yaml
icingaweb_db_groups:
  - groupname: "admin-root"
    members:
      - admin
  - groupname: "admin"
    parent: "admin-root"
    members:
      - admin      
      - bodsch
  - groupname: "admins_2"
    state: absent
```

# Users

In addition to creating the user, you can also roll out the desired user configurations here:

```yaml
icingaweb_db_users:
  - admin:
    username: admin
    password: admin
    preferences:
      language: de_DE
      timezone: Europe/Berlin
      show_application_state_messages: false
      show_stacktraces: false
      show_benchmark: false
      auto_refresh: true
```
