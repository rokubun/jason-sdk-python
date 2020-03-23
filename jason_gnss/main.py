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
    jason process   <rover_file> [ <base_file> ]
    jason submit    <rover_file> [ <base_file>  [ --base_position <x> <y> <z> ] ]
    jason download  <process_id>
    jason status    <process_id>

Options:
    -h --help        shows the help
    -v --version     shows the version
    --api-key        Override the API key from the environment variables
    --secret-token   Override the User secret token from the envirnement variables
    --base_position  Optional base station position (in ECEF XYZ, meters)

Commands:
    process        Submit a file to process and wait for the results (returns the process id)
    submit         Send a file to process, without waiting for the results
    status         Get the status of a process (useful to know if results are ready)
    download       Get the results for a given process ID
"""
import docopt
import pkg_resources
import sys

from . import commands


def main():
    """
    """

    version = pkg_resources.require("jason-gnss")[0].version

    args = docopt.docopt(__doc__, version=version, options_first=True)

    #sys.stderr.write("Start main, parsed arg {}\n".format(args))

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

    return command, command_args


def __get_submit_args__(args):

    command_args = {
        'rover_file' : args.get('<rover_file>', None),
        'base_file' : args.get('<base_file>', None),
    }

    if '--base_position' in args:
        ecef_xyz = [
            args.get('<x>', None),
            args.get('<y>', None),
            args.get('<z>', None)
        ]
        command_args.update({'--base_position' : ecef_xyz})

    return command_args


if __name__ == "__main__":

    return_code = main()
    sys.exit(return_code)

