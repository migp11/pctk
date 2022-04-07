import os
import glob
import json
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import sklearn as skl

import xml.etree.ElementTree as ET


__author__ = "Miguel Ponce de Leon"
__copyright__ = "Copyright 2020, Tools for PhysiCell project"
__credits__ = ["Miguel Ponce de Leon"]
__license__ = "GPL 3.0"
__version__ = "0.1.0"
__maintainer__ = "Miguel Ponce de Leon"
__email__ = "miguel.ponce@bsc.es"
__status__ = "dev"


def get_parameters_dict(root, param_names):
    
    params_dict = {}
    for p in param_names: 
        xpath = "./{}".format(p.replace(".", "/"))
        pname = p.split(".")[-1]
        el = root.find(xpath)
        value = float(el.text)
        params_dict[pname] = value
    
    return params_dict




def main():
    project_root = "./"
    
    output_folder = os.path.join(project_root, "experiments/spheroid_TNF_v2_sweep_n15")

    ga_params_fname = os.path.join(project_root, "ga_params.json")

    param_names = []
    with open(ga_params_fname) as fh:
        ga_params = json.load(fh)
        param_names = list(ga_params.keys())
    
    time_course_fname = "time_course.tsv"
    settings_fname = "settings.xml"

    globbing = os.path.join(output_folder, "instance_*/")
    instances_folder = glob.glob(globbing)
    total_simulations = len(instances_folder)


    input_params = "spheroid_TNF_v2_sweep_params_n15.txt"
    input_params = os.path.join(output_folder, input_params)
    with open(input_params) as fh:
        line = next(fh).rstrip()
        param_names = list(json.loads(line).keys())

    print("Analyzying %i simulations instances", total_simulations)
    print("List of explored parameters:")
    for p in param_names:
        print("- %s" % p)

main()