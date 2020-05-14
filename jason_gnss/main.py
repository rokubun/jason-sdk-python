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
    jason process   <rover_file> [ <base_file> ] [ -p <lat> <lon> <height> ] 
                                 [-l <label>] [--dynamics <dynamic_type>] 
                                 [-s <strategy>] [-d <level>]
    jason submit    <rover_file> [ <base_file> ] [ -p <lat> <lon> <height> ] 
                                 [-l <label>] [--dynamics <dynamic_type>] 
                                 [-s <strategy>] [-d <level>]
    jason download  <process_id> [-d <level>]
    jason status    <process_id> [-d <level>]
    jason convert   <gnss_file> [-d <level>]
    jason list_processes

Options:
    -h --help           shows the help
    -v --version        shows the version
    -d --debug (DEBUG | INFO | WARNING | CRITICAL)
                        Output debug information or more verbose output [default: CRITICAL]
    --api-key           Override the API key from the environment variables
    --secret-token      Override the User secret token from the environment variables
    -l --label <label>  Specify a human readable label to easily identify your process [default: jason-gnss]
    --dynamics (static | dynamic) 
                        Specify the dynamics of the rover receiver [default: dynamic]
    -s --strategy (auto | PPP | PPK | SPP)
                        Select the processing strategy to be applied or let
                        Jason decide the strategy based on the input data. 
                        Strategies can be Precise Point Positioning (PPP, does not
                        require base station), Post-Processing Kinematic (PPK,
                        which requires a base station) or Single Point Positioning
                        (SPP) [default: auto]
    -p --base_position <lat> <lon> <height>  
                        Optional base station position (in WGS84 format)

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

from roktools import logger

from . import commands, AuthenticationError


def main():
    """
    """

    version = pkg_resources.require("jason-gnss")[0].version

    args = docopt.docopt(__doc__, version=version, options_first=False)

    logger.set_level(args['--debug'])

    logger.debug("Start main, parsed arg\n {}".format(args))

    command, command_args = __get_command__(args)

    try:
        command(**command_args)
    except (AuthenticationError,ValueError) as e:
        logger.critical(str(e))

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
    
    if '--label' in args:
        command_args.update({'label' : args['--label']})

    if '--dynamics' in args:
        command_args.update({'rover_dynamics' : args['--dynamics']})

    if '--strategy' in args and args['--strategy'] != "auto":
        command_args.update({'strategy' : args['--strategy']})

    return command_args


if __name__ == "__main__":

    return_code = main()
    sys.exit(return_code)

