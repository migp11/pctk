#!/usr/bin/env python3
# coding: utf-8
import os
import numpy as np
from math import pi, sin, cos

import xml.etree.ElementTree as ET

from pctk.config import phase_grouping 
from pctk.config import phases_dict
from pctk.config import default_pov_colors



__author__ = "Miguel Ponce de Leon"
__copyright__ = "Copyright 2020, PhysiCell ToolsKit project"
__credits__ = ["Miguel Ponce de Leon"]
__license__ = "GPL 3.0"
__version__ = "0.1.0"
__maintainer__ = "Miguel Ponce de Leon"
__email__ = "miguel.ponce@bsc.es"
__status__ = "dev"


class InvalidFormatException(Exception):
    def __init__(self, format):
        self.format = format
        self.message = f"Invalid format {format}. Format must be physicell or physiboss"
        super().__init__(self.message)


class Clipping_Plane:

    def __init__(self):

        self.coefficients = np.zeros(3)

        self.normal = np.array([0,-1,0])
        self.point_on_plane = np.zeros(3)
        self.coefficients = np.zeros(4)
        
        for i in range(3):
            self.coefficients[i] = self.normal[i]
        for i in range(3):
            self.coefficients[3] -= ( self.normal[i]*self.point_on_plane[i] )

    def coefficients_to_normal_point(self):
        for i in range(3):
            self.normal[i] = self.coefficients[i]
	
        self.normal = self.normal / np.sqrt(np.sum(self.normal**2))
        self.point_on_plane = self.normal
        self.point_on_plane *= -1.0
        self.point_on_plane *= self.coefficients[3]

    def signed_distance_to_plane(self, point):
        assert len(point) == 3
        out = self.coefficients[3]
        for i in range(3):
            out += point[i] * self.coefficients[i]
        return out


class PC_Options:
    def __init__(self, folder="sample", filebase="output", format="physicell",
                 time_index=0, camera_distance=1500, nuclear_offset=0.1, cell_bound=750, 
                 threads=1, use_standard_colors=True):

        self.folder = folder
        self.filebase = filebase
        self.format = format
        self.time_index = time_index
        self.filename = self.create_file_name(time_index)
        
        self.nuclear_offset = nuclear_offset
        self.cell_bound = cell_bound
        self.threads = threads
        self.use_standard_colors = use_standard_colors

        self.columns_index_dict = {}
        if self.format == 'physicell':
            self.columns_index_dict = { "cyto_volume": 4, "cell_type": 5, "phase": 7, "nuc_volume": 9}
        elif self.format == 'physiboss':
            self.columns_index_dict = { "cyto_radius": 4, "cell_type": 11, "phase": 13, "nuc_radius": 6}
        else:
            raise InvalidFormatException(self.format)

    def create_file_name(self, index):
        if self.format == 'physicell':
            fname  = "{base_name}{:08}_cells_physicell.mat".format(index, base_name=self.filebase)
        elif self.format == 'physiboss':
            fname  = "cells_{:05}.txt".format(index)
        else:
            fname = None
        fname = os.path.join(self.folder, fname)
        return fname


class POV_Options():
    
    def __init__(self, x_size=2000, y_size=2000, z_size=2000):
        
        self.max_trace_level = 1
        self.assumed_gamma = 1.0
    
        self.domain_center = np.array([0,0,0])
        self.domain_size = np.array([x_size, y_size, z_size])
        
        self.background = np.array([1,1,1])

        self.camera_theta = 5*pi/4.0
        self.camera_phi = pi/3.0
        self.camera_distance = ( self.domain_size[0] + self.domain_size[1] + self.domain_size[2] ) * 1.25 / 3.0
        self.camera_position = np.array([0,0,0])
        self.set_camera_from_spherical_location()
        
        self.camera_look_at = self.domain_center.copy()
        self.camera_right = np.array([-1,0,0]) # computer graphics are goofy. switch to usual coordinate system
        self.camera_up = np.array([0,0,1])
        self.camera_sky = np.array([0,0,1])
        
        self.light_position = np.array([0,0,0])
    
        self.light_position[0] = self.domain_center[0] - 0.5 * self.domain_size[0]; 
        self.light_position[1] = self.domain_center[1] - 0.5 * self.domain_size[1]; 
        self.light_position[2] = self.domain_center[2] + 1.5 * self.domain_size[2]; 
    
        self.light_rgb = 0.75; 
        self.light_fade_distance = np.linalg.norm( self.domain_size ); 
        self.light_fade_power = 2; 
        
        self.no_shadow = False
        self.no_reflection = False
        
        self.clipping_planes = []
        
    def set_camera_from_spherical_location(self):
        self.camera_position[0] = self.domain_center[0] + self.camera_distance * cos(self.camera_theta)*sin(self.camera_phi) 
        self.camera_position[1] = self.domain_center[1] + self.camera_distance * sin(self.camera_theta)*sin(self.camera_phi)
        self.camera_position[2] = self.domain_center[2] + self.camera_distance * cos(self.camera_phi)


