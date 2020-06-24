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

"""
Manage the command line options.
The options are collated in a dictionary keyed on the option long name.
The option dictionary will only contain the options that are present on the command line.
"""
class CommandArgs:
    def __init__(self):
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

def find_files(dir, pattern):
  files = glob.glob(dir+pattern)
  return files

#####################################################################
if __name__ == '__main__':
    # Get the command line options
    options = CommandArgs().get_options()

    data_files = find_files(dir=options['dir'], pattern=options['pattern'])

    if not data_files:
      print('No input files which match ' + options['dir']+options['pattern'])
      sys.exit(1)

    print(data_files)
