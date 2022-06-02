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

from pctk import multicellds 


sns.set(style="ticks", palette="Paired")
sns.set_context('paper')


def create_parser():
    parser = argparse.ArgumentParser(description="Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time")
    
    parser.add_argument("data_folder", action="store", help="folder were the data is stored")
    
    parser.add_argument("--format", action="store", dest="format", choices=("physicell", "physiboss"),
                        help="Format of the input data", default="physicell")

    parser.add_argument("--figout", action="store", dest="fig_fname", default="./cell_vs_time.png",
                        help="File name to save the plot")
                        
    parser.add_argument("--csvout", action="store", dest="csv_fname", default=None,
                        help="File name to store the summary table used for the plot")

    return parser
    

def pb_output_iterator(data_folder, sep=";"):
    globing = os.path.join(data_folder, "cells_[0-9]*.txt")
    for fname in sorted(glob.glob(globing)):
        df = pd.read_csv(fname, sep=sep)
        t = df.Time[0]
        yield (t, df)

def count_pb_files(data_folder):
    globing = os.path.join(data_folder, "cells_[0-9]*.txt")
    return len(glob.glob(globing))

def main():
   
    parser = create_parser()
    args = parser.parse_args()
    
    phases_dict = multicellds.default_phases_dict
    phase_grouping = multicellds.default_phase_grouping
    print(phases_dict)
    # Globing output files according to the output format specified
    if args.format == 'physicell':
        phase_col = "current_phase"
        mcds = multicellds.MultiCellDS(output_folder=args.data_folder)
        df_iterator = mcds.cells_as_frames_iterator()
        num_of_files = mcds.cells_file_count()
    elif args.format == 'physiboss':
        phase_col = "phase"
        df_iterator = pb_output_iterator(args.data_folder)
        num_of_files = count_pb_files(args.data_folder)
    
    # Initializing a Pandas Databrafe to store the data
    columns = ["time", "live", "apoptotic", "necrotic"]
    data = np.zeros((num_of_files, 4), dtype=int)
    df_time_course = pd.DataFrame(columns=columns, data=data)

    print("Reading cell_output files from %i input files from %s" % (num_of_files, args.data_folder))
    # Iterating over all cell_output files
    for i, (t, df) in enumerate(df_iterator):
        print("\tProcessing time step: %.0f" % t)

        # Rename the phases integer codes using the phases_dict as the mapping
        s = df[phase_col]
        s.replace(to_replace=phases_dict, inplace=True)
        
        # Count the number of cells in each phase
        counts = s.value_counts()
    
        df_time_course.loc[i, 'time'] = t
        # group the previous phases count into the three general classes:
        # Alive, Apoptotic, Necrotic
        for k, v in counts.to_dict().items():
            if k not in phase_grouping:
                continue
            df_time_course.loc[i, phase_grouping[k]] += v
            
    
    print("Finish processing files")    
    # Set time column as the dataframe index
    sns.set_context('paper')
    patch_color = "lightgrey"
    
    print("Creating figure")
    # Create a figure
    fig, ax = plt.subplots(1, 1, figsize=(8,3), dpi=300)
    
    # plot Alive vs Time
    curve_params = {}
    curve_params['live'] = {'color': '#75db75', 'label': 'Alive'}
    curve_params['apoptotic'] = {'color': '#ef4242', 'label': 'Apoptotic'}
    curve_params['necrotic'] = {'color':'#97723d', 'label': 'Necrotic'}
    line_width = 2.
    for k,pdict in curve_params.items():
        c = pdict['color']
        l = pdict['label']
        ax.plot(df_time_course.time, df_time_course[k], "-", c=c, label=l, linewidth=line_width)
    
    # setting axes labels
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Nº of cells")

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    
    # Showing legend
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.grid(linestyle='dotted')
    ax.legend()
    
    # Saving fig
    fig.tight_layout()
    fig.savefig(args.fig_fname)
    print("Saving fig as %s" % args.fig_fname)
    
    if args.csv_fname:
        df_time_course.to_csv(args.csv_fname, sep="\t")
        print("Saving csv as %s" % args.csv_fname)


if __name__ == '__main__':
    main()

