import pytest
import os
import yaml
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def AnsibleDefaults():
    with open("../../defaults/main.yml", 'r') as stream:
        return yaml.load(stream)


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
    assert d.exists


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
    assert f.is_file


@pytest.mark.parametrize("links", [
    "/usr/share/icingaweb2",
    "/etc/icingaweb2/enabledModules/monitoring",
])
def test_links(host, links):
    f = host.file(links)
    assert f.exists
    assert f.is_symlink
