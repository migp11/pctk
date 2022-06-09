import os
import json
import glob
import pandas as pd
from scipy.io import loadmat    
import xml.etree.ElementTree as ET

from .config import phases_dict as default_phases_dict
from .config import phase_grouping as default_phase_grouping

__author__ = "Miguel Ponce de Leon"
__copyright__ = "Copyright 2020, PhysiCell ToolKit project"
__credits__ = ["Miguel Ponce de Leon"]
__license__ = "GPL 3.0"
__version__ = "0.1.0"
__maintainer__ = "Miguel Ponce de Leon"
__email__ = "miguel.ponce@bsc.es"
__status__ = "dev"


class Metadata(object):
    def __init__(self, tree):

        root = tree.getroot()
        metadata_node = root.find("metadata")

        node = metadata_node.find("current_time")
        self._current_time = int(float(node.text))
        self._time_units = node.attrib['units']
        
        node = metadata_node.find("current_runtime")
        self._current_runtime = float(node.text)
        self._runtime_units = node.attrib['units']

        micro_env_node = root.find("microenvironment")
        node = micro_env_node.find("domain")
        node = node.find("mesh")
        self._spatial_units = node.attrib['units']
    
    @property
    def current_time(self):
        return self._current_runtime

    @property
    def time_units(self):
        return self._time_units
    
    @property
    def current_runtime(self):
        return self._current_runtime
    
    @property
    def runtime_units(self):
        return self._runtime_units
    
    @property
    def spatial_units(self):
        return self._spatial_units


