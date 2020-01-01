#!/bin/bash

insert_user_into_database() {

  local user="${1}"
  local pass="${2}"

  pass=$(openssl passwd -1 ${pass})

  # insert default icingauser
  (
    echo "USE icinga2_auth;"
    echo "INSERT IGNORE INTO icingaweb_user (name, active, password_hash) VALUES ('${user}', 1, '${pass}');"
    echo "quit"
  ) | mysql ${MYSQL_OPTS}

  if [[ $? -gt 0 ]]
  then
    echo "ERROR can't create the icingaweb user"
    exit 1
  fi
}

# create (or add) the user(s) to the admin role
#
insert_users_into_role() {

  local user_list="${1}"

  if [[ $(grep -c "\[local admins\]" /etc/icingaweb2/roles.ini 2> /dev/null) -eq 0 ]]
  then
    cat << EOF > /etc/icingaweb2/roles.ini
[local admins]
users               = "${user_list}"
permissions         = "*"

EOF
  else

    sed -i \
      -e "/^users.*=/s/=.*/= ${user_list}/" \
      /etc/icingaweb2/roles.ini
  fi
}

create_login_user() {

  local users=
  local users_list=()

  if [[ -e /etc/icingaweb2/icingaweb_users.json ]]
  then
    for user in $(cat /etc/icingaweb2/icingaweb_users.json | jq --raw-output '. | to_entries | .[] | .key')
    do
      pass="$(cat /etc/icingaweb2/icingaweb_users.json | jq --raw-output ".[\"${user}\"].password")"

      [[ -z ${pass} ]] && pass=${user}

      echo "  - '${user}'"

      # insert_user_into_database ${user} ${pass}

      users_list=("${users_list[@]}" "${user}")
    done
  fi

  lst=$( IFS=','; echo "${users_list[*]}" );

  insert_users_into_role ${lst}
}

create_login_user
