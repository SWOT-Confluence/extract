# Third party imports
import pandas as pd
import shapefile as shp

"""extract utilities for working with matrices and data present in the different
test data files."""

def create_mean_series(df_dict):
    """Returns a Series of mean values over time for the dataframe dictionary parameter."""
    
    reach_dict = {}
    reach_dict = { key : value.mean(axis = 0) for key, value in df_dict.items() }

    return reach_dict

def create_reach_dict(df, topology, basin_num):
    """Creates a dictionary of dataframes with a key of reachid."""

    # Add topology index (reachid) and link columns
    df.insert(0, "reachid", topology.topo_data["reachid"])

    # Group by reachid, store dataframe in a dictionary organized by reachid
    df = list(df.groupby("reachid"))
    df_dict = { basin_num + '_' + element[0] : element[1] for element in df }

    # Remove reachid from dataframe value
    for value in df_dict.values():
        value.drop(labels = ["reachid"], axis = 1, inplace = True)
    
    return df_dict

def extract_node_data_txt(file, phrase, topology):
    """Extracts data for each node from file attribute for text files."""

    # Import stage data as a dataframe
    header_end = get_line_num(file, phrase) + 1
    data = pd.read_csv(file,
        skiprows = range(0, header_end), 
        header = None, 
        delim_whitespace = True)
    
    # Drop the time column and transpose matrix
    data.drop(0, inplace = True, axis = 1)
    data = data.transpose()

    # Add an explicit node identifier index
    data.insert(0, "nodeid", topology.topo_data.index.to_numpy())
    data = data.astype({"nodeid": str})
    data.set_index("nodeid", inplace = True)

    return data

def extract_node_data_shp(file, topology):
    """Extracts data for each node from file attribute for shapefiles."""

    data = None
    with shp.Reader(str(file)) as sf:

        # Get fields and records from shapefile and create a dataframe
        fields = [x[0] for x in sf.fields][1:]
        records = sf.records()
        data = pd.DataFrame(columns = fields, data = records)
        
        # Add an explicit node identifier index
        data.insert(0, "nodeid", topology.topo_data.index.to_numpy())
        data = data.astype({"nodeid": str})
        data.set_index("nodeid", inplace = True)

    return data

def get_line_num(filename, phrase):
    with open(filename, 'r') as f:
        for num, line in enumerate(f):
            if phrase in line:
                return num

