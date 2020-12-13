#!/usr/bin/env python3
# coding: utf-8

import sys, os, re, json
from math import pi, sin, cos

import argparse
import numpy as np
from scipy.io import loadmat
import xml.etree.ElementTree as ET

import multiprocessing as mp


__author__ = "Miguel Ponce de Leon"
__copyright__ = "Copyright 2020, Tools for PhysiCell project"
__credits__ = ["Miguel Ponce de Leon"]
__license__ = "GPL 3.0"
__version__ = "0.1.0"
__maintainer__ = "Miguel Ponce de Leon"
__email__ = "miguel.ponce@bsc.es"
__status__ = "dev"


default_POV_options = None
options = None
pigment_and_finish_function = None

cell_color_definitions = {0: {} }
cell_color_definitions[0]["cytoplasm"] = [1,1,1,0]
cell_color_definitions[0]["nuclear"] = [.5,.5,.5,0]
cell_color_definitions[0]["finish"] = [0.05,1,0.1]

pc_columns_index_dict = { "cyto_volume": 4, "cell_type": 5, "phase": 7, "nuc_volume": 9}
pb_columns_index_dict = { "cyto_radius": 4, "cell_type": 11, "phase": 13, "nuc_radius": 6}

columns_index_dict = {}
read_cells_file = None

columns_index_dict = {}

phase_grouping = { 
    "Ki67_positive_premitotic": "live",  
    "Ki67_positive_postmitotic": "live", 
    "Ki67_positive": "live", 
    "Ki67_negative": "live", 
    "G0G1_phase": "live", 
    "G0_phase": "live", 
    "G1_phase": "live", 
    "G1a_phase": "live", 
    "G1b_phase": "live", 
    "G1c_phase": "live", 
    "S_phase": "live", 
    "G2M_phase": "live", 
    "G2_phase": "live", 
    "M_phase": "live", 
    "live": "live", 
    "apoptotic": "apoptotic",  
    "necrotic_lysed": "necrotic", 
    "necrotic_swelling": "necrotic"
    }

phases_dict = {
    0: "Ki67_positive_premitotic",
    1: "Ki67_positive_postmitotic",
    2: "Ki67_positive",
    3: "Ki67_negative",
    4: "G0G1_phase",
    5: "G0_phase",
    6: "G1_phase",
    7: "G1a_phase",
    8: "G1b_phase",
    9: "G1c_phase",
    10: "S_phase",
    11: "G2M_phase",
    12: "G2_phase",
    13: "M_phase",
    14: "live",
    100: "apoptotic",
    101: "necrotic_swelling",
    102: "necrotic_lysed",
    103: "necrotic",
    104: "debris"
    }


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

class Options:
    def __init__(self, folder="sample", filebase="output", format="physicell",
                 time_index=3696, camera_distance=1500, nuclear_offset=0.1, cell_bound=750, 
                 threads=1):

        self.folder = folder
        self.filebase = filebase
        self.format = format
        self.time_index = time_index
        self.filename = self.create_file_name(time_index)
        self.camera_distance = camera_distance
        self.camera_theta = 5*pi/4
        self.camera_phi = pi/3
        
        self.nuclear_offset = nuclear_offset
        self.cell_bound = cell_bound
        self.threads = threads

    def create_file_name(self, index):
        if self.format == 'physicell':
            fname  = "%s/%s%08i_cells_physicell.mat" % (self.folder, self.filebase, index)
        elif self.format == 'physiboss':
            fname  = "%s/cells_%05i.txt" % (self.folder, index)
        else:
            fname = None
        return fname

class POV_Options():
    
    def __init__(self):
        
        self.max_trace_level = 1
        self.assumed_gamma = 1.0
    
        self.domain_center = np.array([0,0,0])
        self.domain_size = np.array([2000,2000,2000])
        
        self.background = np.array([1,1,1])
        
        self.camera_distance = ( self.domain_size[0] + self.domain_size[1] + self.domain_size[2] ) * 1.25 / 3.0
        self.camera_position = np.array([0,0,0])
        self.set_camera_from_spherical_location( self.camera_distance , 5.0*pi/4.0 , pi/4.0 )
        
        self.camera_look_at = self.domain_center.copy()
        self.camera_right = np.array([-1,0,0]) # computer graphics are goofy. switch to usual coordinate system
        self.camera_up = np.array([0,0,1])
        self.camera_sky = np.array([0,0,1])
        
        self.light_position = np.array([0,0,0])
    
        self.light_position[0] = self.domain_center[0] - 0.5*self.domain_size[0]; 
        self.light_position[1] = self.domain_center[1] - 0.5*self.domain_size[1]; 
        self.light_position[2] = self.domain_center[2] + 1.5*self.domain_size[2]; 
    
        self.light_rgb = 0.75; 
        self.light_fade_distance = np.linalg.norm( self.domain_size ); 
        self.light_fade_power = 2; 
        
        self.no_shadow = False
        self.no_reflection = False
        
        self.clipping_planes = []
        
    def set_camera_from_spherical_location(self, distance, theta, phi):
        self.camera_position[0] = self.domain_center[0] + distance*cos(theta)*sin(phi) 
        self.camera_position[1] = self.domain_center[1] + distance*sin(theta)*sin(phi)
        self.camera_position[2] = self.domain_center[2] + distance*cos(phi)

