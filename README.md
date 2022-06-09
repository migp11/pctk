# Introduction
PhysiCell ToolKit (PCTK) is a tiny project that aims to develop a lightweight library and command-line general scripts to process and analyze agent-based simulation of multicellular systems produced by PhysiCell simulations ([http://physicell.org/](http://physicell.org/)) developed by Paul Macklin at MathCancer.
<br>
Although there are already available tools for handling PhysiCell outputs [https://github.com/PhysiCell-Tools/python-loader](https://github.com/PhysiCell-Tools/python-loader), here we aim to gather together and organize different pieces of python code that have been anyhow, recurrently useful in the past, when dealing with PhysiCell and PhysiBoSS. Currently, the package implements a simple module ([multicellds.py](https://github.com/migp11/pctk/blob/master/modules/multicellds.py)) to parse and handle MultiCellDS XML file format and uses the schema defined there to parse and process \.mat files containing the cells and microenvironment time dependent output. On the top of this module we have developed a set of command-line tools for processing and creating basic plots, including time courses of the number of alive and dead cells (apoptotic, necrotic) as well as to generate POV files used as inputs for rendering nice 3D rendering of the multicellular models using [POV-Ray](http://www.povray.org/). PCTK can used both, as library and as stand-alone command line tool.
<br>

# Installation
PCTK is pure python code with few dependencies and only requieres the installation of some python modules. 
### On linux systems using virtualenv + pip
- 1  create a new virtual environemnt, activate it and install the requirments
~~~~
virtualenv -p python3.8 myenv
source myenv/bin/activate
python setup.py install
~~~~
Thats it! If you want to run the script from any location add the base folder to your PATH environmental variable. And if you want to access the multicellds class, add modules/multicellds.py to your PYTHONPATH.

The last step for generating 3D renders of cell from .pov files, it is done using Persistence of Vision Ray Tracer (POV-Ray). POV-Ray is a cross-platform ray-tracing standalone program that generates images from a text-based scene description. POV-Ray is open source () and can be freely obtaind from: <br>
* [http://www.povray.org/download/](http://www.povray.org/download/)

# MultiCellDS class

Upcoming

# Ready-to-run scripts
There are some ready-to-run scripts that can be used to summarize and visualize PhysiCell/PhysiBoSS simulation. These scripts allow to generate cell vs time plots as well 3D renders for time snapshots.

## Ploting time course: plot_time_course.py
The script plot_time_course.py plot number of cells vs time grouping cell by phase (alive, necrotic, apoptotic) <br>
The color mapping can be easily customized to represent other cell-agent variables (eg. color mutants or other cell states)
	
~~~~
usage: plot_time_course.py [-h] [--format {physicell,physiboss}]
                           [--figout FIG_FNAME] [--csvout CSV_FNAME]
                           data_folder

Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time

positional arguments:
  data_folder           folder were the data is stored

optional arguments:
  -h, --help            show this help message and exit
  --format {physicell,physiboss}
                        Format of the input data
  --figout FIG_FNAME    File name to save the plot
  --csvout CSV_FNAME    File name to store the summary table used for the plot	
~~~~

#### Examples
`plot_time_course.py output_test --format physiboss --figout physibos_time_plot.png`

`plot_time_course.py output_test --format physicell --figout physicell_time_plot.png`


## Generations of pov files for 3D rendering: povwriter.py
This script is a "literal" translation from C++ to Python 3. \
The original C++ povrtiter is developed an mantined by Paul Macklin at MatchCancer \
and can be found in the following link [https://github.com/PhysiCell-Tools/PhysiCell-povwriter](https://github.com/PhysiCell-Tools/PhysiCell-povwriter)
<br>
While I've not found many difference at the level of performance, the main advantage of having python version of PhysiCell-povwriter is that is much easiert to extend and customize. Furthermore, handling command line arguments and parsing config files is also much easier in python. Nonetheless, the original motivation of this development was to have a povwrite capable of handling PhysiBoSS output format (which is different from PhysiCell's format).<br>
The script povwriter.py reads xml configuration file and then iterates over a range of \*.mat files to create pov files.<br>
The generated pov files can then be renderied usign the open source The Persistence of Vision Raytracer suite PovRay ([http://www.povray.org/](http://www.povray.org/)).

~~~~
usage: povwriter.py [-h] [--idxs STRN_IDXS] [--format {physicell,physiboss}]
                    [--out-format {pov,png}]
                    xml_config

Render a bunch of physicell outputfile into povray files

positional arguments:
  xml_config            XML configuration file

optional arguments:
  -h, --help            show this help message and exit
  --idxs STRN_IDXS      String specifing the indexes of the output files. The
                        supported options include: - slices: 1:10:1 - indexes:
                        1,2,5,10 - all (use glob)
  --format {physicell,physiboss}
                        Format of the input data
  --out-format {pov,png}
                        Output format
	
~~~~

#### Examples
~~~~
povwriter.py config/povwriter-settings.xml --format physicell
povwriter.py config/povwriter-settings.xml --format physicell --idxs 0:4:1
povwriter.py config/povwriter-settings.xml --format physicell --idxs 1,3,0

./povwriter.py config/povwriter-settings.xml --format physiboss
./povwriter.py config/povwriter-settings.xml --format physiboss --idxs 0:490:120
./povwriter.py config/povwriter-settings.xml --format physiboss --idxs 0,240
~~~~

Any of these commands will generate one or many .pov files. If you have povray instaled in yout system you can try
~~~~
povray -W720 -H680 -a [path to pov file]
~~~~
to render the .pov file a generate an image. Parameters -H -W and -a correspond to Width, heigh and antilaizing, respectively.
