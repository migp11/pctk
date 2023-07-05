#!/usr/bin/env python3
# coding: utf-8

import os
import glob

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from pctk import multicellds 
from pctk.config import default_cell_colors

    

def pb_output_iterator(output_folder, sep=";"):
    globing = os.path.join(output_folder, "cells_[0-9]*.txt")
    for fname in sorted(glob.glob(globing)):
        df = pd.read_csv(fname, sep=sep)
        t = df.Time[0]
        yield (t, df)

def count_pb_files(output_folder):
    globing = os.path.join(output_folder, "cells_[0-9]*.txt")
    return len(glob.glob(globing))


def get_timeserie_mean(mcds, filter_alive=True):
    time = []
    values = []
    filter_alive = True
    for t, df in mcds.cells_as_frames_iterator():
        time.append(t)
        df = df.iloc[:,3:]
        if filter_alive:
            mask = df['current_phase'] <= 14
            df = df[mask]
        values.append(df.mean(axis=0).values)

    cell_columns = df.columns.tolist()
    df = pd.DataFrame(values, columns=cell_columns)
    df['time'] = time
    return df[['time'] + cell_columns]


def get_timeserie_density(mcds):
    data = []
    for t,m in mcds.microenvironment_as_matrix_iterator():
        data.append((t, m[5,:].sum()))
    df = pd.DataFrame(data=data, columns=['time', 'tnf'])
    return df

def plot_molecular_model(df_cell_variables, list_of_variables, ax1):

    threshold = 0.5

    for label in list_of_variables:
        y = df_cell_variables[label]
        time = df_cell_variables["time"]
        ax1.plot(time, y, label="% X " + label)

    ax1.set_ylabel("% X")
    ax1.yaxis.grid(True)
    ax1.set_xlim((0,time.values[-1]))
    ax1.set_ylim((0,1))
    # ax1.set_xlabel("time (min)")
    
def plot_cells(df_time_course, color_dict, ax, xlabel="Time (min)", ylabel="Nº of cells"):

    # Alive/Apoptotic/Necrotic vs Time
    for pheno,color in color_dict.items():
        ax.plot(df_time_course.time, df_time_course[pheno], "-", c=color, label=pheno)
    
    # setting axes labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # Showing legend
    ax.legend()
    ax.yaxis.grid(True)



def plot_time_course(output_folder, fig_fname="time_course.png", csv_fname="time_course.csv", format="physicell"):
    phases_dict = multicellds.default_phases_dict
    phase_grouping = multicellds.default_phase_grouping
    print(phases_dict)
    # Globing output files according to the output format specified
    if format == 'physicell':
        phase_col = "current_phase"
        mcds = multicellds.MultiCellDS(output_folder=output_folder)
        df_iterator = mcds.cells_as_frames_iterator()
        num_of_files = mcds.cells_file_count()
    elif format == 'physiboss':
        phase_col = "phase"
        df_iterator = pb_output_iterator(output_folder)
        num_of_files = count_pb_files(output_folder)
    
    # Initializing a Pandas Databrafe to store the data
    
    cell_columns = ["time", "alive", "apoptotic", "necrotic"]

    data = np.zeros((num_of_files, 4), dtype=int)
    df_time_course = pd.DataFrame(columns=cell_columns, data=data)

    print("Reading cell_output files from %i input files from %s" % (num_of_files, output_folder))
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
    
        # plot Alive vs Time
    print("Creating figure")
    fig, ax = plt.subplots(1, 1, figsize=(8,3), dpi=300)
    plot_cells(df_time_course, default_cell_colors, ax)

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.grid(linestyle='dotted')
    ax.legend()
    
    # Saving fig
    fig.tight_layout()
    fig.savefig(fig_fname)
    print("Saving fig as %s" % fig_fname)
    
    if csv_fname:
        df_time_course.to_csv(csv_fname, sep="\t")
        print("Saving csv as %s" % csv_fname)




