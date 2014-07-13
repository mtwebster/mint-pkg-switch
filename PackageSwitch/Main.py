#!/usr/bin/python

import os
import sys
import optparse
from optparse import OptionParser
import util
import gettext, locale

from PackageSwitch import config

sys.path.append(os.path.join(config.pkgdatadir, "PackageSwitch"))
sys.path.append(os.path.join(config.pkgdatadir, "PackageSwitch", "metapackages"))
sys.path.append(os.path.join(config.pkgdatadir, "PackageSwitch", "distros"))

gettext.bindtextdomain(config.GETTEXT_PACKAGE, config.localedir)
gettext.textdomain(config.GETTEXT_PACKAGE)
locale.bind_textdomain_codeset(config.GETTEXT_PACKAGE,'UTF-8')
_ = gettext.gettext

class Main:
    def __init__(self):
        self.settings_op = util.S_OP_NONE

        print ""
        print _("pkgswitch - metapackage testing tool")
        print ""

        self.distro = self.determine_distro()

        if not self.distro:
            print "Unsupported distribution found!  Aborting."
            quit()

        self.meta_packages = self.load_metapackages()

        meta_string = ""
        for meta in self.meta_packages:
            if meta_string != "":
                meta_string += ", "
            meta_string += "%s" % meta.NAME

        usage = "pkgswitch [-n] <meta-package> stable | testing"

        parser = OptionParser(usage=usage, add_help_option=False)
        parser.add_option("-n", "--nosettings", action="store_true", dest="skip_settings", default=False,
                          help="Skips the interactive question of whether to back your meta-package's settings up or not.  Settings are not altered in any way.")
        parser.add_option("-s", "--skipupdate", action="store_true", dest="skip_update", default=False,
                          help="Skips the time-consuming apt cache update.  Use this if you're frequently switching back and forth within a short timeframe.")

        (options, args) = parser.parse_args()

        self.skip_settings = options.skip_settings
        self.skip_update = options.skip_update

        if not args or len(args) < 2:
            self.print_help(parser, meta_string)
            quit()

        pkgname = args[0]
        self.op_type = args[1]

        if pkgname not in meta_string.split(", "):
            self.print_help(parser, meta_string)
            quit()

        if self.op_type not in ("stable", "testing"):
            self.print_help(parser, meta_string)
            quit()

        self.selected_meta_package = None

        for meta in self.meta_packages:
            if meta.NAME == pkgname:
                self.selected_meta_package = meta
                break

        if self.selected_meta_package == None:
            print "Had trouble determining the desired metapackage to work with.  Sorry!"
            quit()

        self.settings_op = self.prep_settings()

        if self.op_type == "stable":
            self.selected_meta_package.do_stable(self.settings_op, self.skip_update)
        else:
            self.selected_meta_package.do_testing(self.settings_op, self.skip_update)

    def print_help(self, parser, meta_string):
        parser.print_help()
        print """
  <meta-package> - The name of the meta-package to you wish to switch.

  stable - switch to the current, stable versions of the meta-package's
      packages.  If you're already on stable, this will do nothing.

  testing - switch to the latest available testing version of the meta-
      package's packages.  If you're already on the latest version, this
      will do nothing.  If you're running a testing version, but it is
      not the latest, this will upgrade to the latest.

  Example: mint-pkg-channel cinnamon testing (Test out latest cinnamon, guided)

  Current distribution: %s
  Available meta-packages: %s

"""  % (self.distro.NICE_NAME, meta_string)

    def prep_settings(self):
        # Not actually doing anything with settings at this point, will wait to be
        # sure the switch-over was successful
        ret = util.S_OP_NONE

        if not self.skip_settings:
            if self.op_type == "testing":
                print _("Reset your settings for %s?  They will be saved so they can be restored later." % self.selected_meta_package.NAME)
                print _("This is recommended if you are confirming a bug or testing a fix to a bug.\n")
                query = raw_input("y/n (n): ")
                if query.lower() == "y":
                    ret = util.S_OP_SAVE
            elif self.op_type == "stable":
                if self.selected_meta_package.check_for_saved_settings():
                    print _("Restore your previously saved settings for %s?  They will overwrite your current settings." % self.selected_meta_package.NAME)
                    print _("You probably want to do this if you had previously reset your settings for bug testing.\n")
                    query = raw_input("y/n (n): ")
                    if query.lower() == "y":
                        ret = util.S_OP_RESTORE
                else:
                    print _("No previously saved settings found, moving on...")
                    ret = util.S_OP_NONE
        return ret

    def determine_distro(self):
        distros = util.distro_loader(os.path.join(config.pkgdatadir, "PackageSwitch", "distros"))
        for distro in distros:
            try:
                if distro.identify():
                    return distro
            except:
                continue
        return None

    def load_metapackages(self):
        return util.meta_loader(os.path.join(config.pkgdatadir, "PackageSwitch", "metapackages"), self.distro)

def main():
    Main()
