#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os


class EmSDKInstallerConan(ConanFile):
    name = "emsdk_installer"
    version = "2.0.12"
    description = "Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/microblink/conan-emsdk_installer"
    homepage = "https://github.com/kripken/emscripten"
    author = "Bincrafters <bincrafters@gmail.com>, modified by Microblink"
    topics = ("conan", "emsdk", "emscripten", "installer", "sdk")
    license = "MIT"
    exports = ["LICENSE.md"]

    settings = {
        "os_build": ['Windows', 'Linux', 'Macos'],
        "arch_build": ['x86_64', 'macos_fat']
    }
    short_paths = True
    _source_subfolder = "source_subfolder"

    def source(self):
        commit = "master"
        source_url = 'https://github.com/emscripten-core/emsdk/archive/%s.tar.gz' % commit
        tools.get(source_url)
        extracted_folder = "emsdk-%s" % commit
        os.rename(extracted_folder, self._source_subfolder)

    def _run(self, command):
        self.output.info(command)
        self.run(command)

    @staticmethod
    def _touch(filename):
        if not os.path.isfile(filename):
            with open(filename, "w") as f:
                f.write("\n")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def build(self):
        with tools.chdir(self._source_subfolder):
            emsdk = 'emsdk.bat' if os.name == 'nt' else './emsdk'
            if os.path.isfile("python_selector"):
                self._chmod_plus_x("python_selector")
            self._chmod_plus_x('emsdk')
            self._run('%s update' % emsdk)
            if os.path.isfile("python_selector"):
                self._chmod_plus_x("python_selector")
            self._chmod_plus_x('emsdk')

            if not os.path.isdir("zips"):
                os.makedirs("zips")
            self._run('%s list' % emsdk)

            self._run('%s install sdk-%s-64bit' % (emsdk, self.version))
            self._run('%s activate sdk-%s-64bit --embedded' % (emsdk, self.version))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern='*', dst='.', src=self._source_subfolder, symlinks=True)
        emsdk = self.package_folder
        emscripten = os.path.join(emsdk, 'upstream', 'emscripten')
        toolchain = os.path.join(emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')
        # allow to find conan libraries
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)")

    def _define_tool_var(self, name, value):
        suffix = '.bat' if os.name == 'nt' else ''
        path = os.path.join(
            self.package_folder,
            'upstream',
            'emscripten',
            '%s%s' % (value, suffix)
        )
        self._chmod_plus_x(path)
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    @property
    def _host_arch(self):
        if self.settings.arch_build == 'macos_fat':
            return 'x86_64'
        else:
            return self.settings.arch_build

    def package_id(self):
        self.info.settings.arch_build = self._host_arch

    def package_info(self):
        emsdk = self.package_folder
        em_config = os.path.join(emsdk, '.emscripten')
        emscripten = os.path.join(emsdk, 'upstream', 'emscripten')
        em_cache = os.path.join(emsdk, '.emscripten_cache')
        toolchain = os.path.join(emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')

        self.output.info('Appending PATH environment variable: %s' % emsdk)
        self.env_info.PATH.append(emsdk)

        self.output.info('Appending PATH environment variable: %s' % emscripten)
        self.env_info.PATH.append(emscripten)

        self.output.info('Creating EMSDK environment variable: %s' % emsdk)
        self.env_info.EMSDK = emsdk

        self.output.info('Creating EMSCRIPTEN environment variable: %s' % emscripten)
        self.env_info.EMSCRIPTEN = emscripten

        self.output.info('Creating EM_CONFIG environment variable: %s' % em_config)
        self.env_info.EM_CONFIG = em_config

        self.output.info('Creating EM_CACHE environment variable: %s' % em_cache)
        self.env_info.EM_CACHE = em_cache

        self.output.info('Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: %s' % toolchain)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain

        self.env_info.CC = self._define_tool_var('CC', 'emcc')
        self.env_info.CXX = self._define_tool_var('CXX', 'em++')
        self.env_info.RANLIB = self._define_tool_var('RANLIB', 'emranlib')
        self.env_info.AR = self._define_tool_var('AR', 'emar')
