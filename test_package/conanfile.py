#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "cmake"

    def build(self):
        cmake = CMake(self, generator='Ninja')
        cmake.configure()
        cmake.build()
        #self.run("cmake --build %s --config Release" % self.build_folder)

    def test(self):
        test_file = os.path.join(self.build_folder, "bin", "test_package.js")
        self.run('node %s' % test_file, run_environment=True)
