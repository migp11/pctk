#!/usr/bin/env python3
# coding: utf-8

import os
import shutil
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

def render_to_png(pov_fname, width=1024, height=1024, png_fname=None):
    if png_fname is None:
        png_fname = pov_fname[0:-4] + ".png"
    cmd_line = f"{povray_path} +H{height} +W{width} +I{pov_fname} +O{png_fname} -d"
    exit_flag = os.system(cmd_line)
    if exit_flag != 0:
        print(f"Somthing went wrong running povray {cmd_line}. Command finished with exit flag {exit_flag}")
    return png_fname

def animate_pngs(png_files):
    pass

def write_pov_files(pov_config, index_list=[], format='physicell', 
                    width=1024, height=1024, render=False, num_of_threads=None):
    
    if render:
        assert check_povray()

    if num_of_threads is None:
        num_of_threads = os.cpu_count()
    
    # Loadgin XML configuration 
    pov_writer = POVWriter(pov_config, format=format)

    if len(index_list) == 0:
        index_list = [pov_writer.options.time_index]
    
    print(f"Start processing  {num_of_threads} cpus")
    if num_of_threads > 1:

        pool = mp.Pool(num_of_threads)
        pov_files = [pool.apply(local_write_pov_file, args=((pov_writer,idx)))
                                        for idx in index_list]
        pool.close()
        print("Finished!")
        if render:
            png_files = []
            for pov_fname in pov_files:
                png = render_to_png(pov_fname, width=width, height=height)
                png_files.append(png)
            
            pool.close()
    else:
        for idx in index_list:
            pov_fname = pov_writer.write_pov_file(idx)

            if render:
                png_files = []
                for pov_fname in pov_files:
                    png = render_to_png(pov_fname, width=width, height=height)
                    png_files.append(png)
                
