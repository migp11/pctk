#!/usr/bin/env python3
# coding: utf-8

import os, re, sys
import glob, json
import argparse

import numpy as np
import pandas as pd
from scipy.io import loadmat

import matplotlib.pyplot as plt
import seaborn as sns


modules_path = os.path.dirname(os.path.realpath(__file__))
modules_path= os.path.join(modules_path, 'modules')
sys.path.append(modules_path)

import multicellds


sns.set(style="ticks", palette="Paired")
sns.set_context('paper')

def read_csv():
    # reading a cell_output file (plain text ; separated columns)
    # any function can be used here, using pandas is just a shorcut
    if args.format == 'mat':
        df = process_mat(f)
        phase_col = "current_phase"
        # This should be changed regardin time stamp in MultiCellDS
        time *= 60 
    elif args.format == 'csv':
        df = process_csv(f, sep=";")
        phase_col = "phase"

def create_parser():
    parser = argparse.ArgumentParser(description="Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time")
    
    parser.add_argument("data_folder", action="store", help="folder were the data is stored")
    
    parser.add_argument("--format", action="store", dest="format", choices=("mat", "csv"),
                        help="Format of the input data", default="mat")

    parser.add_argument("--figout", action="store", dest="fig_fname", default="./cell_vs_time.png",
                        help="File name to save the plot")
                        
    parser.add_argument("--csvout", action="store", dest="csv_fname", default=None,
                        help="File name to store the summary table used for the plot")

    return parser
    
def main():
    
    
    parser = create_parser()
    args = parser.parse_args()
    
    mcds = multicellds.MultiCellDS(output_folder=args.data_folder)
    
    # PhysiCell/Boss integer codes and the corresponding string the description
    phases_dict = mcds.phases_dict
    
    # The following dict is used to group cell phases into three general classes:
    # Alive, Apoptotic (programmed cell death), Necrotic (Non-programmed cell death)
    phase_grouping = mcds.phase_grouping
    
    
    # Globing output files according to the output format specified
    if args.format == 'mat':
        globing = os.path.join(args.data_folder,  "output[0-9]*_cells_physicell.mat")
    elif args.format == 'csv':
        globing = os.path.join(args.data_folder, "cells_[0-9]*.txt")
        
    # Just counting the number of files (each one corresponding to a time snapshots)
    num_of_files = mcds.cells_file_count()

    # Initializing a Pandas Databrafe to store the data
    columns = ["Time", "Alive", "Apoptotic", "Necrotic"]
    data = np.zeros((num_of_files, 4), dtype=int)
    df_time_course = pd.DataFrame(columns=columns, data=data)

    print("Reading cell_output files from %i input files from %s" % (num_of_files, args.data_folder))
    # Iterating over all cell_output files
    
    phase_col = "current_phase"
    print(mcds.cell_columns)

    for i, (t, df) in enumerate(mcds.cells_as_frames_iterator()):
        print("\tProcessing time step: %.0f" % t)

        time = int(np.ceil(t))

        # Rename the phases integer codes using the phases_dict as the mapping
        s = df[phase_col]
        s.replace(to_replace=mcds.phases_dict, value=None, inplace=True)
        
        # Count the number of cells in each phase
        counts = s.value_counts()
    
        df_time_course.iat[i, 0] = time
        # group the previous phases count into the three general classes:
        # Alive, Apoptotic, Necrotic
        for k, v in counts.to_dict().items():
            if k not in mcds.phase_grouping:
                continue
            df_time_course.loc[i, mcds.phase_grouping[k]] += v
            
    # Set time column as the dataframe index
    df_time_course.set_index("Time", inplace=True)
    

    print("Creating figure")
    # Create a figure
    fig, ax = plt.subplots(1, 1, figsize=(6,4), dpi=150)
    
    # plot Alive vs Time
    ax.plot(df_time_course.index, df_time_course.Alive, "-", c="g", label="alive")
    
    # plot Necrotic vs Time
    ax.plot(df_time_course.index, df_time_course.Necrotic, "-", c="k", label="necrotic")
    
    # plot Apoptotic vs Time
    ax.plot(df_time_course.index, df_time_course.Apoptotic, "-", c="r", label="apoptotic")
    
    # setting axes labels
    ax.set_xlabel("time (min)")
    ax.set_ylabel("Nº of cells")
    
    # Showing legend
    ax.legend()
    ax.grid(True)
    
    sns.despine()
    
    # Saving fig
    fig.tight_layout()
    
    fig.savefig(args.fig_fname)
    print("Saving fig as %s" % args.fig_fname)
    
    if args.csv_fname:
        df_time_course.to_csv(args.csv_fname, sep="\t")
        print("Saving csv as %s" % args.csv_fname)

main()

