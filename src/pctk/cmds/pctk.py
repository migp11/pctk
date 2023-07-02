import os, sys
import argparse
from pctk import multicellds
from pctk.cmds import plot
from pctk.cmds import render


class UnknownCommand(Exception):
    def __init__(self, message):
        self.message = f"Unknown command {message}. Available options are: {COMMANDS}"
        super().__init__(self.message)



COMMANDS = ("plot-time-course", "write-pov")

def create_main_parser():
    parser = argparse.ArgumentParser(description="PhysiCell Tool Kit for handling and processing Physicell outputs")
    parser.add_argument("command", action="store", help="PCTK command", choices=COMMANDS)
    return parser

def povray_cmd_parser(main_parser):
    povray_link = "http://www.povray.org/download/"

    parser = argparse.ArgumentParser(parents=[main_parser],
                                     description="Render a bunch of PhysiCell output file into povray files ({povray_link})")
    


    parser.add_argument("xml_config", action="store", help="XML configuration file")

    parser.add_argument("--idxs", action="store", dest="strn_idxs", 
                        help="String specifing the indexes of the output files. \
                              The supported options include: \
                              - slices: 1:10:1\
                              - indexes: 1,2,5,10\
                              - all (use glob)", 
                        default="")
    
    parser.add_argument("--format", action="store", dest="format", choices=("physicell", "physiboss"),
                        help="Format of the input data", default="physicell")

    parser.add_argument("--render",  action='store_true',
                        help="Render the .pov files into .png. Requires povray ({povray_link})")

    parser.add_argument("--width", action="store", dest="width", type=int, default=2160, 
                        help="Width for povray rendered image")

    parser.add_argument("--height", action="store", dest="height", type=int, default=2160, 
                        help="Heigh for povray rendered image")

    parser.add_argument("--cpus", action="store", dest="cpus", type=int, default=4, 
                        help="Total CPUs availabile to run in parallel using multiprocessing")

    return parser

def plot_tc_parser(main_parser):
    parser = argparse.ArgumentParser(parents=[main_parser],
        description="Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time")

    parser.add_argument("data_folder", action="store", help="folder were the data is stored")
    
    parser.add_argument("--format", action="store", dest="format", choices=("physicell", "physiboss"),
                        help="Format of the input data", default="physicell")

    parser.add_argument("--figout", action="store", dest="fig_fname", default="./cell_vs_time.png",
                        help="File name to save the plot")
                        
    parser.add_argument("--csvout", action="store", dest="csv_fname", default=None,
                        help="File name to store the summary table used for the plot")

    return parser

def main():
    main_parser = create_main_parser()
    main_args, _ = main_parser.parse_known_args()

    if main_args.command == "plot-time-course":
        parser = plot_tc_parser(main_parser)
        args = parser.parse_args(main_parser)
        plot.plot_time_course(args)
    elif main_args.command == "write-pov":
        main_parser.add_argument("--create-config", action="store", dest="config_fname", default="",
                                 help="Create a defaul config XML file for generating POV files")
        main_args, _ = main_parser.parse_known_args()
        if main_args.config_fname:
            with open(main_args.config_fname, "w") as fh:
                print(f"Writing default POV-write config into {main_args.config_fname}.")
                fh.writelines(render.DEFAULT_XML)
        else:
            parser = povray_cmd_parser()
            args = parser.parse_args()
            render.write_pov_files(args)
    else:
        raise UnknownCommand(main_args.command)