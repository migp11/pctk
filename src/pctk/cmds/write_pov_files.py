import re
import os
import shutil
import argparse
import numpy as np


import multiprocessing as mp
from pctk.povwriter import POVWriter

def create_parser():

    povray_link = "http://www.povray.org/download/"

    parser = argparse.ArgumentParser(description="Render a bunch of PhysiCell output file into povray files")
    
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

    parser.add_argument("--create-config", dest="create_default_config", default=False,
                        help="Output format")

    return parser


def check_povray(exec='povray'):
    global povray_path
    povray_path = shutil.which(exec)
    return (povray_path is not None)


def local_write_pov_file(writer, idx):
    fname = writer.write_pov_file(idx)
    return fname

def render_to_png(pov_fname, width, height):
    cmd_line = f"{povray_path} -h{height} -w{width} -a {pov_fname}"
    exit_flag = os.system(cmd_line)
    if exit_flag != 0:
        print(f"Somthing went wrong running povray {cmd_line}. Command finished with exit flag {exit_flag}")

    png_fname = pov_fname[0:-4] + ".png"
    return png_fname

def animate_pngs(png_files):
    pass


povray_path = None


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.render:
        assert check_povray()
    
    # Loadgin XML configuration 
    pov_writer = POVWriter(args.xml_config, format=args.format)

    num_of_jobs = args.cpus

    index_list = []    
    pattern_slices = re.compile("(\d*):(\d*):(\d*)")
    pattern_indexes = re.compile("(\d+)(,\d+)*")
    pattern_all = re.compile("^all$")
    
    match = re.search(pattern_slices, args.strn_idxs)
    if match:
        from_idx = int(match.group(1))
        to_idx = int(match.group(2))
        inc = int(match.group(3))
        index_list = list(range(from_idx, to_idx, inc))
    elif re.search(pattern_indexes, args.strn_idxs):
        index_list = [int(i) for i in args.strn_idxs.split(",")]
    elif re.search(pattern_all, args.strn_idxs):
        pass
    else:
        index_list = [pov_writer.options.time_index]
    
    print(f"Start processing  {num_of_jobs} cpus")
    if num_of_jobs > 1:

        pool = mp.Pool(num_of_jobs)
        pov_files = [pool.apply(local_write_pov_file, args=((pov_writer,idx)))
                                        for idx in index_list]
        pool.close()

        print("Finished!")
        if args.render:
            png_files = []
            for fname in pov_files:
                png = render_to_png(fname, args.width, args.height)
                png_files.append(png)
            
            pool.close()
            #animate_pngs(png_files)
        
    else:
        for idx in index_list:
            pov_writer.write_pov_file(idx)


if __name__ == '__main__':
    main()