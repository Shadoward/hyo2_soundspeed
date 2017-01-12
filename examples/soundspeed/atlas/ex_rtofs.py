from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from datetime import datetime as dt, timedelta

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeedmanager.qt_callbacks import QtCallbacks


def main():
    app = QtGui.QApplication([])  # PySide stuff (start)
    mw = QtGui.QMainWindow()
    mw.show()

    lib = SoundSpeedLibrary(qt_progress=QtGui.QProgressDialog)
    lib.set_callbacks(QtCallbacks(mw))

    tests = [
        (43.026480, -70.318824, dt.utcnow()),  # offshore Portsmouth
        (-19.1, 74.16, dt.utcnow()),  # Indian Ocean
        (18.2648113, 16.1761115, dt.utcnow()),  # in land -> middle of Africa
    ]

    # download the current-time rtofs
    if not lib.has_rtofs():
        lib.download_rtofs()
    logger.info("has rtofs: %s" % lib.has_rtofs())

    # test today urls
    temp_url, sal_url = lib.atlases.rtofs._build_check_urls(dt.utcnow())
    logger.info("urls:\n%s [%s]\n%s [%s]"
                % (temp_url, lib.atlases.rtofs._check_url(temp_url), sal_url, lib.atlases.rtofs._check_url(sal_url)))
    # test yesterday urls
    temp_url, sal_url = lib.atlases.rtofs._build_check_urls(dt.utcnow() - timedelta(days=1))
    logger.info("urls:\n%s [%s]\n%s [%s]"
                % (temp_url, lib.atlases.rtofs._check_url(temp_url), sal_url, lib.atlases.rtofs._check_url(sal_url)))

    # test for a few locations
    for test in tests:
        logger.info("rtofs profile:\n%s" % lib.atlases.rtofs.query(lat=test[0], lon=test[1], datestamp=test[2]))

    # test user interaction
    lib.retrieve_rtofs()
    logger.info("lib retrieve rtofs: %s" % lib.ssp)

    app.exec_()  # PySide stuff (end)

if __name__ == "__main__":
    main()