#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: nix
short_description: Manage packages with Nix

'''

EXAMPLES = '''
# Install package foo
- nix: name=foo state=present
'''

import json
import os

NIX_PATH = os.environ['HOME'] + "/.nix-profile/bin/nix-env"

def query_package(module, name, state="present"):
    if state == "present":
        cmd = "nix-env -q %s" % (name)
        rc, stdout, stderr = module.run_command(cmd, check_rc=False)

        if rc == 0:
            return True

        return False

def install_packages(module, packages):
    install_c = 0

    for i, package in enumerate(packages):
        if query_package(module, package):
            continue

        cmd = "nix-env -i %s" % package
        rc, stdout, stderr = module.run_command(cmd, check_rc=False)

        if rc != 0:
            module.fail_json(msg="failed to install %s" % (package))

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg="installed %s package(s)" % (install_c))

    module.exit_json(changed=False, msg="package(s) already installed")

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name      = dict(aliases=['pkg']),
            state     = dict(default='present', choices=['present', 'installed', 'absent', 'removed'])),
        required_one_of = [['name']],
        supports_check_mode = True)

    if not os.path.exists(NIX_PATH):
        module.fail_json(msg="cannot find nix-env, looking for %s" % (NIX_PATH))

    p = module.params

    # normalize the state parameter
    if p['state'] in ['present', 'installed']:
        p['state'] = 'present'
    elif p['state'] in ['absent', 'removed']:
        p['state'] = 'absent'

    if p['name']:
        pkgs = p['name'].split(',')

        if p['state'] == 'present':
            install_packages(module, pkgs)

# import module snippets
from ansible.module_utils.basic import *

main()
