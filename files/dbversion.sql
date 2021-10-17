CREATE TABLE `icingaweb_dbversion` (
  `dbversion_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(10) CHARACTER SET latin1 DEFAULT '',
  `version` varchar(10) CHARACTER SET latin1 DEFAULT '',
  `create_time` timestamp DEFAULT CURRENT_TIMESTAMP,
  `modify_time` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`dbversion_id`),
  UNIQUE KEY `dbversion` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