def standard_pigment_and_finish_function():
    pass

def my_pigment_and_finish_function():
    pass

def load_config_file(fname):
    
    tree = ET.parse(fname)
    root = tree.getroot()
    
    # Parsing save node
    node = root.find("save")
    options.folder = node.find("folder").text
    options.filebase = node.find("filebase").text
    options.time_index = int(node.find("time_index").text)

    mat_fname  = "./%s/%s%08i_cells_physicell.mat" % (options.folder, options.filebase, options.time_index)
    options.filename = mat_fname

    # Parsing options node
    node = root.find("options")
    use_standard_colors = node.find("use_standard_colors").text == 'true'
    if use_standard_colors:
        pigment_and_finish_function = standard_pigment_and_finish_function
    else:
        pigment_and_finish_function = my_pigment_and_finish_function

    options.nuclear_offset = float(node.find("nuclear_offset").text)
    options.cell_bound = float(node.find("cell_bound").text)
    options.threads = int(node.find("threads").text)

    # Parsing clipping_planes node
    node = root.find("clipping_planes")
    for cp_node in node:
        cp = Clipping_Plane()
        vec = np.array([float(i) for i in cp_node.text.split(",")])
        cp.coefficients = vec
        cp.coefficients_to_normal_point()
        default_POV_options.clipping_planes.append(cp)
    print("Found %i clipping planes" % len(default_POV_options.clipping_planes))

    # Parsing cell_color_definitions node
    node = root.find("cell_color_definitions")
    for cell_cd_node in node:
        cell_type = int(cell_cd_node.attrib['type'])
        phase_color_dict = {}
        for phase_node in cell_cd_node:
            phase_name = phase_node.tag
            cytoplasm = phase_node.find("cytoplasm")
            cyto_color = np.array([float(i) for i in cytoplasm.text.split(",")])
            nuclear = phase_node.find("nuclear")
            nuc_color = np.array([float(i) for i in nuclear.text.split(",")])
            
            phase_color_dict[phase_name] = { "cytoplasm":cyto_color, 
                                             "nuclear":nuc_color,
                                             "finish":[0.05,1,0.1]
                                             }
        cell_color_definitions[cell_type] = phase_color_dict
    print("Found %i cell color definitions ... " % len(cell_color_definitions) )

    # Parsing camera node
    node = root.find("camera")
    options.camera_distance = float(node.find("distance_from_origin").text)
    options.camera_theta = float(node.find("xy_angle").text)
    options.camera_phi = float(node.find("yz_angle").text)

    camera_distance = options.camera_distance
    camera_theta = options.camera_theta
    camera_phi = options.camera_phi
    
    default_POV_options.set_camera_from_spherical_location( 
        camera_distance, camera_theta, camera_phi )
    default_POV_options.light_position[0] *= 0.5

