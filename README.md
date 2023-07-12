# Introduction
PhysiCell ToolKit (PCTK) is a tiny project that aims to develop a lightweight library and command-line general scripts to process and analyze agent-based simulation of multicellular systems produced by PhysiCell simulations ([http://physicell.org/](http://physicell.org/)) developed by Paul Macklin at MathCancer. Although there are already available tools for handling PhysiCell outputs [https://github.com/PhysiCell-Tools/python-loader](https://github.com/PhysiCell-Tools/python-loader), here we aim to gather together and organize different pieces of Python code that have been anyhow, recurrently useful in the past, when dealing with PhysiCell and PhysiBoSS. Currently, the package implements a simple module ([multicellds.py](https://github.com/migp11/pctk/blob/master/modules/multicellds.py)) to parse and handle MultiCellDS XML file format and uses the schema defined there to parse and process \.mat files containing the cells and microenvironment time-dependent output. On the top of this module, we have developed a set of command-line tools for processing and creating basic plots, including time courses of the number of alive and dead cells (apoptotic, necrotic) as well as to generate POV files used as inputs for rendering nice 3D rendering of the multicellular models using [POV-Ray](http://www.povray.org/). PCTK can used both, as a library and as a stand-alone command line tool.

# Installation
PCTK is pure Python code with few dependencies and only requires the installation of some Python modules. 
### On Linux systems using virtualenv + pip
1 - create a new virtual environment, activate it and install the requirements:<br>

```virtualenv -p python3 venv```
<br><br>
2 - Activate the virtual environment:<br>

```source venv/bin/activate```
<br><br>
3 - Install pctk using pip:<br>

```pip install pctk```
<br><br>
PCTK can also be installed directly from the git repository to get the latest version:<br>

```
pip install git+https://github.com/migp11/pctk/
```

The last step for generating 3D renders of cells from `.pov` files, is done using the Persistence of Vision Ray Tracer (POV-Ray). POV-Ray is a cross-platform ray-tracing standalone program that generates images from a text-based scene description. POV-Ray is open source and can be freely obtained from: <br>
* [http://www.povray.org/download/](http://www.povray.org/download/)

# MultiCellDS class

MultiCellDS is the standard format for PhysiCel and thus PhysiBoSS outputs. For each simulation, the state is saved at intervals of time *t* different files in `.xml` and `.mat` formats are generated to store the information on the individual cells and the microenvironment. The module `multicellds` provides a simple Python API for loading the different outputs into Pandas Dataframes; among other functionalities, `multicellds` allows to iterate over the sequences of outputs stored at each time step of the simulations. Below there are a couple of code snippets:
<br>

```
from pctk import multicellds 

output_folder = "output/"

# Creating a MCDS reader
reader = multicellds.MultiCellDS(output_folder=output_folder)

# Counting the number of stored time steps
num_of_files = reader.cells_file_count()

# creating an iterator to load a cell DataFrame for each stored simulation time step
df_iterator = reader.cells_as_frames_iterator()

for (t,df_cells) in df_iterator:
    alive = (df_cells.current_phase<=14).sum()
    dead = (df_cells.current_phase>14).sum()
    print(f"Total alive {alive} and dead {dead} cellw at time {t}")

```

This code snippet will iterate over all simulation outputs and print the number of alive an dead cells aat each saved time point.

# Ready-to-run command line tool-kit
There are some ready-to-run scripts that can be used to summarize and visualize PhysiCell/PhysiBoSS simulation outputs. 
These command line tools allow generating summary plots and `.csv` tables, as well as, 3D renders of the less at a given time point. Rendering requires an install and running version of PovRay.
Subcommands include:
* `plot-time-course`
* `write-pov`


~~~~
usage: pctk [-h] [--format {physicell,physiboss}] output_folder {plot-time-course,povray} ...

PhysiCell Tool Kit 0.2.2 for handling and processing PhysiCell outputs

positional arguments:
  output_folder         Folder where the simulation output is stored
  {plot-time-course,povray}
                        sub-command help

optional arguments:
  -h, --help            show this help message and exit
  --format {physicell,physiboss}
                        Format of the input data

~~~~

## Ploting time course:
The command plot-time-course plot number of cells vs time grouping cell by phase (alive, necrotic, apoptotic) <br>
The colour mapping can be easily customized to represent other cell-agent variables (eg. colour mutants or other cell states)
	

~~~~
usage: pctk output_folder plot-time-course [-h] [--figout FIG_FNAME] [--csvout CSV_FNAME]

Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time

optional arguments:
  -h, --help          show this help message and exit
  --figout FIG_FNAME  File name to save the plot
  --csvout CSV_FNAME  File name to store the summary table used for the plot
	
~~~~

#### Examples

`pctk output/ plot-time-course --figout physicell_time_plot.png`

![image](./docs/cell_vs_time.png)<br>
**Figure 1. Time course of a simulation of cancer cells under a treatment.**
<br>


## Generations of pov files for 3D rendering: povwriter.py
This command is an almost "literal" translation from C++  to Python 3. The original C++ PhysiCell-povwriter is developed and maintained by Paul Macklin at MatchCancer and can be found in the following link:

<br>
[https://github.com/PhysiCell-Tools/PhysiCell-povwriter](https://github.com/PhysiCell-Tools/PhysiCell-povwriter)
<be>
[http://www.mathcancer.org/blog/povwriter/](http://www.mathcancer.org/blog/povwriter/)

<br>
While I've not found many differences in the level of performance, the main advantage of having a Python version of PhysiCell-povwriter is that is much easier to extend and customize. Furthermore, handling command line arguments and parsing config files is also much easier in Python. And the package can be easily extended to add new subcommands and functionalities. The subcommands `pctk Povwriter` reads xml-based configuration for generating .pov files from PhysiCell output files.
The generated pov files can then be rendered using the open source The Persistence of Vision Raytracer suite PovRay ([http://www.povray.org/](http://www.povray.org/)).


The command PovWriter uses an XML config file and PhyisiCell outputs to generate POV files for each time step <br>

```
usage: pctk output_folder povray [-h] [--config CONFIG] [--render] [--width WIDTH] [--height HEIGHT] [--cpus CPUS] [--create-config CONFIG_OUT] [--idxs STRN_IDXS]

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       XML configuration file for creating pov files
  --render              Render the .pov files into .png. Requires povray ({povray_link})
  --width WIDTH         Width for povray rendered image
  --height HEIGHT       Heigh for povray rendered image
  --cpus CPUS           Total cpus availabile to run in parallel using multiprocessing
  --create-config CONFIG_OUT
                        Create a default config XML file for generating POV files
  --idxs STRN_IDXS      String specifying the indexes of the output files. The supported options include: - slices: 1:10:1 - indexes: 1,2,5,10 - all (use glob)
```
### Example: generating a new povwriter.xml configuration files

```
pctk povwriter --create-config povwriter.xml
Writing default POV-write config into povwriter.xml
```
This command will generate the `XML` configuration file needed to create `.pov` files which are used by PovRay to generate the 3D renders. The file looks like this:

```<povwriter_settings>
	<camera>
		<distance_from_origin units="micron">750</distance_from_origin>
		<xy_angle>3.92699081699</xy_angle> 
		<yz_angle>1.0471975512</yz_angle>  
	</camera>

	<options>
		<use_standard_colors>true</use_standard_colors>
		<nuclear_offset units="micron">0.1</nuclear_offset>  
		<cell_bound units="micron">500</cell_bound> 
		<threads>1</threads>
	</options>

	<save> 
		<folder>test/</folder>
		<filebase>output</filebase> 
		<time_index>0</time_index> 
	</save>
	
	<clipping_planes>  
		<clipping_plane>0,-1,0,0</clipping_plane>
		<clipping_plane>-1,0,0,0</clipping_plane>
		<clipping_plane>0,0,1,0</clipping_plane>
	</clipping_planes>
	
	 
	   
	<cell_color_definitions>
		
		 
		<cell_colors type="0">
			<alive>
				<cytoplasm>.25,1,.25</cytoplasm>  
				<nuclear>0.03,0.125,0</nuclear>
				<finish>0.05,1,0.1</finish> 
			</alive>
			<apoptotic>
				<cytoplasm>1,0,0</cytoplasm>  
				<nuclear>0.125,0,0</nuclear>
				<finish>0.05,1,0.1</finish> 
			</apoptotic>
			<necrotic>
				<cytoplasm>1,0.5412,0.1490</cytoplasm>  
				<nuclear>0.125,0.06765,0.018625</nuclear>
				<finish>0.01,0.5,0.1</finish> 
			</necrotic>
		</cell_colors>
		
		<cell_colors type="1">
			<alive>
				<cytoplasm>0.25,0.25,1</cytoplasm>  
				<nuclear>0.03,0.03,0.125</nuclear>
				<finish>0.05,1,0.1</finish> 
			</alive>
			<apoptotic>
				<cytoplasm>1,0,0</cytoplasm>  
				<nuclear>0.125,0,0</nuclear>
				<finish>0.05,1,0.1</finish> 
			</apoptotic>
			<necrotic>
				<cytoplasm>1,0.5412,0.1490</cytoplasm>  
				<nuclear>0.125,0.06765,0.018625</nuclear>
				<finish>0.01,0.5,0.1</finish> 
			</necrotic>
		</cell_colors>
	
	</cell_color_definitions>``` 


#### Creating POV files using config/povwriter-settings.xml config
```
pctk povwriter --config config/povwriter-settings.xml
Found 3 clipping planes
Found 2 cell color definitions ... 
Start processing  4 cpus
Processing file  ./src/test/data/output/output00000000_cells_physicell.mat
Matrix size: 3963 x 28 
Creating file ./src/test/data/output/output00000000_cells_physicell.pov for output ... 
Writing 3963 cells ... 
Finished!
```

#### Creating POV files using config/povwriter-settings.xml slicing over physicell output files using 0:4:2
```
pctk output/ povwriter --config src/test/data/config/povwriter-settings.xml --idxs 0:4:2
Found 3 clipping planes
Found 2 cell color definitions ... 
Start processing  4 cpus
Processing file  ./src/test/data/output/output00000000_cells_physicell.mat
Matrix size: 3963 x 28 
Creating file ./src/test/data/output/output00000000_cells_physicell.pov for output ... 
Writing 3963 cells ... 
Processing file  ./src/test/data/output/output00000002_cells_physicell.mat
Matrix size: 4137 x 28 
Creating file ./src/test/data/output/output00000002_cells_physicell.pov for output ... 
Writing 4137 cells ... 
Finished!
```

Any of these commands will generate one or many .pov files. If you have PovRay instaled in your system you can try

```
pctk povwriter --config config/povwriter-settings.xml --idx 10 --render
```

If PovRay is installed, this command will generate a render using the provided `povwriter-settings.xm`

![image](./docs/cell3d.png)<br>
**Figure 2. Render of a 3D spheroid of cancer cells.**
<br>

```
povray -W720 -H680 -a [path to pov file]
```
to render the .pov file a generate an image. Parameters -H -W and -a correspond to width, height and antilaizing, respectively.
