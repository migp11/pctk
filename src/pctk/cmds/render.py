import re
import os
import shutil
import argparse
import numpy as np


import multiprocessing as mp
from pctk.povwriter import POVWriter

povray_path = None

DEFAULT_XML = """
<?xml version="1.0" encoding="UTF-8"?>

<povwriter_settings>
	<camera> <!-- done -->
		<distance_from_origin units="micron">750</distance_from_origin>
		<xy_angle>3.92699081699</xy_angle> <!-- 5*pi/4 -->
		<yz_angle>1.0471975512</yz_angle> <!-- pi/3 --> 
	</camera>

	<options> <!-- done -->
		<use_standard_colors>true</use_standard_colors>
		<nuclear_offset units="micron">0.1</nuclear_offset> <!-- how far to clip nuclei in front of cyto --> 
		<cell_bound units="micron">500</cell_bound> <!-- only plot if |x| , |y| , |z| < cell_bound -->
		<threads>1</threads>
	</options>

	<save> <!-- done --> 
		<folder>./src/test/data/output/</folder>
		<filebase>output</filebase> 
		<time_index>0</time_index> 
	</save>
	
	<clipping_planes> <!-- done --> 
		<clipping_plane>0,-1,0,0</clipping_plane>
		<clipping_plane>-1,0,0,0</clipping_plane>
		<clipping_plane>0,0,1,0</clipping_plane>
	</clipping_planes>
	
	<!-- if using standard coloring (above), these will be used --> 
	<!-- otherwise, the code will look for a user-defined color/finish function -->  <!-- done --> 
	<cell_color_definitions>
		<!-- each cell's type will be used to choose a coloring scheme for live, apoptotic, or necrotic -->
		<!-- If the cell's type is not recognized, the standard coloring function will default to 0 --> 
		<cell_colors type="0">
			<live>
				<cytoplasm>.25,1,.25</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.03,0.125,0</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</live>
			<apoptotic>
				<cytoplasm>1,0,0</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0,0</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</apoptotic>
			<necrotic>
				<cytoplasm>1,0.5412,0.1490</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0.06765,0.018625</nuclear>
				<finish>0.01,0.5,0.1</finish> <!-- ambient,diffuse,specular -->
			</necrotic>
		</cell_colors>
		
		<cell_colors type="1">
			<live>
				<cytoplasm>0.25,0.25,1</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.03,0.03,0.125</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</live>
			<apoptotic>
				<cytoplasm>1,0,0</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0,0</nuclear>
				<finish>0.05,1,0.1</finish> <!-- ambient,diffuse,specular -->
			</apoptotic>
			<necrotic>
				<cytoplasm>1,0.5412,0.1490</cytoplasm> <!-- red,green,blue,filter --> 
				<nuclear>0.125,0.06765,0.018625</nuclear>
				<finish>0.01,0.5,0.1</finish> <!-- ambient,diffuse,specular -->
			</necrotic>
		</cell_colors>
	
	</cell_color_definitions>

</povwriter_settings>
"""

def create_parser():

    povray_link = "http://www.povray.org/download/"

    parser = argparse.ArgumentParser(description="Render a bunch of PhysiCell output file into povray files")
    
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

    parser.add_argument("--render",  action='store_true',
                        help="Render the .pov files into .png. Requires povray ({povray_link})")

    parser.add_argument("--width", action="store", dest="width", type=int, default=2160, 
                        help="Width for povray rendered image")

    parser.add_argument("--height", action="store", dest="height", type=int, default=2160, 
                        help="Heigh for povray rendered image")

    parser.add_argument("--cpus", action="store", dest="cpus", type=int, default=4, 
                        help="Total CPUs availabile to run in parallel using multiprocessing")

    parser.add_argument("--create-config", dest="create_default_config", default=False,
                        help="Output format")

    return parser

def check_povray(exec='povray'):
    global povray_path
    povray_path = shutil.which(exec)
    return (povray_path is not None)

def local_write_pov_file(writer, idx):
    fname = writer.write_pov_file(idx)
    return fname

def render_to_png(pov_fname, width=1024, height=1024):
    cmd_line = f"{povray_path} -h{height} -w{width} -a {pov_fname}"
    exit_flag = os.system(cmd_line)
    if exit_flag != 0:
        print(f"Somthing went wrong running povray {cmd_line}. Command finished with exit flag {exit_flag}")

    png_fname = pov_fname[0:-4] + ".png"
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
                for fname in pov_files:
                    png = render_to_png(pov_fname, width=width, height=height)
                    png_files.append(png)
                
            

def main():
    parser = create_parser()
    args = parser.parse_args()
    write_pov_files(args)

if __name__ == '__main__':
    main()