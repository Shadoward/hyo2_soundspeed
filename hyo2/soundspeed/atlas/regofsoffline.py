import os
from enum import IntEnum
import logging
from typing import Optional, Union
from netCDF4 import Dataset, num2date

from hyo2.soundspeed.base.geodesy import Geodesy
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.profile.profile import Profile
from hyo2.soundspeed.profile.profilelist import ProfileList
from hyo2.abc.lib.progress.cli_progress import CliProgress


logger = logging.getLogger(__name__)


class RegOfsOffline:

    class Model(IntEnum):
        # East Coast
        CBOFS = 10  # RG = True     # Format is GoMOFS
        DBOFS = 11  # RG = True     # Format is GoMOFS
        GoMOFS = 12  # RG = True     # Format is GoMOFS
        NYOFS = 13  # RG = False
        SJROFS = 14  # RG = False

        # Gulf of Mexico
        NGOFS = 20  # RG = True     # Format is GoMOFS
        TBOFS = 21  # RG = True     # Format is GoMOFS

        # Great Lakes
        LEOFS = 30  # RG = True     # Format is GoMOFS
        LHOFS = 31  # RG = False
        LMOFS = 32  # RG = False
        LOOFS = 33  # RG = False
        LSOFS = 34  # RG = False

        # Pacific Coast
        CREOFS = 40  # RG = True     # Format is GoMOFS
        SFBOFS = 41  # RG = True     # Format is GoMOFS

    # noinspection DuplicatedCode
    regofs_model_descs = \
        {
            Model.CBOFS: "Chesapeake Bay Operational Forecast System",
            Model.DBOFS: "Delaware Bay Operational Forecast System",
            Model.GoMOFS: "Gulf of Maine Operational Forecast System",
            Model.NYOFS: "Port of New York and New Jersey Operational Forecast System",
            Model.SJROFS: "St. John's River Operational Forecast System",
            Model.NGOFS: "Northern Gulf of Mexico Operational Forecast System",
            Model.TBOFS: "Tampa Bay Operational Forecast System",
            Model.LEOFS: "Lake Erie Operational Forecast System",
            Model.LHOFS: "Lake Huron Operational Forecast System",
            Model.LMOFS: "Lake Michigan Operational Forecast System",
            Model.LOOFS: "Lake Ontario Operational Forecast System",
            Model.LSOFS: "Lake Superior Operational Forecast System",
            Model.CREOFS: "Columbia River Estuary Operational Forecast System",
            Model.SFBOFS: "San Francisco Bay Operational Forecast System"
        }

    def __init__(self, data_folder: str, prj: 'hyo2.soundspeed.soundspeed import SoundSpeedLibrary') -> None:
        self.name = self.__class__.__name__
        self.desc = "Abstract atlas"  # a human-readable description
        self.data_folder = data_folder
        self.prj = prj
        self.g = Geodesy()

        self._has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)

        self._file = None
        self._day_idx = 0
        self._zeta = None
        self._siglay = None
        self._h = None
        self._lats = None
        self._lons = None
        self._lat = None
        self._lon = None
        self._loc_idx = None
        self._d = None

    def query(self, nc_path: str, lat: float, lon: float) -> Optional[ProfileList]:
        if not os.path.exists(nc_path):
            raise RuntimeError('Unable to locate %s' % nc_path)
        logger.debug('nc path: %s' % nc_path)

        if (lat is None) or (lon is None):
            logger.error("invalid location query: (%s, %s)" % (lon, lat))
            return None
        logger.debug('query location: %s, %s' % (lat, lon))

        progress = CliProgress()

        try:
            self._file = Dataset(nc_path)
            progress.update(20)

        except (RuntimeError, IOError) as e:
            logger.warning("unable to access data: %s" % e)
            self.clear_data()
            progress.end()
            return None

        try:
            # Now get latitudes, longitudes and depths for x,y,z referencing
            self._lats = self._file.variables['lat'][:]
            self._lons = self._file.variables['lon'][:]
            # logger.debug('lat:(%s)\n%s' % (self._lats.shape, self._lats))
            # logger.debug('lon:(%s)\n%s' % (self._lons.shape, self._lons))

            self._zeta = self._file.variables['zeta'][0, :]
            self._siglay = self._file.variables['siglay'][:]
            self._h = self._file.variables['h'][:]
            logger.debug('zeta:(%s)\n%s' % (self._zeta.shape, self._zeta))
            logger.debug('siglay:(%s)\n%s' % (self._siglay.shape, self._siglay[:, 0]))
            logger.debug('h:(%s)\n%s' % (self._h.shape, self._h))

        except Exception as e:
            logger.error("troubles in variable lookup for lat/long grid and/or depth: %s" % e)
            self.clear_data()
            progress.end()
            return None

        min_dist = 100000.0
        min_idx = None
        for idx, _ in enumerate(self._lats):
            nc_lat = self._lats[idx]
            nc_lon = self._lons[idx]
            if nc_lon > 180.0:
                nc_lon = nc_lon - 360.0
            nc_dist = self.g.distance(nc_lon, nc_lat, lon, lat)
            # logger.debug('loc: %.6f, %.6f -> %.6f' % (nc_lat, nc_lon, nc_dist))
            if nc_dist < min_dist:
                min_dist = nc_dist
                min_idx = idx
        if min_dist >= 10000.0:
            logger.error("location too far from model nodes: %.f" % min_dist)
            self.clear_data()
            progress.end()
            return None

        self._loc_idx = min_idx
        self._lon = self._lons[self._loc_idx]
        if self._lon > 180.0:
            self._lon = self._lon - 360.0
        self._lat = self._lats[self._loc_idx]
        logger.debug('closest node: %d [%s, %s] -> %s' % (self._loc_idx, self._lat, self._lon, min_dist))

        zeta = self._zeta[self._loc_idx]
        h = self._h[self._loc_idx]
        siglay = self._siglay[:, self._loc_idx]
        # logger.debug('zeta: %s, h: %s, siglay: %s' % (zeta, h, siglay))
        self._d = zeta + siglay * (h + zeta)
        logger.debug('d:(%s)\n%s' % (self._h.shape, self._d))

        # Make a new SV object to return our query in
        ssp = Profile()
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        # ssp.meta.probe_type = Dicts.probe_types[self.name]
        ssp.meta.latitude = self._lat
        ssp.meta.longitude = self._lon
        # ssp.meta.utc_time = dt(year=dtstamp.year, month=dtstamp.month, day=dtstamp.day,
        #                        hour=dtstamp.hour, minute=dtstamp.minute, second=dtstamp.second)
        # ssp.meta.original_path = "%s_%s" % (self.name, dtstamp.strftime("%Y%m%d_%H%M%S"))
        ssp.init_data(self._d.shape[0])
        ssp.data.depth = self._d[:]

        profiles = ProfileList()
        profiles.append_profile(ssp)

        progress.end()
        return profiles

    def clear_data(self) -> None:
        """Delete the data and reset the last loaded day"""
        logger.debug("clearing data")
        if self._has_data_loaded:
            if self._file:
                self._file.close()
            self._file = None

        self._has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)