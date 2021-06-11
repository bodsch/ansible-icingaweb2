
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


## Why from sources?

The package offered by Icinga has a hard (and in my eyes unnecessary) dependency on Apache2.

This role also supports other distributions like ArchLinux, Gentoo by using the sources.

## Requirements & Dependencies

 - running mariadb / mysql database
 - PHP > 7.0
 - nginx

### Operating systems

Tested on

* Debian 10
* Ubuntu 18.04 / 20.04
* CentOS 7 / 8
* OracleLinux 7 / 8

## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-icingaweb2/tags)!

---

Please read the following documention for configuration points.


## Documentation

- [Authentication](doc/authentication.md)
- [commandtransports](doc/commandtransports.md)
- [modules](doc/modules.md)
- [resources](doc/resources.md)
- [themes](doc/themes.md)
- [logging](doc/logging.md)

---

## Examples

A complete test setup can be found in GitLab under [icinga2-infrastructure](https://gitlab.com/icinga2-infrastructure/deployment).

Or take e look into the [molecule](molecule/defaults/converge.yml) test.


## tests

For Example

```
$ tox -e py39-ansible210 -- molecule test
```

## License

BSD 2-clause
