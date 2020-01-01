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
    "/tmp/deployment_artefacts",
    "/etc/ansible/facts.d",
    "/opt/jolokia/"
])
def test_directories(host, dirs):
    d = host.file(dirs)
    assert d.is_directory
    assert d.exists


# @pytest.mark.parametrize("files", [
#     "/opt/jolokia/jolokia-agent.jar"
# ])
# def test_files(host, files):
#     f = host.file(files)
#     assert f.exists
#     assert f.is_file


def test_user(host):
    assert host.group("jolokia").exists
    assert host.user("jolokia").exists
    assert "jolokia" in host.user("jolokia").groups
    assert host.user("jolokia").shell == "/sbin/nologin"
    assert host.user("jolokia").home == "/opt/jolokia"
