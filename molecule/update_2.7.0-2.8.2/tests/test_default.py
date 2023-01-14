
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
import pytest
import os
import testinfra.utils.ansible_runner

import pprint
pp = pprint.PrettyPrinter()

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('instance')


def base_directory():
    cwd = os.getcwd()
    pp.pprint(cwd)
    pp.pprint(os.listdir(cwd))

    if ('group_vars' in os.listdir(cwd)):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = "molecule/{}".format(os.environ.get('MOLECULE_SCENARIO_NAME'))

    return directory, molecule_directory


@pytest.fixture()
def get_vars(host):
    """

    """
    base_dir, molecule_dir = base_directory()

    # pp.pprint(" => '{}' / '{}'".format(base_dir, molecule_dir))

    file_defaults = "file={}/defaults/main.yml name=role_defaults".format(base_dir)
    file_vars = "file={}/vars/main.yml name=role_vars".format(base_dir)
    file_molecule = "file={}/group_vars/all/vars.yml name=test_vars".format(molecule_dir)

    # pp.pprint(file_defaults)
    # pp.pprint(file_vars)
    # pp.pprint(file_molecule)

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(molecule_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


@pytest.mark.parametrize("dirs", [
    "/etc/icingaweb2",
    "/etc/icingaweb2/dashboards",
    "/etc/icingaweb2/modules",
    "/etc/icingaweb2/enabledModules",
    "/var/log/icingaweb2",
])
def test_directories(host, dirs):
    d = host.file(dirs)
    assert d.is_directory


@pytest.mark.parametrize("files", [
    "/etc/icingaweb2/authentication.ini",
    "/etc/icingaweb2/config.ini",
    "/etc/icingaweb2/groups.ini",
    "/etc/icingaweb2/resources.ini",
    "/etc/icingaweb2/roles.ini",
    "/etc/icingaweb2/modules/monitoring/backends.ini",
    "/etc/icingaweb2/modules/monitoring/commandtransports.ini",
    "/etc/icingaweb2/modules/monitoring/config.ini",
])
def test_files(host, files):
    f = host.file(files)
    assert f.exists


@pytest.mark.parametrize("links", [
    "/usr/share/icingaweb2",
    "/etc/icingaweb2/enabledModules/monitoring",
])
def test_links(host, links):
    f = host.file(links)
    assert f.is_symlink
