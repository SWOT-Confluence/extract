# Standard imports
import logging
from os import scandir
from pathlib import Path
from time import time

# Third party imports
from mpi4py import MPI

# Local imports
from app.config import extract_config
from app.Extract import Extract

'''Runs extract program using input and output directories specified
in 'config.py' file.'''

COMM = MPI.COMM_WORLD

def run(input_dir, output_dir):
    """Run extract using MPI where a range of basins is handled by each process."""

    rank = COMM.Get_rank()

    if rank == 0:
        print("Extracting and calculating data for directory:", 
            "\n\t", input_dir)
    
    # Create a dictionary of all ranks assigned to a range of basin directories
    dir_dict = {}
    if rank == 0:
        dir_dict = get_dir_dict(input_dir)
      
    # Send data dictionary to all processes to calculate SWOT and SWORD data
    dir_dict = COMM.bcast(dir_dict, root=0)

    # Create a logger for each rank
    rank_logger = create_rank_log(rank)
    
    # Run extract on dir_dict passing input based on rank
    print("Processing for rank number:", rank)
    extract = Extract(dir_dict[rank], output_dir, rank_logger)
    extract.extract_data()

    COMM.barrier()
    if rank == 0:
        print("Processing complete. Reach files can be found in directory:", 
            "\t\n", output_dir)

def get_dir_dict(input_dir):
    """Creates a dictionary of rank keys with a directory list value."""
    
    dir_dict = {}
    with scandir(input_dir) as entries:
        all_dir_list = [Path(entry.path) for entry in entries]
    
    # Divide directory list up evenly and deal with any remainders
    total_dirs = len(all_dir_list)
    size = COMM.Get_size()
    dirs_per_rank = total_dirs // size
        
    # Create a dictionary to send to each process with a key of rank
    dir_count = 0
    for i in range(size):
        start = dir_count
        end = dir_count + dirs_per_rank
        dir_dict[i] = all_dir_list[start:end]
        dir_count += dirs_per_rank

    # Spread remaining directories over processes
    if total_dirs % size != 0:
        remaining = total_dirs - dir_count
        i = 0
        for j in range(remaining):
            dir_dict[i].append(all_dir_list[dir_count])
            dir_count += 1
            i = 0 if i == (size - 1) else i + 1

    total_basins = 0
    for key,value in dir_dict.items():
        basin_count = 0
        for element in value:
            basin_count += 1
        total_basins += basin_count
        print(key, "\tbasin count", basin_count)
    print("Total basins", total_basins, "\n")

    return dir_dict

def create_rank_log(rank):
    """Creates a file logger for each rank to log to."""

    # Create a Logger object and set log level
    rank_logger = logging.getLogger(__name__)
    rank_logger.setLevel(logging.DEBUG)

    # Create a handler to file and set level
    filename = f"{extract_config['logging_dir']}/{rank}.log"
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handler
    file_format = logging.Formatter("%(asctime)s - %(threadName)s - "
        + "%(module)s - %(levelname)s : %(message)s")
    file_handler.setFormatter(file_format)

    # Add handlers to logger
    rank_logger.addHandler(file_handler)

    # Return logger
    return rank_logger

if __name__ == "__main__":
    start = time()
    input_dir = Path(extract_config["input_dir"])
    output_dir = Path(extract_config["output_dir"])
    run(input_dir, output_dir)
    COMM.barrier()
    end = time()
    if (COMM.Get_rank() == 0):
        print("Total processing time:", end - start)
