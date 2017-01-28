from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeed.base.callbacks.test_callbacks import TestCallbacks
from hydroffice.soundspeed.base import testing


class TestSoundSpeedFormats(unittest.TestCase):

    def setUp(self):
        self.formats = ["caris", "csv", "elac", "hypack", "ixblue", "asvp", "qps", "sonardyne", "unb", ]
        self.data_output = testing.output_data_folder()

    def tearDown(self):
        pass

    def test_read_store_and_write_asvp(self):
        filters = ["asvp", ]
        self._run(filters=filters)

    def test_read_store_and_write_castaway(self):
        filters = ["castaway", ]
        self._run(filters=filters)

    def test_read_store_and_write_digibarpro(self):
        filters = ["digibarpro", ]
        self._run(filters=filters)

    def test_read_store_and_write_digibars(self):
        filters = ["digibars", ]
        self._run(filters=filters)

    def test_read_store_and_write_elac(self):
        filters = ["elac", ]
        self._run(filters=filters)

    def test_read_store_and_write_idronaut(self):
        filters = ["idronaut", ]
        self._run(filters=filters)

    def test_read_store_and_write_iss(self):
        filters = ["iss", ]
        self._run(filters=filters)

    def test_read_store_and_write_mvp(self):
        filters = ["mvp", ]
        self._run(filters=filters)

    def test_read_store_and_write_saiv(self):
        filters = ["saiv", ]
        self._run(filters=filters)

    def test_read_store_and_write_seabird(self):
        filters = ["seabird", ]
        self._run(filters=filters)

    def test_read_store_and_write_sippican(self):
        filters = ["sippican", ]
        self._run(filters=filters)

    def test_read_store_and_write_sonardyne(self):
        filters = ["sonardyne", ]
        self._run(filters=filters)

    def test_read_store_and_write_turo(self):
        filters = ["turo", ]
        self._run(filters=filters)

    def test_read_store_and_write_unb(self):
        filters = ["unb", ]
        self._run(filters=filters)

    def test_read_store_and_write_valeport(self):
        filters = ["valeport", ]
        self._run(filters=filters)

    def _run(self, filters):
        # create a project with test-callbacks
        lib = SoundSpeedLibrary(callbacks=TestCallbacks())

        # set the current project name
        lib.setup.current_project = 'test_read_store_and_write'

        tests = testing.input_dict_test_files(inclusive_filters=filters)

        for idx, testfile in enumerate(tests.keys()):

            logger.info("test: * New profile: #%03d *" % idx)

            lib.import_data(data_path=testfile, data_format=tests[testfile].name)

            lib.store_data()

            lib.export_data(data_path=self.data_output, data_formats=self.formats)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedFormats))
    return s