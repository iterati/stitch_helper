#!/usr/bin/env python3

import argparse
import subprocess
import sys

from stitch_helper import aws, services, tmux

HELP = """\
Valid commands:
\tvm - Starts the core vm and all necessary services

Valid services:
\t{services}"""

SESSIONS = [
    "app",
    "connections",
    "core",
    "menagerie",
    "reckoner",
]

def _main():
    args = sys.argv[1:]
    service_names = sorted(services.SERVICES.keys())

    if len(args) == 0:
        raise Exception(HELP.format(services="\n\t".join(service_names)))

    if args[0] == "vm":
        tmux.start_core_vm()
        for s in SESSIONS:
            service = services.Service(s, **services.SERVICES[s])
            tmux.Tmux().session(service)

        tmux.attach_session("core")

    elif args[0] in service_names:
        service = services.Service(args[0], **services.SERVICES[args[0]])
        if len(args) == 1:
            tmux.Tmux().session(service)
        else:
            cmd = args[1]
            if cmd == "list":
                service.list()
            elif cmd == "ssh":
                service.ssh()
            elif cmd == "db":
                service.db()
            else:
                raise Exception("Unknown command")

    else:
        raise Exception(HELP.format(services="\n\t".join(service_names)))


def main():
    try:
        _main()
    except Exception as e:
        print(e)
        sys.exit(1)
