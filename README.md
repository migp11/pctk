# tools4physicell
A set of scripts and utilities to analyze PhysiCell/hisyBoSS simulations

# Ready-to-run scripts

## Ploting time course: plot_time_course.py
The script plot_time_course.py plot number of cells vs time grouping cell by phase (alive, necrotic, apoptotic) <br>
The color mapping can be easily customized to represent other cell-agent variables (eg. color mutants or other cell states)
```usage: plot_time_course.py [-h] [--format {physicell,physiboss}]
                           [--figout FIG_FNAME] [--csvout CSV_FNAME]
                           data_folder```

## Generations of pov files for 3D rendering: povwriter.py
The script povwriter.py reads  <br>

