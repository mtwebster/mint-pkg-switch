#!/usr/bin/python

import Impl
import os

SERIES_MAP = {
    "qiana" : "trusty"
}

PPA = "ppa:gwendal-lebihan-dev/cinnamon-nightly"

try:
    from launchpadlib.launchpad import Launchpad
    import platform
    import apt
except:
    print "Missing required library: python-launchpadlib"
    print "Updating package list..."
    os.system("sudo apt-get update")
    print "Installing..."
    ret = os.system("sudo apt-get install -y python-launchpadlib")
    if ret > 0:
        pass
    else:
        from launchpadlib.launchpad import Launchpad
        print "Complete!"

class module(Impl.Distribution):
    NAME = "linuxmint"
    NICE_NAME = "Linux Mint"
    CODE_NAME = "invalid"

    def identify(self):
        import os
        import commands
        if os.path.exists("/etc/linuxmint/info"):
            self.NICE_NAME = commands.getoutput("awk -F \"=\" '/GRUB_TITLE/ {print $2}' /etc/linuxmint/info")
            self.CODE_NAME = commands.getoutput("awk -F \"=\" '/CODENAME/ {print $2}' /etc/linuxmint/info")
            
            if "linux mint" in self.NICE_NAME.lower():
                return True
            else:
                return False

    def get_arch_string(self):
        arch = ""
        if "64" in platform.machine():
            arch = "amd64"
        else:
            arch = "i386"
        return arch

    def install_testing_packages(self, metapackage_name, source_list, skip_update):
        arch = self.get_arch_string()

        matching_sources = []

        launchpad = Launchpad.login_anonymously('pkgswitch', 'production', os.path.join(os.getenv("HOME"), ".launchpadlib", "cache"))
        ppa = launchpad.load("https://api.launchpad.net/1.0/~gwendal-lebihan-dev/+archive/cinnamon-nightly")
        ppa_sources = ppa.getPublishedSources(status = "Published")
        
        # Make sure all our metapackage sources are available, for our series (code name)
        for source in ppa_sources:
            if source.source_package_name in source_list and SERIES_MAP[self.CODE_NAME] in source.distro_series_link:
                matching_sources.append(source)
                
        if len(matching_sources) != len(source_list):
            print "Could not find all source packages required for this metapackage.  Aborting!"
            return False

        # Figure out provided package names and their latest published/built versions

        print "\nFinding packages, please wait...\n"

        resolved_packages = []

        for source in matching_sources:
            for bin in source.getPublishedBinaries():
                if bin.distro_arch_series_link.endswith(arch):
                    resolved_packages.append((bin.binary_package_name, bin.binary_package_version))
                    print "Found: %s_%s" % (bin.binary_package_name, bin.binary_package_version)

        # Add the PPA

        print "\n\nAdding Cinnamon nightly PPA...\n\n"

        if os.system("sudo add-apt-repository -y %s" % PPA) > 0:
            print "Something went wrong trying to add the repository: %s" % PPA
            return False

        # Refresh

        if not skip_update:
            print "\n\nUpdating repositories...\n\n"
            os.system("sudo apt-get update")

        # Install

        print "\n\nInstalling testing packages.  Please wait...\n\n"

        pkg_string = ""

        for name, version in resolved_packages:
            pkg_string += "%s/%s " % (name, SERIES_MAP[self.CODE_NAME])

        if os.system("sudo apt-get install %s" % pkg_string) > 0:
            print "Something went wrong trying to install the testing packages.\n"
            print "You should immediately run:\n\npkgswitch -n %s stable" % metapackage_name
            return False

        return True

    def install_stable_packages(self, metapackage_name, source_list, skip_update):
        arch = self.get_arch_string()

        # Refresh

        if not skip_update:
            print "\n\nUpdating repositories...\n\n"
            os.system("sudo apt-get update")

        # Figure out provided package names and their latest published/built versions

        print "\n\nFinding packages, please wait...\n\n"

        cache = apt.Cache()
        cache.open()

        resolved_packages = []

        for name in cache.keys():
            pkg = cache[name]
            if pkg.architecture() != arch:
                continue
            for version in pkg.versions:
                if version.source_name in source_list:
                    # print version.source_name, version.version, pkg.name, len(version.origins)
                    if self.CODE_NAME in version.version or self.CODE_NAME == version.origins[0].archive:
                        resolved_packages.append((pkg.name, version.version))
                        print "Found: %s_%s" % (pkg.name, version.version)

        # Install

        print "\n\nInstalling stable packages.  Please wait...\n\n"

        pkg_string = ""

        for name, version in resolved_packages:
            pkg_string += "%s/%s " % (name, self.CODE_NAME)

        if os.system("sudo apt-get install %s" % pkg_string) > 0:
            print "Something went wrong trying to downgrade to the stable packages.\n"
            print "You should immediately run:\n\npkgswitch -n %s testing, then try this again later." % metapackage_name
            return False

        return True

