# ansible role for icingaweb2

Install an Iicngaweb2 from the sources.

Supports various external modules and themes.

Supports an Icinga2 HA cluster.


## Requirements & Dependencies

 - running mariadb / mysql database
 - PHP > 7.0
 - nginx

### Operating systems

Tested on

* Debian 9 / 10
* Ubuntu 18.04 / 20.04
* CentOS 7 / 8

## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-icingaweb2/tags)!

---

Please read the following documention for configuration points.


## Documentation

- [Authentication](doc/athentication.md)
- [commandtransports](doc/commandtransports.md)
- [modules](doc/modules.md)
- [resources](doc/resources.md)
- [themes](doc/themes.md)
- [logging](doc/logging.md)

---

## Examples

A complete test setup can be found in the GitLab under [icinga2-infrastructure](https://gitlab.com/icinga2-infrastructure/deployment).

Or take e look into the [molecule](molecule/defaults/converge.yml) test.


## tests

For Example

```
MOLECULE_DISTRO=debian10 molecule converge
```

## License

BSD 2-clause
