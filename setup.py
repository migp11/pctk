import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

root = os.path.dirname(os.path.realpath(__file__))
requirementPath = root + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="pctk",
    version="0.0.1",
    author="Miguel Ponce de Leon",
    author_email="miguel.ponce@bsc.es",
    description="PhysiCell ToolKit: a tool for handling MultiCellDS output from PhysiCell and PhysiBoSS simulations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PhysiBoSS/pctk",
    packages=setuptools.find_packages(where="src"   ),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['matplotlib', 'numpy', 'pandas', 'pytz', 'scipy', 'seaborn'],
    # install_requires=install_requires,
    entry_points={
        'console_scripts': ['plot-time-course=pctk.cmds.plot_time_course:main',
                            'write-pov-files=pctk.cmds.write_pov_files:main',
                            ]
        
    }
)
