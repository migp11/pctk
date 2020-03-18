import os
import json
import glob
import pandas as pd
from scipy.io import loadmat    
import xml.etree.ElementTree as ET



class Metadata(object):
    def __init__(self, tree):

        root = tree.getroot()
        metadata_node = root.findall("metadata")[0]

        node = metadata_node.findall("current_time")[0]
        self._current_time = int(float(node.text))
        self._time_units = node.attrib['units']
        
        node = metadata_node.findall("current_runtime")[0]
        self._current_runtime = float(node.text)
        self._runtime_units = node.attrib['units']

        micro_env_node = root.findall("microenvironment")[0]
        node = micro_env_node.findall("domain")[0]
        node = node.findall("mesh")[0]
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

        self._phases_dict = {}
        self._load_defaul_phasedict()

        self._phase_grouping = {}
        self._load_defaul_phasegrouping()

        xml_fname = os.path.join(output_folder, xml_fname)
        self._tree = ET.parse(xml_fname)

        self._metadata = Metadata(self._tree)
        self._cell_columns = self._get_cell_columns()
        self._microenvironment_columns = self._get_microenvironment_columns()


    def _get_time_units(self):
        root = self._tree.getroot()
        node = root.findall("metadata")[0]
        node = node.findall("current_time")[0]
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
        node = root.findall("cellular_information")[0]
        
        node = self._get_cell_info_recursive(node)
        cellular_info_node = node.findall("labels")[0]
        
        cell_columns = []
        for child in cellular_info_node:
            column = child.text
            index = child.attrib["index"]
            size = int(child.attrib["size"])
            if size == 1:
                cell_columns.append(column)
                continue
            for i, v in enumerate(['x', 'y', 'x']):
                cell_columns.append(v + self._separator + column)
                if i == size: 
                    break
                
                
        return cell_columns

    def _get_microenvironment_columns(self):
        root = self._tree.getroot()
        node = root.findall("microenvironment")[0]
        node = node.findall("domain")[0]
        node = node.findall("variables")[0]
        
        columns = []
        for child in node.findall("variable"):
            name = child.attrib['name']
            units = child.attrib['units']
            ID = child.attrib['ID']
            columns.append((name, units, ID))
            
        return columns

    def _load_defaul_phasedict(self):
        phasedict_fname = os.path.join(self._param_folder, "cell_phases_dict.json")
        phases_dict = {}
        with open(phasedict_fname) as fh:
            phases_dict = json.load(fh)
            phases_dict = {int(k):v for k,v in phases_dict.items()}
        
        self._phases_dict = phases_dict

    def _load_defaul_phasegrouping(self):
        phasedict_fname = os.path.join(self._param_folder, "phases_grouping_dict.json")
        phase_grouping = {}
        with open(phasedict_fname) as fh:
            phase_grouping = json.load(fh)
        self._phase_grouping = phase_grouping

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

    def read_matlab_mat(self, fname, column):
        stru = loadmat(fname)
        data = stru[column]
        return data

    def get_time(self, tree):
        root = tree.getroot()
        node = root.findall("metadata")[0]
        node = node.findall("current_time")[0]
        time = int(float(node.text))
        return time

    def cells_file_count(self):
        return len(glob.glob(self._globing))

    def get_cells_fname(self, tree):
        root = tree.getroot()
        node = root.findall("cellular_information")[0]
        node = self._get_cell_info_recursive(node)
        node = node.findall("filename")[0]
        return node.text

    def get_cells_matrix(self, tree):
        matfile = self.get_cells_fname(tree)
        matfile = os.path.join(self._output_folder, matfile)
        data = self.read_matlab_mat(matfile, "cells")
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
        node = root.findall("microenvironment")[0]
        node = node.findall("domain")[0]
        node = node.findall("data")[0]
        node = node.findall("filename")[0]
        return node.text

    def get_microenvironment_matrix(self, tree):
        matfile = self.get_microenvironment_fname(tree)
        matfile = os.path.join(self._output_folder, matfile)
        data = self.read_matlab_mat(matfile, "multiscale_microenvironment")
        return data
        
    def microenvironment_as_matrix_iterator(self):
        xml_list = sorted(glob.glob(self._globing))
        for xml_fname in xml_list:
            tree = ET.parse(xml_fname)
            microenv_matrix = self.get_microenvironment_matrix(tree)
            time = self.get_time(tree)
            yield (time, microenv_matrix)
    

