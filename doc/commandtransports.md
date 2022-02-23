# Commandtransport

## For an singulär Incinga Master:

creates `modules/monitoring/commandtransports.ini`

```yaml
icingaweb_commandtransport:
  master:
    transport: api
    host: 192.168.130.20
    port: 5665
    username: icingaweb
    password: S0mh1TuFJI
```

## For an Icinga2 HA Master Setup

```yaml
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
```
