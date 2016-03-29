from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractTextReader
from ...profile.dicts import Dicts


class DigibarPro(AbstractTextReader):
    """Digibar Pro reader -> SVP style

    Info: http://www.odomhydrographic.com/product/digibar-pro/
    """

    def __init__(self):
        super(DigibarPro, self).__init__()
        self._ext.add('txt')

        self.tk_cast_time = "DATE:"
        self.tk_field_header = "DEPTH (M)"

    def read(self, data_path):
        logger.debug('*** %s ***: start' % self.driver)

        self.init_data()  # create a new empty profile

        # initialize probe/sensor type
        self.ssp.meta.sensor_type = Dicts.sensor_types['SVP']
        self.ssp.meta.probe_type = Dicts.probe_types['SVP']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """"Parsing header: time"""
        logger.debug('parsing header')

        # control flags
        has_field_header = False

        for line in self.lines:

            if not line:  # skip empty lines
                continue

            if line[:len(self.tk_field_header)] == self.tk_field_header:
                self.samples_offset += 1
                logger.debug("samples offset: %s" % self.samples_offset)
                has_field_header = True
                break

            elif line[:len(self.tk_cast_time)] == self.tk_cast_time:
                try:
                    fields = line.split(" ")
                    if len(fields) == 2:
                        date_fields = fields[0].split(':')

                        if len(date_fields) == 2:
                            # we are assuming that the cast time is after 2000
                            year = 2000 + int(date_fields[-1][:2])
                            yr_day = int(date_fields[-1][2:])
                            self.ssp.meta.utc_time = dt.datetime(year=year, month=1, day=1) + dt.timedelta(yr_day - 1)
                            # print(self.dg_time)
                        time_fields = fields[1].split(':')

                        if len(time_fields) == 2:
                            hour = int(time_fields[-1][:2])
                            minute = int(time_fields[-1][2:4])
                            self.ssp.meta.utc_time += dt.timedelta(days=0, seconds=0, microseconds=0,
                                                                   milliseconds=0, minutes=minute, hours=hour)

                except ValueError:
                    logger.warning("unable to parse cast date and time at line #%s" % self.samples_offset)

            self.samples_offset += 1

        # sample fields checks
        if not has_field_header:
            raise RuntimeError("Missing field header: %s" % self.tk_field_header)
        if not self.ssp.meta.original_path:
            self.ssp.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.init_data(len(self.lines) - self.samples_offset)

    def _parse_body(self):
        """Parsing samples: depth, speed, temp"""
        logger.debug('parsing body')

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if not line:
                continue

            # first required data fields
            try:
                depth, speed, temp = line.split()

                if speed == 0.0:
                    logger.info("skipping 0-speed row #%s" % (self.lines_offset + count))
                    count += 1
                    continue

                self.ssp.data.depth[count] = depth
                self.ssp.data.speed[count] = speed
                self.ssp.data.temp[count] = temp

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.resize(count)
