
# Ansible Role:  `icingaweb2`

Install an icingaweb2 from [sources](https://github.com/Icinga/icingaweb2).

Supports various external modules and themes.

Supports also an Icinga2 HA cluster.


[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/bodsch/ansible-icingaweb2/CI)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-icingaweb2)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-icingaweb2)][releases]

[ci]: https://github.com/bodsch/ansible-icingaweb2/actions
[issues]: https://github.com/bodsch/ansible-icingaweb2/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-icingaweb2/releases


## BREAKING CHANGES

**Version 1.3.x to 1.4.x**

| 1.3.x | 1.4.x |
| :---- | :---- |
| `icingaweb_resources.db.icingaweb` | `icingaweb_resources.icingaweb` |
| `icingaweb_auth_backend`           | `icingaweb_auth_backend.database` |

**Version < 1.7.x**

| <= 1.7 | >= 1.8 |
| :---- | :---- |
| `icingaweb_users` | `icingaweb_db_users` |

**Version < 1.8.x**

Since version 1.8, the deployment of external themes and modules has been outsourced to separate Ansible roles.

| <= 1.8 | >= 1.8 |
| :---- | :---- |
| `icingaweb_themes` | removed |
| `icingaweb_themes_default` | removed |
| `icingaweb_external_modules` | removed |

## Why from sources?

The package offered by Icinga has a hard (and in my eyes unnecessary) dependency on Apache2.

This role also supports other distributions like ArchLinux, Gentoo by using the sources.

The source code archive is downloaded to the Ansible controller and then copied to the 
target system.
For this purpose, a temporary directory is created under `${HOME}/.cache/ansible/icingaweb`

If you want a different directory, you can specify an individual directory by setting the 
environment variable `CUSTOM_LOCAL_TMP_DIRECTORY`.


## Requirements & Dependencies

 - running mariadb / mysql database
 - PHP > 7.0, < 8.x
 - nginx

## tested operating systems

* ArchLinux
* Debian based
    - Debian 10 / 11
    - Ubuntu 20.04
* RedHat based
    - Alma Linux 8
    - Rocky Linux 8
    - OracleLinux 8

## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-icingaweb2/tags)!

---

Please read the following documention for configuration points.


## Documentation

- [Authentication](doc/authentication.md)
- [Users and Groups](doc/database_users_and_groups.md)
- [commandtransports](doc/commandtransports.md)
- [resources](doc/resources.md)
- [logging](doc/logging.md)
- [icingadb](doc/icingadb.md)

---

## Examples

Take a look into the [molecule](molecule) directory.
Some example configurations are stored there:

- [simple installation](molecule/default)
- [update from 2.7.0 to 2.8.2](molecule/update_2.7.0-2.8.2)
- [update from 2.8.2 to 2.9.3](molecule/update_2.8.2-2.9.3)
- [with icingadb](molecule/icingadb)

Or a complete test setup can be found in GitLab under [icinga2-infrastructure](https://gitlab.com/icinga2-infrastructure/deployment).


## tests

For Example

```bash
tox -e py39-ansible510 -- molecule test
```
or
```bash
tox -e py310-ansible510 -- molecule test --scenario-name update_2.7.0-2.8.2
```
or
```bash
tox -e py310-ansible510 -- molecule test --scenario-name with-icingadb

```
## License

BSD 2-clause
