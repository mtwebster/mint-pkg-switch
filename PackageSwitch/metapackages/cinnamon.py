#!/usr/bin/python

import Impl

class module(Impl.MetaPackage):
    NAME = "cinnamon"
    GIT_REPO_NAMES = [
        "cinnamon",
        "cinnamon-session",
        "cinnamon-settings-daemon",
        "cinnamon-control-center",
        "cjs",
        "cinnamon-desktop",
        "cinnamon-menus",
        "cinnamon-screensaver",
        "muffin",
        "nemo"                  # nemo should be its own metapackage I think, but there is a dependency issue.
                                # For some reason, you can't downgrade cinnamon without also downgrading nemo,
                                # even if the installed nemo satisfies the stated dependency.
    ]

    REFRESH_MECHANISM = "Reboot your computer."

    G_SETTINGS_SCHEMAS = ["org.cinnamon"]

    def save_and_reset_settings_hook(self):
        return True

    def restore_settings_hook(self):
        return True
