#!/usr/bin/env python
"""
A simple wrapper to the resin CLI (faster than understanding the full API)
which will show if a nodes is currently online

Author: Philip Basford
Date: 17/07/2017
Contact: P.J.Basford@soton.ac.uk

"""
import subprocess
from datetime import datetime, timedelta
import argparse
import pytz
import dateutil.parser

CMD_LINE = "/usr/local/bin/resin"
STATUS_CMD = "device"

EXIT_OK = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2
EXIT_UNKNOWN = 3

def check_online(node_id):
    """
        Checks that the specified node is reporting as online
    """
    status = _get_status(node_id)
    online = status['IS ONLINE:']
    if online:
        return (EXIT_OK, "OK: Node is online")
    else:
        return (EXIT_CRTICAL, "CRITICAL: Node is offline")

def _get_status(node_id):
    (status, output) = _run_cmd("%s %s" % (STATUS_CMD, node_id))
    if status == 0: #Double check exit status
        return _parse_status(output)

def _run_cmd(arguments):
    cmd = subprocess.Popen(
        args="%s %s" %(CMD_LINE, arguments),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    exit_status = cmd.wait()
    if exit_status != 0:    #Failed to run happily
        raise ResinCheckError("Unknown: Command execution failed")
    output = cmd.communicate()[0]
    return exit_status, output.split("\n")

def _parse_status(output):
    data = {}
    for line in output:
        if not line.startswith("="):
            key = line[:19].strip()
            value = line[20:].strip()
            data[key] = value
    return data


class ResinCheckError(Exception):
    """
        Generic error for when things go wrong
    """
    pass


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Resin node status checker")
    PARSER.add_argument(
        "-n", "--node", type=str, action='store', required=True,
        help="The ID of the node to check")
    ARGS = PARSER.parse_args()
    try:
        (STATUS, MESSAGE) = check_online(ARGS.node)
    except ResinCheckError as err:
        print str(err)
        exit(EXIT_UNKNOWN)
    print MESSAGE
    exit(STATUS)
