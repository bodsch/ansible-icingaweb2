# Icingaweb Module 

creates `modules/monitoring/config.ini`

```yaml
icingaweb_module:
  monitoring:
    security:
      protected_customvars:
        - '*http_auth_pair*'
        - '*password*'
```


## external Modules

Each module can be installed, activated and configured individually.

Currently the following external modules are supported:

- [audit](https://github.com/Icinga/icingaweb2-module-audit.git)
- [graphite](https://github.com/Icinga/icingaweb2-module-graphite.git)
- [grafana](https://github.com/Mikesch-mp/icingaweb2-module-grafana.git)


Do you have any wishes for further ... read the [Contribution](../CONTRIBUTING.md), create a PR or ask carefully. 

The following parameters can be used to influence the installation and activation: 

```yaml
icingaweb_external_modules:
  - audit:
    enabled: false
    name: audit
    src: https://github.com/Icinga/icingaweb2-module-audit.git
    version: v1.0.1
```

- `enabled` enabled or disable the module
- `name` a name for the installation
- `src` the sourcecode
- `version` the version

Additionally there is the possibility to configure the corresponding modules. 
The respective parameters are individual and will be explained separately.

Each configuration takes place in a `configuration` block.

### Audit

There are two different blocks [`Standard Log`](https://github.com/Icinga/icingaweb2-module-audit#standard-log) and 
[`JSON Log`](https://github.com/Icinga/icingaweb2-module-audit#standard-log).

The standard log (`log`) is a normal log with human readable messages. 
It's possible to log to a file and to syslog.

* `type`<br>
     One of these three possibilities are available:
     * `file` - log to a file
     * `syslog` - log in to syslog
     * `none` - log nothing
* `ident`<br>
     Syslog Ident<br>
     > *ident* is an arbitrary identification string which future syslog invocations will prefix to each message. 
     [see here](http://www.gnu.org/software/libc/manual/html_node/openlog.html)<br>
     (Only has an effect if 'type: syslog' has been defined)
* `facility`<br>
     Syslog facility<br>
     > ... default *facility* code for this connection
     [see here](http://www.gnu.org/software/libc/manual/html_node/openlog.html)<br>
     (Only has an effect if 'type: syslog' has been defined)
* `path`<br>
     The log file in which the audit information is stored.

The JSON log (`stream`) is supposed to be consumed by other applications. 
It writes one JSON object per line to a file.

* `format`<br>
     The format in which the data is stored. It is only available for `json`.<br>
     For more information, please consult the corresponding module documentation!
* `path`<br>
     The log file in which the audit information is stored.

```yaml
    configuration:
      log:
        # file / syslog / none
        type: file
        # ident = "web-ident"
        # facility = "authpriv"
        path: /var/log/icingaweb2/audit.log
      stream:
        # none / json
        format: json
        path: /var/log/icingaweb2/json.log
```

**Complete example:**

```yaml
icingaweb_external_modules:

  - audit:
    enabled: false
    name: audit
    src: https://github.com/Icinga/icingaweb2-module-audit.git
    version: v1.0.1
    configuration:
      log:
        type: file
        path: /var/log/icingaweb2/audit.log
      stream:
        format: json
        path: /var/log/icingaweb2/json.log
```

### Graphite

This module integrates an existing [Graphite](https://graphite.readthedocs.io/en/latest/) installation 
in the IcingaWeb frontend.

* `host`<br>
    The hostname for the corresponding graphite service
* `port`<br>
    The port for the graphite Web URL

These following credentials are only needed, when your Graphite Web is protected by a HTTP basic 
authentication mechanism.

* `user`<br>
    username for the basic authentication
* `password`<br>
    corresponding password for the basic authentication
* [`advanced`](https://github.com/Icinga/icingaweb2-module-graphite/blob/master/doc/03-Configuration.md#advanced)
    - `graphite_writer_host_name_template`
    - `graphite_writer_service_name_template`
    - `customvar_obscured_check_command` 
* [`ui`](https://github.com/Icinga/icingaweb2-module-graphite/blob/master/doc/03-Configuration.md#ui)<br>
   The settings `default_time_range` and `default_time_range_unit` set the default time range for displayed 
   graphs both in the graphs lists and in monitored objects' detail views.<br>
   If you'd like to suppress the No graphs found messages, activate `disable_no_graphs_found`

```yaml
    configuration:
      host: localhost
      port: 2003
      user: ''
      password: ''
      ui:
        default_time_range: 12
        default_time_range_unit: hours
        disable_no_graphs_found:  false
      advanced:
        graphite_writer_host_name_template: host.tpl
        graphite_writer_service_name_template: ''
        customvar_obscured_check_command: ''
```

**Complete example:**

```yaml
icingaweb_external_modules:

  - graphite:
    enabled: false
    name: graphite
    src: https://github.com/Icinga/icingaweb2-module-graphite.git
    version: v1.1.0
    # url: https://github.com/Icinga/icingaweb2-module-graphite/archive/v1.1.0.zip
    configuration:
      host: localhost
      ui:
        default_time_range: 12
        default_time_range_unit: hours
```


### Grafana

Add Grafana graphs into Icinga Web 2 to display performance metrics.


```yaml
    configuration:
      support_grafana_5: false
      host: tsdb.icinga.local
      port: 3000
      protocol: http
      timerange: 6h
      timerangeAll: 2d
      defaultdashboard:
        name: icinga2-default
        uid: Z-TfDRpGz
        panelid: 1
      defaultdashboard:
        name: icinga2-default
        uid: "Zm47ngtMk"
        panelid: "1"
      defaultorgid: "1"
      shadows: false
      theme: "light"
      datasource: "influxdb"
      accessmode: "direct"
      authentication:
      apitoken:
      username:
      password:
      indirectproxyrefresh:
      proxytimeout:
      directrefresh: "no"
      height: "280"
      width: "640"
      enableLink: true
      publichost:
      publicprotocol:
      debug: false
```

After configuring the Grafana connection, further graphs can be set up.

```yaml
    graphs:
      - ping4:
        dashboard: hostalive
        dashboarduid: Z-TfDRpGz
        panelId: 9
        orgId: 1
        repeatable: false
      - hostalive:
        dashboard: hostalive
        dashboarduid: Z-TfDRpGz
        panelId: 9
        orgId: 1
        repeatable: false
```


**Complete example:**

```yaml
icingaweb_external_modules:

  - grafana:
    enabled: false
    name: grafana
    src: https://github.com/Mikesch-mp/icingaweb2-module-grafana.git
    version: v1.3.6
    configuration:
      # support_grafana_5: false
      host: tsdb.icinga.local
      # port: 3000
      # protocol: http
      # timerange: 6h
      # timerangeAll: 2d
      defaultdashboard:
        # name: icinga2-default
        uid: Z-TfDRpGz
        # panelid: 1
      # defaultdashboard:
      #   name: icinga2-default
      #   uid: "Zm47ngtMk"
      #   panelid: "1"
      # defaultorgid: "1"
      # shadows: false
      # theme: "light"
      # datasource: "influxdb"
      # accessmode: "direct"
      # authentication
      # apitoken
      # username
      # password
      # indirectproxyrefresh
      # proxytimeout
      # directrefresh: "no"
      # height: "280"
      # width: "640"
      enableLink: true
      # publichost
      # publicprotocol
      # debug: true

    graphs:
      - ping4:
        dashboard: hostalive
        dashboarduid: Z-TfDRpGz
        panelId: 9
        orgId: 1
        repeatable: false
```
