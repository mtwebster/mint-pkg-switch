## Process this file with automake to produce Makefile.in

SUBDIRS = PackageSwitch po

CLEANFILES=

bin_SCRIPTS = pkgswitch
CLEANFILES += pkgswitch

DISTCLEANFILES = ChangeLog

pkgswitch: pkgswitch.in
	$(AM_V_GEN)sed -e s!\@PYTHON\@!@PYTHON@!	\
	    -e s!\@PYOPTIONS\@!-OOt!			\
	    < $< > $@
pkgswitch: Makefile

EXTRA_DIST = \
	pkgswitch.in \
	MAINTAINERS

ChangeLog:
	@echo Creating $@
	@if test -d "$(srcdir)/.git"; then \
	  (GIT_DIR=$(top_srcdir)/.git ./missing --run git log git-migration.. --stat -M -C --name-status  --date=short --no-color) | fmt --split-only > $@.tmp \
	  && mv -f $@.tmp $@ \
	  || ($(RM) $@.tmp; \
	      echo Failed to generate ChangeLog, your ChangeLog may be outdated >&2; \
	      (test -f $@ || echo git-log is required to generate this file >> $@)); \
	else \
	  test -f $@ || \
	  (echo A git checkout and git-log is required to generate ChangeLog >&2 && \
	   echo A git checkout and git-log is required to generate this file >> $@); \
	fi
	