class POVWriter_config():
    def __init__(self):
        self.options = PC_Options()
        self.pov_options = POV_Options()
        self.cell_color_definitions = {0: default_pov_colors}


    # This method parse XML povwriter config file
    def load_config_file(self, fname):
        
        tree = ET.parse(fname)
        root = tree.getroot()
        
        # Parsing save node
        node = root.find("save")
        self.options.folder = node.find("folder").text
        self.options.filebase = node.find("filebase").text
        self.options.time_index = int(node.find("time_index").text)
        self.options.filename = self.options.create_file_name(self.options.time_index)

        # Parsing options node
        node = root.find("options")
        self.options.nuclear_offset = float(node.find("nuclear_offset").text)
        self.options.cell_bound = float(node.find("cell_bound").text)
        self.options.threads = int(node.find("threads").text)

        use_standard_colors = node.find("use_standard_colors").text == 'true'
        if use_standard_colors:
            pigment_and_finish_function = standard_pigment_and_finish_function
        else:
            pigment_and_finish_function = my_pigment_and_finish_function

        # Parsing camera node
        node = root.find("camera")
        self.pov_options.camera_distance = float(node.find("distance_from_origin").text)
        self.pov_options.camera_theta = float(node.find("xy_angle").text)
        self.pov_options.camera_phi = float(node.find("yz_angle").text)
        
        self.pov_options.set_camera_from_spherical_location()
        self.pov_options.light_position[0] *= 0.5
        
        # Parsing clipping_planes node
        node = root.find("clipping_planes")
        for cp_node in node:
            cp = Clipping_Plane()
            vec = np.array([float(i) for i in cp_node.text.split(",")])
            cp.coefficients = vec
            cp.coefficients_to_normal_point()
            self.pov_options.clipping_planes.append(cp)
        print("Found %i clipping planes" % len(self.pov_options.clipping_planes))

        # Parsing cell_color_definitions node
        node = root.find("cell_color_definitions")
        for cell_cd_node in node:
            cell_type = int(cell_cd_node.attrib['type'])
            phase_color_dict = {}
            for phase_node in cell_cd_node:
                phase_name = phase_node.tag
                phase_color_dict[phase_name] = {}
                for comp_node in phase_node:
                    comp = comp_node.tag
                    color_array = np.array([float(i) for i in comp_node.text.split(",")])
                    phase_color_dict[phase_name][comp] = color_array
                
            self.cell_color_definitions[cell_type] = phase_color_dict
        
        print("Found %i cell color definitions ... " % len(self.cell_color_definitions) )


