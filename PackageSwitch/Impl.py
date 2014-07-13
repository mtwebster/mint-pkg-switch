#!/usr/bin/python

import util
import os
import gettext
import locale
from gi.repository import GLib

user_data = GLib.get_user_data_dir()

_ = gettext.gettext

# Any extra imports in your distro implementation here - wrap any failable or distro-specific ones in try/except (pass)
# import ...

class Distribution:
    NAME = "invalid"                    # module name
    NICE_NAME = "invalid"               # Display name - override if necessary, or set during identify()
    STASH_LOCATION = os.path.join(user_data, "pkgswitch") # Location to store settings

    def __init__(self):
        pass

    # returns whether this is the identified
    # distro or not.
    def identify(self):
        raise NotImplementedError()

    # install testing
    # return success
    def install_testing_packages(self, metapackage_name, source_list, skip_update):
        raise NotImplementedError()

    # install stable
    # return success
    def install_stable_packages(self, metapackage_name, source_list, skip_update):
        raise NotImplementedError()


class MetaPackage:
    NAME = "invalid"                    # module name
    GIT_REPO_NAMES = ["invalid"]        # List of repos that make up this metapackage
    G_SETTINGS_SCHEMAS = ["invalid"]    # List of gsettings schemas to save/reset for testing

    def __init__(self, distro):
        self.settings_op = util.S_OP_NONE
        self.distro = distro
        self.stash_dir = os.path.join(self.distro.STASH_LOCATION, self.NAME)
        self.setting_files = {}
        for schema in self.G_SETTINGS_SCHEMAS:
            self.setting_files[schema] = os.path.join(self.stash_dir, schema + ".backup")

    # calls this hook in your metapackage, in case you have special config save/reset needs
    # just return True if you don't use it.
    def save_and_reset_settings_hook(self):
        raise NotImplementedError()

    # calls this hook in your metapackage, in case you have special config restore needs
    # just return True if you don't use it.
    def save_and_reset_settings_hook(self):
        raise NotImplementedError()

    def ensure_stash_dir(self):
        if not os.path.exists(self.stash_dir):
            print self.stash_dir
            os.makedirs(self.stash_dir)

    def check_for_saved_settings(self):
        self.ensure_stash_dir()
        ret = False
        for schema in self.G_SETTINGS_SCHEMAS:
            if os.path.exists(self.setting_files[schema]):
                ret = True
            else:
                ret = False
                break
        return ret

    def save_and_reset_settings(self):
        self.ensure_stash_dir()
        for schema in self.G_SETTINGS_SCHEMAS:
            path = schema.replace(".", "/")
            path = "/" + path + "/"
            ret = os.system("dconf dump %s > %s" % (path, self.setting_files[schema]))
            if ret > 0:
                print _("Error saving schema %s.  Aborting rest of save process.") % schema
                return False
            else:
                print _("Schema: %s successfully saved.") % schema
                os.system("dconf reset -f %s" % path)
        return self.save_and_reset_settings_hook()

    def restore_settings(self):
        self.ensure_stash_dir()
        for schema in self.G_SETTINGS_SCHEMAS:
            path = schema.replace(".", "/")
            path = "/" + path + "/"
            ret = os.system("dconf load %s < %s" % (path, self.setting_files[schema]))
            if ret > 0:
                print _("Error restoring schema %s.  Aborting!") % schema
                return False
            else:
                print _("Schema: %s successfully restored.") % schema
                os.remove(self.setting_files[schema])
        return self.restore_settings_hook()

    def do_stable(self, s_op, skip_update):
        self.settings_op = s_op
        self.ensure_stash_dir()

        status = True

        status = self.distro.install_stable_packages(self.NAME, self.GIT_REPO_NAMES, skip_update)

        if status and self.settings_op == util.S_OP_RESTORE:
            print "\nRestoring your saved settings...you should reboot after this is complete.\n"
            status = self.restore_settings()

        if status:
            print ""
            print _("Successfully switched to the STABLE packages for %s.  Thanks for testing!\n") % self.NAME
            print "To make sure your system state is consistent with these packages, it is recommended that you:\n\n%s\n" % self.REFRESH_MECHANISM
        else:
            print _("Something went wrong, aborting...")
            exit()

    def do_testing(self, s_op, skip_update):
        self.settings_op = s_op
        self.ensure_stash_dir()

        status = True

        status = self.distro.install_testing_packages(self.NAME, self.GIT_REPO_NAMES, skip_update)

        if status and self.settings_op == util.S_OP_SAVE:
            print "Resetting your configuration to defaults...you should reboot after this is complete."
            status = self.save_and_reset_settings()

        if status:
            print "\n"
            print _("Successfully switched to the TESTING packages for %s.  Enjoy and be careful!\n") % self.NAME
            print "To switch back to the stable package, run:\n"
            if s_op == util.S_OP_SAVE:
                print "pkgswitch %s stable" % self.NAME
            elif s_op == util.S_OP_NONE:
                print "pkgswitch -n %s stable" % self.NAME
            print "\nTo make sure your system state is consistent with these packages, it is recommended that you:\n\n%s\n" % self.REFRESH_MECHANISM
        else:
            print _("\nSomething went wrong, aborting...")
            exit()