class MultiCellDS(object):
    
    def __init__(self, output_folder="./", xml_fname="initial.xml", sep="_"):
        
        
        self._param_folder = os.path.join(os.path.dirname(__file__), "params")
        self._globing = os.path.join(output_folder, "output*.xml")
        
        self._separator = sep
        self._output_folder = output_folder

        self._phases_dict = default_phases_dict
        self._phase_grouping = default_phase_grouping

        xml_fname = os.path.join(output_folder, xml_fname)
        self._tree = ET.parse(xml_fname)

        self._metadata = Metadata(self._tree)
        self._cell_columns = self._get_cell_columns()
        self._microenvironment_columns = self._get_microenvironment_columns()


    def _get_time_units(self):
        root = self._tree.getroot()
        node = root.find("metadata")
        node = node.find("current_time")
        units = node.attrib['units']
        return units

    def _get_cell_info_recursive(self, node):

        childs = [i for i in node]
        if len(childs) == 0:
            return None
        for child in childs:
            if child.tag != "simplified_data":
                continue
            if child.attrib["source"] == "PhysiCell":
                return child
    
        return self._get_cell_info_recursive(childs[0])
    
    def _get_cell_columns(self):
        root = self._tree.getroot()
        node = root.find("cellular_information")
        
        node = self._get_cell_info_recursive(node)
        cellular_info_node = node.find("labels")
        
        cell_columns = []
        for child in cellular_info_node:
            column = child.text
            index = child.attrib["index"]
            size = int(child.attrib["size"])
            if size == 1:
                cell_columns.append(column)
                continue
            for i, v in enumerate(['x', 'y', 'z']):
                cell_columns.append(v + self._separator + column)
                if i == size: 
                    break
                
                
        return cell_columns

    def _get_microenvironment_columns(self):
        root = self._tree.getroot()
        node = root.find("microenvironment")
        node = node.find("domain")
        node = node.find("variables")
        
        columns = []
        for child in node.findall("variable"):
            name = child.attrib['name']
            units = child.attrib['units']
            ID = child.attrib['ID']
            columns.append((name, units, ID))
            
        return columns

    @property
    def current_time(self):
        return self._metadata.current_runtime

    @property
    def time_units(self):
        return self._metadata.time_units
    
    @property
    def current_runtime(self):
        return self._metadata.current_runtime
    
    @property
    def runtime_units(self):
        return self._metadata.runtime_units
    
    @property
    def spatial_units(self):
        return self._metadata.spatial_units

    @property
    def cell_columns(self):
        return self._cell_columns

    @property
    def microenvironment_columns(self):
        return self._microenvironment_columns

    @property
    def phases_dict(self):
        return self._phases_dict

    @property
    def phase_grouping(self):
        return self._phase_grouping

    def _read_matlab_mat(self, fname, column):
        stru = loadmat(fname)
        data = stru[column]
        return data

    def get_time(self, tree):
        root = tree.getroot()
        node = root.find("metadata")
        node = node.find("current_time")
        time = int(float(node.text))
        return time

    def cells_file_count(self):
        return len(glob.glob(self._globing))

    def get_cells_fname(self, tree):
        root = tree.getroot()
        node = root.find("cellular_information")
        node = self._get_cell_info_recursive(node)
        node = node.find("filename")
        return node.text

    def get_cells_matrix(self, tree):
        matfile = self.get_cells_fname(tree)
        matfile = os.path.join(self._output_folder, matfile)
        data = self._read_matlab_mat(matfile, "cells")
        return data.T

    def cells_as_matrix_iterator(self):
        xml_list = sorted(glob.glob(self._globing))
        for xml_fname in xml_list:
            tree = ET.parse(xml_fname)
            cell_matrix = self.get_cells_matrix(tree)
            
            time = self.get_time(tree)
            yield (time, cell_matrix)

    def cells_as_frames_iterator(self):
        xml_list = sorted(glob.glob(self._globing))
        for xml_fname in xml_list:
            tree = ET.parse(xml_fname)
            cell_matrix = self.get_cells_matrix(tree)
            
            df = pd.DataFrame(cell_matrix, columns=self._cell_columns)
            df = df.set_index("ID")
        
            time = self.get_time(tree)
            yield (time, df)
  
    def get_microenvironment_fname(self, tree):
        root = tree.getroot()
        node = root.find("microenvironment")
        node = node.find("domain")
        node = node.find("data")
        node = node.find("filename")
        return node.text

    def get_microenvironment_matrix(self, tree):
        matfile = self.get_microenvironment_fname(tree)
        matfile = os.path.join(self._output_folder, matfile)
        data = self._read_matlab_mat(matfile, "multiscale_microenvironment")
        return data
        
    def microenvironment_as_matrix_iterator(self):
        xml_list = sorted(glob.glob(self._globing))
        for xml_fname in xml_list:
            tree = ET.parse(xml_fname)
            microenv_matrix = self.get_microenvironment_matrix(tree)
            time = self.get_time(tree)
            yield (time, microenv_matrix)

    def get_cells_summary_frame(self, phase_col="current_phase"):

        cell_phases = list(set(self.phase_grouping.values()))
        num_of_files = self.cells_file_count()

        # Initializing a Pandas Databrafe to store the data
        index = range(num_of_files)
        columns = ["time"] + cell_phases
        df_time_course = pd.DataFrame(columns=columns, dtype=int, index=index, data=0)
        
        for i, (time, df) in enumerate(self.cells_as_frames_iterator()):
            df_time_course.iloc[i, 0] = time

            # Rename the phases integer codes using the phases_dict as the mapping
            s = df[phase_col]
            s.replace(to_replace=self.phases_dict, inplace=True)

            # Count the number of cells in each phase
            counts = s.value_counts()

            # group the previous phases count into the three general classes:
            # Alive, Apoptotic, Necrotic
            for k, v in counts.to_dict().items():
                if k not in self.phase_grouping:
                    continue
                df_time_course.loc[i, self.phase_grouping[k]] += v
        
        return df_time_course


    def plot_cells(self):
        color_dict = {"alive": "g", "apoptotic": "r", "necrotic":"k"}

        fig, ax = plt.subplots(1, 1, figsize=(6,4), dpi=150)
        # Alive/Apoptotic/Necrotic vs Time
        for k in columns:
            ax.plot(df_time_course.Time, df_time_course[k], "-", c=color_dict[k], label=k)
        # setting axes labels
        ax.set_xlabel("time (min)")
        ax.set_ylabel("Nº of cells")
        # Showing legend
        ax.legend()
        ax.yaxis.grid(True)
        fig.tight_layout()
        # Saving fig
        if save:
            fig.savefig(output_folder + 'cell_vs_time.png')
