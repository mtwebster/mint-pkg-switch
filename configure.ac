dnl -*- Mode: autoconf -*-
dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.53)
AC_INIT(pkgswitch, 0.0.1, https://github.com/mtwebster/mint-pkg-switch)
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])
AC_CONFIG_SRCDIR(pkgswitch.in)
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE([1.7 no-dist-gzip dist-xz])
AM_MAINTAINER_MODE

dnl put the ACLOCAL flags in the makefile
ACLOCAL="$ACLOCAL $ACLOCAL_FLAGS"

GETTEXT_PACKAGE=pkgswitch
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.40.0])

AM_PATH_PYTHON_VERSION(2.7, 2.7.0, 2.6, 2.6.0, 2.5, 2.5.0, 2.4, 2.4.0)

AC_CONFIG_FILES([
        Makefile
        PackageSwitch/Makefile
        PackageSwitch/distros/Makefile
        PackageSwitch/metapackages/Makefile
        po/Makefile.in
        ])

AC_OUTPUT