class POVWriter():
    def __init__(self, xml_config, format='physicell'):

        self._config = POVWriter_config()
        self._config.load_config_file(xml_config)
        self.format = format
    
    @property
    def pov_options(self):
        return self._config.pov_options

    @property
    def options(self):
        return self._config.options

    @property
    def threads(self):
        return self.options.threads
    
    @property
    def format(self):
        return self.options.format

    @property
    def cell_color_definitions(self):
        return self._config.cell_color_definitions

    @format.setter
    def format(self, format):
        self.options.format = format

    def _write_pov_header(self, fh):
        fh.write("#include \"colors.inc\"\n")
        fh.write("#include \"shapes.inc\" \n\n")
                
        fh.write("global_settings {\n")
        fh.write("  max_trace_level %i\n" % (self.pov_options.max_trace_level) )
        fh.write("  assumed_gamma %.4f\n" % (self.pov_options.assumed_gamma) )
        fh.write("}\n\n")
        fh.write("background {\n")
        fh.write("  color rgb <%i,%i,%i>\n" % (self.pov_options.background[0], 
                                               self.pov_options.background[1], 
                                               self.pov_options.background[2]) ) 
        fh.write("}\n\n")
        fh.write("camera {\n")
        fh.write("  location <%.3f,%.3f,%.3f>\n" % (self.pov_options.camera_position[0],
                                                    self.pov_options.camera_position[1],
                                                    self.pov_options.camera_position[2]) ) 
        fh.write("  right x\n")
        fh.write("  look_at <%i,%i,%i>\n" % (self.pov_options.camera_look_at[0], 
                                             self.pov_options.camera_look_at[1],
                                             self.pov_options.camera_look_at[2]) )  
        
        fh.write("  right <%i,%i,%i>\n" % (self.pov_options.camera_right[0], 
                                           self.pov_options.camera_right[1],
                                           self.pov_options.camera_right[2]) )  
        
        fh.write("  up <%i,%i,%i>\n" % (self.pov_options.camera_up[0], 
                                        self.pov_options.camera_up[1],
                                        self.pov_options.camera_up[2]) )  

        fh.write("  sky <%i,%i,%i>\n" % (self.pov_options.camera_sky[0],
                                         self.pov_options.camera_sky[1],
                                         self.pov_options.camera_sky[2]) )  
        fh.write(" }\n\n")
        fh.write("light_source {\n")
        fh.write("  <%i,%i,%i>\n" % (self.pov_options.light_position[0],
                                     self.pov_options.light_position[1],
                                     self.pov_options.light_position[2]) )  
        
        fh.write("  color rgb %.2f\n" % (self.pov_options.light_rgb) )
        fh.write("  fade_distance %.2f\n" % (self.pov_options.light_fade_distance) )
        fh.write("  fade_power %i\n" % (self.pov_options.light_fade_power) )
        fh.write("}\n\n")

    def _write_all_cells(self, fh, cells):
        bound = self.options.cell_bound
        for i,row in enumerate(cells):
            if row[1] < -bound or bound < row[1]:
                continue
            if row[2] < -bound or bound < row[2]:
                continue
            if row[3] < -bound or bound < row[3]:
                continue
            
            self._write_cell(fh, row)

    def _write_cell(self, fh, row):
        
        cell_type_index = self.options.columns_index_dict["cell_type"]
        phase_idx = self.options.columns_index_dict["phase"]
        
        cell_type = int(row[cell_type_index])
        current_phase_idx = int(row[phase_idx])
        
        current_phase_name = phases_dict[current_phase_idx]
        current_phase_name = phase_grouping[current_phase_name]
        colors = self.cell_color_definitions[cell_type][current_phase_name]

        center = row[1:4]

        # cytoplasm radius
        if self.options.format == 'physiboss':
            col_idx = self.options.columns_index_dict["cyto_radius"]
            radius = row[col_idx]
        
        elif self.options.format == 'physicell':
            col_idx = self.options.columns_index_dict["cyto_volume"]
            radius = pow( 3/(4*pi) * abs(row[col_idx]), (1./3.) )
        
        render = len(self.pov_options.clipping_planes) == 0
        intersect = False
        for i,cp in enumerate(self.pov_options.clipping_planes):
            dist = cp.signed_distance_to_plane(center)
            if dist <= -radius:
                render = True
            if -radius < dist <= radius:
                render = True
                intersect = True
        
        if intersect:
            fh.write("intersection{ \n")
        if render:
            if intersect:
                fh.write("union{ \n")
                for cp in self.pov_options.clipping_planes:
                    fh.write("plane{<")
                    fh.write("%.3f," % cp.coefficients[0])
                    fh.write("%.3f," % cp.coefficients[1])
                    fh.write("%.3f>," % cp.coefficients[2])
                    fh.write("%.3f\n" % cp.coefficients[3])
                    fh.write(" pigment {color rgb<")
                    fh.write("%.3f," % colors["cytoplasm"][0])
                    fh.write("%.3f," % colors["cytoplasm"][1])
                    fh.write("%.3f>}\n" % colors["cytoplasm"][2])
                    fh.write(" finish {ambient %.3f " % colors["finish"][0] )
                    fh.write("diffuse %.3f " % colors["finish"][1] )
                    fh.write("specular %.3f } }\n" % colors["finish"][2] )
                fh.write("} \n")
            self._write_pov_sphere(fh, center, radius, colors["cytoplasm"], colors["finish"])
        if intersect:
            fh.write("}\n")    


        # nuclear radius
        col_idx = self.options.columns_index_dict["nuc_volume"]
        radius = pow( 3/(4*pi) * abs(row[col_idx]), (1./3.) )
        if self.options.format == 'physiboss':
            col_idx = self.options.columns_index_dict["nuc_radius"]
            radius = row[col_idx]

        
        render = len(self.pov_options.clipping_planes) == 0
        intersect = False
        for i,cp in enumerate(self.pov_options.clipping_planes):
            dist = cp.signed_distance_to_plane(center)        
            if dist <= -(radius + self.options.nuclear_offset):
                render = True
            if -(radius + self.options.nuclear_offset) < dist <= (radius + self.options.nuclear_offset):
                render = True
                intersect = True
        
        if intersect > 0:
            fh.write("intersection{ \n")
        if render:
            if intersect:
                fh.write("union{ \n")
                for cp in self.pov_options.clipping_planes:
                    fh.write("plane{<")
                    fh.write("%.3f," % cp.coefficients[0])
                    fh.write("%.3f," % cp.coefficients[1])
                    fh.write("%.3f>," % cp.coefficients[2])
                    fh.write("%.3f\n" % (cp.coefficients[3]+self.options.nuclear_offset))
                    fh.write(" pigment {color rgb<")
                    fh.write("%.3f," % colors["nuclear"][0])
                    fh.write("%.3f," % colors["nuclear"][1])
                    fh.write("%.3f>}\n" % colors["nuclear"][2])
                    fh.write(" finish {ambient %.3f " % colors["finish"][0] )
                    fh.write("diffuse %.3f " % colors["finish"][1] )
                    fh.write("specular %.3f } }\n" % colors["finish"][2] )
                fh.write("} \n")
            self._write_pov_sphere(fh, center, radius, colors["nuclear"], colors["finish"], no_shadow=True)
        if intersect:
            fh.write("}\n")

    def _write_pov_sphere(self, fh, center, radius, pigment, finish, no_shadow=False, no_reflection=False):
        fh.write("sphere\n{\n")
        fh.write(" <%.4f,%.4f,%.4f>, %.4f" % (center[0], center[1], center[2], radius) )
        fh.write(" pigment {color rgb<%.2f,%.2f,%.2f>}\n" % (pigment[0],pigment[1],pigment[2]) )
        fh.write(" finish {ambient %.2f diffuse %.2f specular %.2f}\n" % (finish[0],finish[1],finish[2]) )
        if no_shadow:
            fh.write(" no_shadow ")
        if no_reflection:
            fh.write(" no_reflection ")
        fh.write("}\n")

    def write_pov_file(self, idx):

        fname = self.options.create_file_name(idx)
        print("Processing file ", fname)
        
        mat = self.read_cells_file(fname)
        print("Matrix size: %i x %i " % mat.shape)
        
        pov_fname = fname[:-4] + ".pov"
        with open(pov_fname, 'w') as fh:
            print("Creating file %s for output ... " % pov_fname)
            self._write_pov_header(fh)       
            print("Writing %i cells ... " % mat.shape[0])
            self._write_all_cells(fh, mat)
            return pov_fname
        
        return None

    def read_cells_file(self, fname):
        if self.format == 'physicell':
            from scipy.io import loadmat
            mat = loadmat(fname)['cells'].T
            return mat
        elif self.format == 'physiboss':
            data = []
            with open(fname) as fh:
                header = next(fh)
                for row in fh:
                    data.append([float(i) for i in row.split(";")])
                data = np.array(data)
                # Removing time storing column
                data = data[:,1:]
            return data
        else:
            raise InvalidFormatException(self.format)



def standard_pigment_and_finish_function():
    pass

def my_pigment_and_finish_function():
    pass