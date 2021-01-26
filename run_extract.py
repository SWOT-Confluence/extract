# Standard imports
from pathlib import Path
from time import time

# Local imports
from app.config import extract_config
from app.Extract import Extract

'''Runs extract program using input and output directories specified
in 'config.py' file.'''

input_directory = Path(extract_config["input_dir"])
output_directory = Path(extract_config["output_dir"])

print("Extracting and calculating data for directory:", 
    "\n\t", input_directory)
start = time()
extract = Extract(input_directory, output_directory)
extract.extract_data()
end = time()
print("Processing complete. Reach files can be found in directory:", 
    "\t\n", output_directory)
print("Total processing time:", end - start)