def write_pov_header(fh, pov_options):
    fh.write("#include \"colors.inc\"\n")
    fh.write("#include \"shapes.inc\" \n\n")
            
    fh.write("global_settings {\n")
    fh.write("  max_trace_level %i\n" % (pov_options.max_trace_level) )
    fh.write("  assumed_gamma %.4f\n" % (pov_options.assumed_gamma) )
    fh.write("}\n\n")
    fh.write("background {\n")
    fh.write("  color rgb <%i,%i,%i>\n" % (pov_options.background[0], 
                                                 pov_options.background[1], 
                                                 pov_options.background[2]) ) 
    fh.write("}\n\n")
    fh.write("camera {\n")
    fh.write("  location <%.3f,%.3f,%.3f>\n" % (pov_options.camera_position[0],
                                                pov_options.camera_position[1],
                                                pov_options.camera_position[2]) ) 
    fh.write("  right x\n")
    fh.write("  look_at <%i,%i,%i>\n" % (pov_options.camera_look_at[0], 
                                               pov_options.camera_look_at[1],
                                               pov_options.camera_look_at[2]) )  
    
    fh.write("  right <%i,%i,%i>\n" % (pov_options.camera_right[0], 
                                             pov_options.camera_right[1],
                                             pov_options.camera_right[2]) )  
    
    fh.write("  up <%i,%i,%i>\n" % (pov_options.camera_up[0], 
                                          pov_options.camera_up[1],
                                          pov_options.camera_up[2]) )  

    fh.write("  sky <%i,%i,%i>\n" % (pov_options.camera_sky[0],
                                           pov_options.camera_sky[1],
                                           pov_options.camera_sky[2]) )  
    fh.write(" }\n\n")
    fh.write("light_source {\n")
    fh.write("  <%i,%i,%i>\n" % (pov_options.light_position[0],
                                       pov_options.light_position[1],
                                       pov_options.light_position[2]) )  
    
    fh.write("  color rgb %.2f\n" % (pov_options.light_rgb) )
    fh.write("  fade_distance %.2f\n" % (pov_options.light_fade_distance) )
    fh.write("  fade_power %i\n" % (pov_options.light_fade_power) )
    fh.write("}\n\n")

def write_all_cells(fh, cells, options, pov_options):
    bound = options.cell_bound
    for i,row in enumerate(cells):
        if row[1] < -bound or bound < row[1]:
            continue
        if row[2] < -bound or bound < row[2]:
            continue
        if row[3] < -bound or bound < row[3]:
            continue
        
        write_cell(fh, row, pov_options, options)

def write_cell(fh, row, pov_options, options):
    
    cell_type_index = columns_index_dict["cell_type"]
    phase_idx = columns_index_dict["phase"]
    
    cell_type = int(row[cell_type_index])
    current_phase_idx = int(row[phase_idx])
    
    current_phase_name = phases_dict[current_phase_idx]
    current_phase_name = phase_grouping[current_phase_name]
    colors = cell_color_definitions[cell_type][current_phase_name]

    center = row[1:4]

    # cytoplasm radius
    if options.format == 'physiboss':
        col_idx = columns_index_dict["cyto_radius"]
        radius = row[col_idx]
    elif options.format == 'physicell':
        col_idx = columns_index_dict["cyto_volume"]
        radius = pow( 3/(4*pi) * abs(row[col_idx]), (1./3.) )
    
    render = len(pov_options.clipping_planes) == 0
    intersect = False
    for i,cp in enumerate(pov_options.clipping_planes):
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
            for cp in pov_options.clipping_planes:
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
        write_pov_sphere(fh, center, radius, colors["cytoplasm"], colors["finish"])
    if intersect:
        fh.write("}\n")    

    nuclear_offset = options.nuclear_offset
    # nuclear radius
    if options.format == 'physiboss':
        col_idx = columns_index_dict["nuc_radius"]
        radius = row[col_idx]
    else:
        col_idx = columns_index_dict["nuc_volume"]
        radius = pow( 3/(4*pi) * abs(row[col_idx]), (1./3.) )
    
    render = len(pov_options.clipping_planes) == 0
    intersect = False
    for i,cp in enumerate(pov_options.clipping_planes):
        dist = cp.signed_distance_to_plane(center)        
        if dist <= -(radius+nuclear_offset):
            render = True
        if -(radius+nuclear_offset) < dist <= (radius+nuclear_offset):
            render = True
            intersect = True
    
    if intersect > 0:
        fh.write("intersection{ \n")
    if render:
        if intersect:
            fh.write("union{ \n")
            for cp in pov_options.clipping_planes:
                fh.write("plane{<")
                fh.write("%.3f," % cp.coefficients[0])
                fh.write("%.3f," % cp.coefficients[1])
                fh.write("%.3f>," % cp.coefficients[2])
                fh.write("%.3f\n" % (cp.coefficients[3]+nuclear_offset))
                fh.write(" pigment {color rgb<")
                fh.write("%.3f," % colors["nuclear"][0])
                fh.write("%.3f," % colors["nuclear"][1])
                fh.write("%.3f>}\n" % colors["nuclear"][2])
                fh.write(" finish {ambient %.3f " % colors["finish"][0] )
                fh.write("diffuse %.3f " % colors["finish"][1] )
                fh.write("specular %.3f } }\n" % colors["finish"][2] )
            fh.write("} \n")
        write_pov_sphere(fh, center, radius, colors["nuclear"], colors["finish"], no_shadow=True)
    if intersect:
        fh.write("}\n")

