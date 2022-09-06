#!/usr/bin/python3 -u

import subprocess
import yaml
import re
import logging

def shell_exec(command, shell=False, debug=False):
    process = subprocess.Popen(command,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        shell=shell)
    stdout, stderr = process.communicate()

    error = stderr != '' and ' already ' not in stderr

    if debug or error:
        print(command)
        print(stdout)
        print(stderr)

    if error:
        exit(1)

with open("repos.yaml", "r") as stream:
    try:
        repos = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

repo_names = []
for repo in repos:
    if "name" not in repo:
        logging.error("Il n'y a pas d'attribut name dans le repo")
        logging.error(repo)
        exit(1)

    (logging.error("Il n'y a pas d'attribut url dans le repo " + repo["name"]), exit(1)) if "url" not in repo else True
    (logging.error("Il n'y a pas d'attribut distributions dans le repo " + repo["name"]), exit(1)) if "distributions" not in repo else True
    (logging.error("Il n'y a pas d'attribut components dans le repo " + repo["name"]), exit(1)) if "components" not in repo else True
    (logging.error("Il n'y a pas d'attribut archs dans le repo " + repo["name"]), exit(1)) if "archs" not in repo else True

    (logging.error("Aucune distribution dans le repo " + repo["name"]), exit(1)) if len(repo["distributions"]) == 0 else True

    for distribution in repo["distributions"]:
        repo_names.append(repo["name"] + '-' + re.sub('[^A-Za-z0-9-_]+', '', distribution))

if len(repo_names) != len(set(repo_names)):
    logging.error('Il y a des conflits au niveau du nommage des repos:')
    logging.error(repo_names)
    exit(1)

def mirror_create(name, url, distribution, components, archs, shell=False, debug=False):
    command = ['aptly', 'mirror', 'create', '-ignore-signatures']
    command.append('-architectures=' + ','.join(archs))
    command.append(name)
    command.append(url)
    command.append(distribution)
    for component in components:
        command.append(component)
    shell_exec(command, shell, debug)

def mirror_update(name, archs, shell=False, debug=False):
    command = ['aptly', 'mirror', 'update', '-ignore-signatures']
    command.append('-architectures=' + ','.join(archs))
    command.append(name)
    shell_exec(command, shell, debug)

def snap_create(name, snap_name, shell=False, debug=False):
    command = ['aptly', 'snapshot', 'create']
    command.append(snap_name)
    command.append('from')
    command.append('mirror')
    command.append(name)
    shell_exec(command, shell, debug)

def snap_drop(name, shell=False, debug=False):
    command = ['aptly', 'snapshot', 'drop']
    command.append(name)
    shell_exec(command, shell, debug)

def publish_snap(name, url, override_path, shell=False, debug=False):
    command = ['aptly', 'publish', 'snapshot', '-skip-contents', '-skip-bz2', '-skip-signing']
    command.append(name)
    command.append('filesystem:fsSymlink:aptmirror/' + (override_path if override_path != '' else re.sub('http:?s?:\/\/', '', url)))
    shell_exec(command, shell, debug)

def publish_switch(name, url, distribution, override_path, shell=False, debug=False):
    command = ['aptly', 'publish', 'switch', '-skip-contents', '-skip-bz2', '-skip-signing']
    command.append('.-' + distribution[:-1] + '-' if distribution[-1:] == '/' else distribution)
    command.append('filesystem:fsSymlink:aptmirror/' + (override_path if override_path != '' else re.sub('http:?s?:\/\/', '', url)))
    command.append(name)
    shell_exec(command, shell, debug)
