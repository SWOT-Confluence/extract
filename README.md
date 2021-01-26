# extract

Program that extracts UK data from input directory defined in `./app/config.py` and outputs two NetCDFs per reach one for SWOT attributes and one for SWORD of Science data. The output directory is also defined in `./app/config.py`.

Note: This program takes advantage of parallel processing in the calculation of slope data. Please enter the number of cores you wish to use in this calculation in the config file: `./app/config.py`.

# installation

1. Clone the repository to your file system.
2. extract is best run with Python virtual environments so install venv and create a virutal environment: https://docs.python.org/3/library/venv.html
3. Activate the virtual environment and use pip to install dependencies: `pip install -r requirements.txt`


# execution

Edit `./app.config.py` to specify where input data is stored on your file system and where you would like output data to be written to. Also include the number of cores you wish to use for parallel processing.

1. Activate your virtual environment.
2. Run `python3 run_extract.py`
3. Output is written to the directory you specified in the config file.