def write_pov_sphere(fh, center, radius, pigment, finish, no_shadow=False, no_reflection=False):
    fh.write("sphere\n{\n")
    fh.write(" <%.4f,%.4f,%.4f>, %.4f" % (center[0], center[1], center[2], radius) )
    fh.write(" pigment {color rgb<%.2f,%.2f,%.2f>}\n" % (pigment[0],pigment[1],pigment[2]) )
    fh.write(" finish {ambient %.2f diffuse %.2f specular %.2f}\n" % (finish[0],finish[1],finish[2]) )
    if no_shadow:
        fh.write(" no_shadow ")
    if no_reflection:
        fh.write(" no_reflection ")
    fh.write("}\n")

def write_pov_file(idx, pov_options, options):

    fname = options.create_file_name(idx)
    print("Processing file ", fname)
    mat = read_cells_file(fname)
    print("Matrix size: %i x %i " % mat.shape)
    
    pov_fname = fname[:-4] + ".pov"
    with open(pov_fname, 'w') as fh:
        print("Creating file %s for output ... " % pov_fname)
        write_pov_header(fh, default_POV_options)       
        print("Writing %i cells ... " % mat.shape[0])
        write_all_cells(fh, mat,options, default_POV_options)
        return True
    
    return False

def physicell_read_file(fname):
    mat = loadmat(fname)['cells'].T
    return mat

def physiboss_read_file(fname, sep=";"):
    data = []
    with open(fname) as fh:
        header = next(fh)
        for row in fh:
            data.append([float(i) for i in row.split(";")])
        data = np.array(data)
        # Removing time storing column
        data = data[:,1:]
    print(data[:,4].max())
    return data

def create_parser():

    parser = argparse.ArgumentParser(description="Render a bunch of physicell outputfile into povray files")
    
    parser.add_argument("xml_config", action="store", help="XML configuration file")

    parser.add_argument("--idxs", action="store", dest="strn_idxs", 
                        help="String specifing the indexes of the output files. \
                              The supported options include: \
                              - slices: 1:10:1\
                              - indexes: 1,2,5,10\
                              - all (use glob)", 
                        default="")
    
    parser.add_argument("--format", action="store", dest="format", choices=("physicell", "physiboss"),
                        help="Format of the input data", default="physicell")

    parser.add_argument("--out-format", action="store", dest="out_format", default="pov",
                        choices=('pov', 'png'), help="Output format")

    return parser

def main():    
    # Makeing parameters and options storing classes global variables
    global phases_dict
    global phase_grouping
    global default_POV_options
    global options
    global pigment_and_finish_function
    global cell_color_definitions
    global read_cells_file
    global columns_index_dict

    #
    parser = create_parser()
    args = parser.parse_args()

    # Deafult option stoting classes
    options = Options()
    default_POV_options = POV_Options()
    
    ###########################################################

    # Loadgin XML configuration 
    load_config_file(args.xml_config)

    ###########################################################


    num_of_jobs = options.threads
    options.format = args.format
    if args.format == 'physicell':
        read_cells_file = physicell_read_file
        columns_index_dict = pc_columns_index_dict
    elif args.format == 'physiboss':
        read_cells_file = physiboss_read_file
        columns_index_dict = pb_columns_index_dict
    
    pattern_slices = re.compile("(\d*):(\d*):(\d*)")
    pattern_indexes = re.compile("(\d+)(,\d+)*")
    pattern_all = re.compile("^all$")

    index_list = []

    match = re.search(pattern_slices, args.strn_idxs)
    if match:
        from_idx = int(match.group(1))
        to_idx = int(match.group(2))
        inc = int(match.group(3))
        index_list = range(from_idx, to_idx, inc)
    elif re.search(pattern_indexes, args.strn_idxs):
        index_list = [int(i) for i in args.strn_idxs.split(",")]
    elif re.search(pattern_all, args.strn_idxs):
        pass
    else:
        index_list = [options.time_index]
    
    if num_of_jobs > 1:
        pool = mp.Pool(num_of_jobs)
        results = [pool.apply(write_pov_file, args=(idx, default_POV_options, options)) 
                        for idx in index_list]
        pool.close()
    else:
        for idx in index_list:
            write_pov_file(idx, default_POV_options, options)


main()

# options.max_trace_level = int(0)
# options.assumed_gamma = 0.0
# options.background = (0.,0.,0.)
# options.camera_look_at = (0.,0.,0.)
# options.camera_right = (0.,0.,0.)
# options.camera_up = (0.,0.,0.)
# options.camera_sky = (0.,0.,0.)
# options.light_position = (0.,0.,0.)
# options.light_rgb = 0.
# options.light_fade_distance = 0.
# options.light_fade_power = int(0)