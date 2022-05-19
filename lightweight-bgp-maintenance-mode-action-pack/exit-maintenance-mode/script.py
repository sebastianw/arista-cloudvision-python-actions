# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# This script is far less complex than inbuilt CVP one and simply Enters and Exits BGP MM
# for the unit System, regardless of traffic counters/etc.

# Why use this instead of built-in BGP MM script?
# The built-in BGP MM script actions contain a number of tests to see if entering MM was successful
# (keeps track of traffic volumes, whether BGP neighbors come up after reboot, etc.)
# These complexities make the built-in scripts hard to use in many real-world scenarios where one
# may have orphan ports causing minimum traffic thresholds to never be reached. This means the
# actions are prone to failure.
# This custom script does not include any of the tests, making it easier to use in scenarios where
# you have orphan ports or other conditions that are causing minimum traffic thresholds to never
# be reached.

from typing import List, Dict
from cloudvision.cvlib import ActionFailed

# Check if any custom maintenance config exists.
cmds = [
    "show maintenance units",
]
cmdResponse: List[Dict] = ctx.runDeviceCmds(cmds)
err = cmdResponse[0].get("error")
if err:
    raise ActionFailed(f"Showing maintenance units failed with: {err}")
response = cmdResponse[0]["response"]
unitsystemchanged = False
custommaintconfig = False
if "maintenanceUnits" in response:
    if len(response["maintenanceUnits"]) == 1 and "System" in response["maintenanceUnits"]:
        if response["maintenanceUnits"]["System"]["unitProfile"] != "Default":
            custommaintconfig = True
            unitsystemchanged = True
    else:
        custommaintconfig = True
        if response["maintenanceUnits"]["System"]["unitProfile"] != "Default":
            unitsystemchanged = True

ctx.info("Exiting Maintenance Mode due to CVP Change Control action.")
if custommaintconfig is False:
    cmds = [
        "enable",
        "configure",
        "default maintenance",
        "copy running-config startup-config",
    ]
elif unitsystemchanged is False:
    cmds = [
        "enable",
        "configure",
        "maintenance",
        "default unit System",
        "copy running-config startup-config",
    ]
else:
    cmds = [
        "enable",
        "configure",
        "maintenance",
        "unit System",
        "default quiesce",
        "copy running-config startup-config",
    ]


cmdResponses: List[Dict] = ctx.runDeviceCmds(cmds)
# Iterate through the list of responses for the commands, and if an error occurred in
# any of the commands, raise an exception
# Only consider the first error that is encountered as following commands require previous ones to succeed
errs = [resp.get('error') for resp in cmdResponses if resp.get('error')]
if errs:
    raise ActionFailed(f"Exiting maintenance mode failed with: {errs[0]}")
