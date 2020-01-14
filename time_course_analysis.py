#!/usr/bin/env python3
# coding: utf-8

import os, re, glob, json
import argparse

import numpy as np
import pandas as pd
from scipy.io import loadmat

import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="ticks", palette="Paired")
sns.set_context('paper')

def get_params_dir():
    param_folder = os.path.dirname(os.path.realpath(__file__))
    param_folder = os.path.join(param_folder, "params")
    return param_folder

def create_parser():
    parser = argparse.ArgumentParser(description="Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time")
    
    parser.add_argument("data_folder", action="store", help="folder were the data is stored")
    
    parser.add_argument("--format", action="store", dest="format", choices=("mat", "csv"),
                        help="Format of the input data", default="mat")
    
    parser.add_argument("--phase-map", action="store", dest="json_phase_map",
                        help="Path to json file with metabolic functions", default=None)

    parser.add_argument("--figout", action="store", dest="fig_fname", default="./cell_vs_time.png",
                        help="File name to save the plot")
                        
    parser.add_argument("--csvout", action="store", dest="csv_fname", default=None,
                        help="File name to store the summary table used for the plot")

    return parser
    

def create_defaul_phasedict():
    param_folder = get_params_dir()
    phasedict_fname = os.path.join(param_folder, "cell_phases_dict.json")
    phases_dict = {}
    with open(phasedict_fname) as fh:
        phases_dict = json.load(fh)
        phases_dict = {int(k):v for k,v in phases_dict.items()}
    
    return phases_dict


def create_defaul_phasegrouping():
    param_folder = get_params_dir()
    phasedict_fname = os.path.join(param_folder, "phases_grouping_dict.json")
    phase_grouping = {}
    with open(phasedict_fname) as fh:
        phase_grouping = json.load(fh)
    
    return phase_grouping


def get_defaul_columns():
    defaul_columns = [ "ID", "x", "y", "z", "total_volume", "cell_type", 
                       "cycle_model", "current_phase", "elapsed_time_in_phase", 
                       "nuclear_volume", "cytoplasmic_volume", "fluid_fraction", 
                       "calcified_fraction", "orientation_x", "orientation_y", 
                       "orientation_z", "polarity", "migration_speed", 
                       "motility_vector_x", "motility_vector_y", "motility_vector_z", 
                       "migration_bias", "motility_bias_direction_x", "motility_bias_direction_y", 
                       "motility_bias_direction_z", "persistence_time", "motility_reserved"
                      ]
                      
    return defaul_columns


def process_mat(fname, columns=[]):
    
    if len(columns) == 0:
        columns = get_defaul_columns()
    
    stru = loadmat(fname)
    cells = stru['cells'].T
    
    assert cells.shape[1] == len(columns)
    df = pd.DataFrame(cells, columns=columns)
    
    return df


def process_csv(fname, sep=';'):
    df = pd.read_csv(fname, sep=sep)
    return df


def main():
    
    parser = create_parser()
    args = parser.parse_args()
    
    global phases_dict
    global phase_grouping
    
    # Reading a json file which includes a dictionary with the mapping between 
    # PhysiCell/Boss integer codes and the corresponding string the description
    if args.json_phase_map:
        with open(args.json_phase_map) as fh:
            phases_dict = json.load(fh)
            phases_dict = {int(k):v for k,v in phases_dict.items()}
    else:
        phases_dict = create_defaul_phasedict()
    
    # The following dict is used to group cell phases into three general classes:
    # Alive, Apoptotic (programmed cell death), Necrotic (Non-programmed cell death)
    phase_grouping = create_defaul_phasegrouping()
    
    
    # Globing output files according to the output format specified
    if args.format == 'mat':
        globing = os.path.join(args.data_folder,  "output[0-9]*_cells_physicell.mat")
    elif args.format == 'csv':
        globing = os.path.join(args.data_folder, "cells_[0-9]*.txt")
        
    # Just counting the number of files (each one corresponding to a time snapshots)
    num_of_files = len(glob.glob(globing))

    # Initializing a Pandas Databrafe to store the data
    columns = ["Time", "Alive", "Apoptotic", "Necrotic"]
    data = np.zeros((num_of_files, 4), dtype=int)
    df_time_course = pd.DataFrame(columns=columns, data=data)

    print("Reading cell_output files from %i input files from %s" % (num_of_files, args.data_folder))
    # Iterating over all cell_output files
    for i, f in enumerate(sorted(glob.glob(globing))):
        print("\tProcessing file: %s" % f)
        # the filenmae includes the simulation time so we extract the current time
        # from the files name and store it in the created dataframe
        time = int(re.sub('[^0-9]', '', os.path.basename(f)))
        
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
        
        # Rename the phases integer codes using the phases_dict as the mapping
        df.replace(to_replace={phase_col: phases_dict}, value=None, inplace=True)
        
        # Count the number of cells in each phase
        counts = df.groupby(phase_col).ID.count()
        
        df_time_course.iat[i, 0] = time
        # group the previous phases count into the three general classes:
        # Alive, Apoptotic, Necrotic
        for k, v in counts.to_dict().items():
            df_time_course.at[i, phase_grouping[k]] += v
            
    # Set time column as the dataframe index
    df_time_course.set_index("Time", inplace=True)
    

    print("Creating figure")
    # Create a figure
    fig, ax = plt.subplots(1, 1, figsize=(6,4), dpi=150)
    
    # plot Alive vs Time
    ax.plot(df_time_course.index, df_time_course.Alive, "g", label="alive")
    
    # plot Necrotic vs Time
    ax.plot(df_time_course.index, df_time_course.Necrotic, "k", label="necrotic")
    
    # plot Apoptotic vs Time
    ax.plot(df_time_course.index, df_time_course.Apoptotic, "r", label="apoptotic")
    
    # setting axes labels
    ax.set_xlabel("time (min)")
    ax.set_ylabel("Nº of cells")
    
    # Showing legend
    ax.legend()
    ax.grid(True)
    
    sns.despine()
    
    # Saving fig
    fig.tight_layout()
    
    if os.path.isfile(args.fig_fname):
        print("Warning: figure filename %s already exists" % args.fig_fname)
    else:
        fig.savefig(args.fig_fname)
        print("Saving fig as %s" % args.fig_fname)
    
    if args.csv_fname:
        if os.path.isfile(args.csv_fname):
            print("Warning: CSV filename %s already exists" % args.csv_fname)
        else:
            df_time_course.to_csv(args.csv_fname, sep="\t")
            print("Saving csv as %s" % args.csv_fname)

main()

