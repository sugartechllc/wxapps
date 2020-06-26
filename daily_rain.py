import json
import argparse
import glob
import sh
import os
import platform
import sys
from datetime import datetime, timedelta

# Platform characteristics
os_name = os.name
os_arch = platform.uname()[4]

VERBOSE = False

"""
Manage the command line options.
The options are collated in a dictionary keyed on the option long name.
The option dictionary will only contain the options that are present on the command line.
"""
class CommandArgs:
  def __init__(self):
    global VERBOSE

    description = """
Iterate through a collection of CHORDS geojson files from the sugartecllc TPG instrument,
extracting the daily rainfall. Write this to a file, in CSV format.
"""

    epilog = """
The json in each input file is expected to have at least the following elements:

""" + "This operating system is " + os_name + ", the architecture is " + os_arch + "."

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", "--pattern",action="store", default="*.geojson", help="file matching pattern (default '*.geojson')")
    parser.add_argument("-d", "--dir",    action="store", default="./", help="source directory (default './)'")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="verbose output (optional)")

    # Parse the command line. 
    args = parser.parse_args()

    self.options = vars(args)
    self.options['dir'] = os.path.abspath(os.path.expanduser(self.options['dir']))+'/'
    VERBOSE = self.options['verbose']

  def get_options(self):
    """
    Return the dictionary of existing options.
    """
    return self.options

  def get_date(self, s):
    try:
        return datetime.strptime(s,"%Y-%m-%d")
    except ValueError as e:
        print('Error in date "' + s + '", use format YYYY-M-D')
        exit(1)

class OneDay:
  def __init__(self, file_path):
    self.file_path = file_path
    self.n_records = 0
    self.daily_precip = None
    self.first_precip = None
    self.last_precip = None
    self.first_bucket = None
    self.last_bucket = None
    self.begin_time = None
    self.end_time = None
    self.site = None

    if VERBOSE:
      print(self.file_path)

    tpg_data = json.loads(open(file_path).read())
    if not tpg_data['features'][0]['properties']['measurements_in_feature']:
      return

    self.features = tpg_data['features']
    self.properties = self.features[0]['properties']
    data = self.properties['data']
    self.n_records = len(data)
    self.begin_time = data[0]['time']
    self.end_time = data[-1]['time']
    self.first_precip = data[0]['measurements']['precip']
    self.last_precip = data[-1]['measurements']['precip']
    self.daily_precip = self.last_precip - self.first_precip

  def info(self):
    print(self.file_path)
    print(self.daily_precip, self.n_records, self.begin_time, self.end_time)

  def header(self):
    print('File Created,', datetime.now().isoformat(timespec='minutes')+'Z')
    print('DOI,', self.properties['doi'])
    print('Instrument,','Sutron Total Precipitation Gauge (https://www.sutron.com/product/total-precipitation-gauge-tpg)')
    print('Data Infrastructure,', 'CHORDS (http://chordsrt.com)')
    print('Data Collection,', 'https://wx.sugartechllc.com')
    print('Project,', self.properties['project'])
    print('Affiliation,', self.properties['affiliation'])
    print('Site,', self.properties['site'])
    print('Instrument,', self.properties['instrument'])
    print('Longitude (deg),', self.features[0]['geometry']['coordinates'][0])
    print('Latitude (deg),', self.features[0]['geometry']['coordinates'][1])
    print('Elevation (m),', self.features[0]['geometry']['coordinates'][2])

def find_files(dir, pattern):
  files = sorted(glob.glob(dir+pattern))
  return files

#####################################################################
if __name__ == '__main__':
    # Get the command line options
    options = CommandArgs().get_options()

    data_files = find_files(dir=options['dir'], pattern=options['pattern'])

    if not data_files:
      print('No input files which match ' + options['dir']+options['pattern'])
      sys.exit(1)

    first_file = True
    for data_file in data_files:
      one_day = OneDay(file_path=data_file)
      if first_file:
        one_day.header()
        print('Date, Daily Precipitation (in)')
        first_file = False
      if one_day.n_records:
        print(one_day.begin_time+',', '{:5.2f}'.format(one_day.daily_precip))
