# TEMBA_FPV
Extension of TEMBA model to include floating photovoltaics (FPV) in the Eastern Nile Basin (ENB)

Original data and model from https://github.com/KTH-dESA/jrc_temba
This repository contains all the scripts and data necessary to reproduce the
work for JRC TEMBA project.

## Setup and Installation
To run this analysis you need to install GLPK and a solver such as CBC, CPLEX or Gurobi
You should also have Python >=3.6 environment setup with the following dependencies ideally
using miniconda so that snakemake can manage custom environments for each of the workflow tasks:

- `pandas`
- `xlrd`
- [`snakemake`](https://snakemake.readthedocs.io/en/stable/index.html)
- `plotly`
- `cufflinks-py`


## Running the TEMBA workflow
To run the workflow with snakemake, type the command `snakemake`.
To perform a dry run, use the flag `-n` and to run the workflow in parallel, use the flag `-j` and pass the (optional)
number of threads to use e.g. `snakemake -j 8`.

Note 1: the current version of the snakemake framework works on UBUNTU 20.04.6 LTS for Windows, using WSL 2

Note 2: the snakemake framework uses Gurobi as default solver. If you wish to run the model with another solver, use the commands in `run_analysis_cbc` or `run_analysis_cplex` text files

More information are contained in the `procedure.txt` file

## Folder structure
- Input data are stored in `.xlsx` Excel files in the `input_data` folder
- A modified OSeMOSYS model file is stored in `model` folder
- Temporary output data is stored in the `output_data` folder
- Final results are stored in `results`
- The scripts for intermediate processing are stored in the `scripts` folder or in the main folder
- The workflow for the scenario without FPVs is in the `NoFPV` folder
- Other data necessary for the pre and post processing are in the folders `HydroFPV_plants`, `LandValue`
- Relevant literature is in the `Literature` folder

Inìì
