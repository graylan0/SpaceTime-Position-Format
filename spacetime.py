import struct
import datetime
from geopy.distance import great_circle
from geopy import Point
from pytz import timezone
import pyproj
from math import sqrt


def gps_to_xyz(latitude, longitude, altitude, time):
    """
    Converts GPS coordinates (latitude, longitude, altitude) and time to Cartesian coordinates (x, y, z, t)
    """
    transformer = pyproj.transformer.Transformer.from_crs('EPSG:4326', 'EPSG:4978')  # define transformation from WGS84 to ECEF
    x, y, z = transformer.transform(longitude, latitude, altitude)
    est_time = time.astimezone(timezone('US/Eastern'))
    t = (est_time.year, est_time.month, est_time.day, est_time.hour * 3600 + est_time.minute * 60 + est_time.second)
    t_seconds = t[3] + (t[2] - 1) * 86400 + sum([((month - 1) * 30 + (month - 1) // 2) * 86400 for month in range(1, t[1])]) + (t[0] - 1970) * 31536000
    return x, y, z, t_seconds


def to_stpf(position, time):
    """
    Converts a position and time value to STPF format
    """
    x, y, z, t = position
    timestamp = int(t * 10**6)  # convert time to microseconds since epoch
    stpf = struct.pack('!dddq', x, y, z, timestamp)  # pack position and time into STPF format
    return stpf


# Example usage
while True:
    latitude = float(input('Enter latitude in decimal degrees: '))
    longitude = float(input('Enter longitude in decimal degrees: '))
    altitude = float(input('Enter altitude in meters: '))
    utc_time = datetime.datetime.utcnow()  # Current UTC time
    position = gps_to_xyz(latitude, longitude, altitude, utc_time)  # Convert GPS coordinates and time to Cartesian coordinates
    c = 299792458.0  # speed of light in m/s
    v = 0.5 * c  # velocity relative to Earth in m/s
    x, y, z, t = position
    t_prime = (t - (v * x)/(c**2))/sqrt(1 - (v**2/c**2))
    position_prime = (x, y, z, t_prime)
    stpf = to_stpf(position_prime, utc_time)
    print(stpf.hex())  # Print STPF value as hexadecimal string
