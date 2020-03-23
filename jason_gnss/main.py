#!/usr/bin/env python
"""
Jason PaaS client utility

By default, this client will use the following environment variables for the
authentication
- JASON_API_KEY
- JASON_SECRET_TOKEN

Alternatively, you can override these settings via the command line arguments

Usage:
    jason -h | --help
    jason --version
    jason process   <rover_file> [ <base_file> ] [ --base_position <lat> <lon> <height> ]
    jason submit    <rover_file> [ <base_file> ] [ --base_position <lat> <lon> <height> ]
    jason download  <process_id>
    jason status    <process_id>
    jason convert   <gnss_file>
    jason list_processes

Options:
    -h --help        shows the help
    -v --version     shows the version
    --api-key        Override the API key from the environment variables
    --secret-token   Override the User secret token from the envirnement variables
    --base_position  Optional base station position (in WGS84 format)

Commands:
    process        Submit a file to process and wait for the results (returns the process id)
    submit         Send a file to process, without waiting for the results
    status         Get the status of a process (useful to know if results are ready)
    download       Get the results for a given process ID
    convert        Convert an input file into a RINEX 3.03 format and, if 
                   present in the file, camera/trigger events. If the input
                   file comes from an Argonaut/MEDEA GNSS receiver, also provide
                   with the IMU measurements
    list_processes Get the list of processes issued by the user
"""
import docopt
import pkg_resources
import sys

from . import commands


def main():
    """
    """

    version = pkg_resources.require("jason-gnss")[0].version

    args = docopt.docopt(__doc__, version=version, options_first=False)

    #sys.stderr.write("Start main, parsed arg\n {}\n".format(args))

    command, command_args = __get_command__(args)

    command(**command_args)


    return 0



def __get_command__(args):

    command = None
    command_args = {}

    if args['process']:
        command = commands.process
        command_args = __get_submit_args__(args)
    
    elif args['submit']:
        command = commands.submit
        command_args = __get_submit_args__(args)

    elif args['download']:
        command = commands.download
        command_args = { 'process_id': args.get('<process_id>', None)}

    elif args['status']:
        command = commands.status
        command_args = { 'process_id': args.get('<process_id>', None)}

    elif args['convert']:
        command = commands.process
        command_args = {
            'rover_file' : args.get('<gnss_file>', None),
            'process_type' : "CONVERSION"
        }
    
    elif args['list_processes']:
        command = commands.list_processes

    return command, command_args


def __get_submit_args__(args):

    command_args = {
        'rover_file' : args.get('<rover_file>', None),
        'base_file' : args.get('<base_file>', None),
    }

    if '--base_position' in args:
        lonlathgt = [
            args.get('<lon>', None),
            args.get('<lat>', None),
            args.get('<height>', None)
        ]
        command_args.update({'base_lonlathgt' : lonlathgt})

    return command_args


if __name__ == "__main__":

    return_code = main()
    sys.exit(return_code)

