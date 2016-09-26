##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Install packages as eggs
"""
import logging
import os
import re
import sys

import zc.buildout.easy_install

logger = logging.getLogger(__name__)


class Base:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        options['_d'] = buildout['buildout']['develop-eggs-directory']
        options['_e'] = buildout['buildout']['eggs-directory']


        environment_section = options.get('environment')
        if environment_section:
            self.environment = buildout[environment_section]
        else:
            self.environment = {}
        environment_data = list(self.environment.items())
        environment_data.sort()
        options['_environment-data'] = repr(environment_data)

        self.build_ext = build_ext(buildout, options)

        links = options.get('find-links',
                            buildout['buildout'].get('find-links'))
        if links:
            links = links.split()
            options['find-links'] = '\n'.join(links)
        else:
            links = ()
        self.links = links

        index = options.get('index', buildout['buildout'].get('index'))
        if index is not None:
            options['index'] = index
        self.index = index

        self.newest = buildout['buildout'].get('newest') == 'true'



    def install(self):
        self._set_environment()
        try:
            self._install_setup_eggs()
            return self._install()
        finally:
            self._restore_environment()

    def update(self):
        return self.install()

    def _set_environment(self):
        self._saved_environment = {}
        for key, value in list(self.environment.items()):
            if key in os.environ:
                self._saved_environment[key] = os.environ[key]
            # Interpolate value with variables from environment. Maybe there
            # should be a general way of doing this in buildout with something
            # like ${environ:foo}:
            os.environ[key] = value % os.environ

    def _restore_environment(self):
        for key in self.environment:
            if key in self._saved_environment:
                os.environ[key] = self._saved_environment[key]
            else:
                try:
                    del os.environ[key]
                except KeyError:
                    pass

    def _install_setup_eggs(self):
        options = self.options
        setup_eggs = [
            r.strip()
            for r in options.get('setup-eggs', '').split('\n')
            if r.strip()]
        if setup_eggs:
            ws = zc.buildout.easy_install.install(
                setup_eggs, options['_e'],
                links=self.links,
                index=self.index,
                executable=sys.executable,
                path=[options['_d'], options['_e']],
                newest=self.newest,
                )
            extra_path = os.pathsep.join(ws.entries)
            os.environ['PYTHONEXTRAPATH'] = extra_path

    def _get_patch_dict(self, options, distribution):
        patch_dict = {}
        global_patch_binary = options.get('patch-binary', 'patch')
        def get_option(egg, key, default):
            return options.get('%s-%s' % (egg, key),
                               options.get(key, default))
        egg = re.sub('[<>=].*', '', distribution)
        patches = filter(lambda x:x,
                         map(lambda x:x.strip(),
                             get_option(egg, 'patches', '').splitlines()))
        patches = list(patches)
        if not patches:
            return patch_dict
        patch_options = get_option(egg, 'patch-options', '-p0').split()
        patch_binary = get_option(egg, 'patch-binary', global_patch_binary)
        patch_revision = int(get_option(egg, 'patch-revision', len(patches)))
        patch_dict[egg] = {
          'patches':patches,
          'patch_options':patch_options,
          'patch_binary':patch_binary,
          'patch_revision':patch_revision,
        }
        return patch_dict

class Custom(Base):

    def __init__(self, buildout, name, options):
        Base.__init__(self, buildout, name, options)

        if buildout['buildout'].get('offline') == 'true':
            self._install = lambda: ()

    def _install(self):
        options = self.options
        distribution = options.get('egg')
        if distribution is None:
            distribution = options.get('eggs')
            if distribution is None:
                distribution = self.name
            else:
                logger.warn("The eggs option is deprecated. Use egg instead")


        distribution = options.get('egg', options.get('eggs', self.name)
                                   ).strip()

        patch_dict = self._get_patch_dict(options, distribution)
        return zc.buildout.easy_install.build(
            distribution, options['_d'], self.build_ext,
            self.links, self.index, sys.executable,
            [options['_e']], newest=self.newest, patch_dict=patch_dict,
            )


class Develop(Base):

    def __init__(self, buildout, name, options):
        Base.__init__(self, buildout, name, options)
        options['setup'] = os.path.join(buildout['buildout']['directory'],
                                        options['setup'])

    def _install(self):
        options = self.options
        return zc.buildout.easy_install.develop(
            options['setup'], options['_d'], self.build_ext)


def build_ext(buildout, options):
    result = {}
    for be_option in ('include-dirs', 'library-dirs'):
        value = options.get(be_option)
        if value is None:
            continue
        value = [
            os.path.join(
                buildout['buildout']['directory'],
                v.strip()
                )
            for v in value.strip().split('\n')
            if v.strip()
        ]
        result[be_option] = os.pathsep.join(value)
        options[be_option] = os.pathsep.join(value)

    # rpath has special symbolic dirnames which must not be prefixed
    # with the buildout dir.  See:
    # http://man7.org/linux/man-pages/man8/ld.so.8.html
    RPATH_SPECIAL = [
        '$ORIGIN', '$LIB', '$PLATFORM', '${ORIGIN}', '${LIB}', '${PLATFORM}']
    def _prefix_non_special(x):
        x = x.strip()
        for special in RPATH_SPECIAL:
            if x.startswith(special):
                return x
        return os.path.join( buildout['buildout']['directory'], x)

    value = options.get('rpath')
    if value is not None:
        values = [_prefix_non_special(v)
                    for v in value.strip().split('\n') if v.strip()]
        result['rpath'] = os.pathsep.join(values)
        options['rpath'] = os.pathsep.join(values)

    swig = options.get('swig')
    if swig:
        options['swig'] = result['swig'] = os.path.join(
            buildout['buildout']['directory'],
            swig,
            )

    for be_option in ('define', 'undef', 'libraries', 'link-objects',
                      'debug', 'force', 'compiler', 'swig-cpp', 'swig-opts',
                      ):
        value = options.get(be_option)
        if value is None:
            continue
        result[be_option] = value

    return result
