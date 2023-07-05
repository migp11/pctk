import re
import os
import shutil
import argparse
import numpy as np


import multiprocessing as mp
from pctk.povwriter import POVWriter

povray_path = None


def check_povray(exec='povray'):
    global povray_path
    povray_path = shutil.which(exec)
    return (povray_path is not None)

def local_write_pov_file(writer, idx):
    fname = writer.write_pov_file(idx)
    return fname

def render_to_png(pov_fname, width, height, png_fname=None):
    if png_fname is None:
        png_fname = pov_fname[0:-4] + ".png"
    cmd_line = f"{povray_path} +H{height} +W{width} +I{pov_fname} +O{png_fname}"
    exit_flag = os.system(cmd_line)
    if exit_flag != 0:
        print(f"Somthing went wrong running povray {cmd_line}. Command finished with exit flag {exit_flag}")
    return png_fname

def animate_pngs(png_files):
    pass

def write_pov_files(args):
    if args.render:
        assert check_povray()
    
    # Loadgin XML configuration 
    pov_writer = POVWriter(args.config, format=args.format)

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

def main():
    parser = create_parser()
    args = parser.parse_args()
    write_pov_files(args)

if __name__ == '__main__':
    main()
