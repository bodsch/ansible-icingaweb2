# Icingaweb Module 

creates `modules/monitoring/config.ini`

```
icingaweb_module:
  monitoring:
    security:
      protected_customvars:
        - '*http_auth_pair*'
        - '*password*'
```



## external Modules 

```
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
      - ping5:
        dashboard: hostalive
        dashboarduid: Z-TfDRpGz    
        panelId: 9
        orgId: 1
        repeatable: false
    
    
    
```
