import numpy as np
import os.path
import pandas as pd
import dataframe_image as dfi


# Turns off annoying Pandas warning when setting a value across an column axis. As it's a warning and not an error
# it's OK to set this value
pd.options.mode.chained_assignment = None  # default='warn'

# Some constants
NORMAL = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
# Some common functions

# Will turn a csv file that exists into a Pandas Dataframe. Although we're just wrapping Pandas functionality
# it might be better as we can alter its functionality, for instance making sure the file exists

def csv_to_dataframe(filename, sep=","):
    """
    Call with just the name of the csv file or the name and separator type sep which defaults to ","
    """
    
    # Check the file exists - raise an exception if it doesn't
    if not os.path.exists(filename):
        raise Exception("Unable to find the  file {} for processing. Please check value you entered above".format(filename))
        
    # Call Pandas to do the heavy lifting
    df = pd.read_csv (filename, sep=sep)
    
    return df

# This method wraps a value with BOLD and NORMAL ASCII escape for convenience
def bold(val, int_fmt=":,", float_fmt=":.2f"):
    """
    Pass a value and it will return an escaped version to output the val in BOLD in a Print statment
    """
    fmt_str = "{}{}{}"
    
    if (type(val) == int) | (isinstance(val, np.int32)) | (isinstance(val, np.int64)):
        fmt_str = "{}{" + int_fmt + "}{}"
    
    if (type(val) == float) | (isinstance(val, np.float32)) | (isinstance(val, np.float64)):
        fmt_str = "{}{" + float_fmt + "}{}"

    return fmt_str.format(BOLD, val, NORMAL)

# This method wraps a value with UNDERLINE and NORMAL ASCII escape for convenience
def ul(val):
    """
    Pass a value and it will return an escaped version to output the val underlined in a Print statment
    """
    fmt_str = "{}{}{}"
    return fmt_str.format(UNDERLINE, val, NORMAL)

def add_value_labels(ax, spacing=1):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """

    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'
        
        # Don't label 0s
        if not y_value == 0:
            # If value of bar is negative: Place label below bar
            if y_value < 0:
                # Invert space to place label below
                space *= -1
                # Vertically align label at top
                va = 'top'

            # Use Y value as label and format number with one decimal place
            label = "{:.1f}".format(y_value)

            # Create annotation
            ax.annotate(
                label,                      # Use `label` as label
                (x_value, y_value),         # Place label at end of the bar
                xytext=(0, space),          # Vertically shift label by `space`
                textcoords="offset points", # Interpret `xytext` as offset in points
                ha='center',                # Horizontally center label
                va=va)                      # Vertically align label differently for
                                            # positive and negative values.

# Turn a list into a dictionary indexed from idx_offset
def list_to_indexed_dict(list, idx_offset=1):
    """
    Turns a list of values into an indexes dictionary starting from idx_offset (default 1)
    """
    # Create an empty dictionary
    ret_dict = {}
    # Loop through list
    for idx, value in enumerate(list):
        # Create index
        ret_dict[idx + idx_offset] = value
    # Return it
    
    
    return ret_dict

# Functions for the plotting functionality
def cmd_eq(command, function_name):
    return command.strip().lower() == function_name.lower()

def is_exit(command):
    return cmd_eq(command, "exit")

def set_column(command):
    return cmd_eq(command, "column")

def column_values(command):
    return cmd_eq(command, "column_values")

def data(command):
    return cmd_eq(command, "data")

def set_x(command):
    return cmd_eq(command, "x")
    
def set_y(command):
    return cmd_eq(command, "y")
    
def xy_values(command):
    return cmd_eq(command, "xy_values")
    
def print_plot(command):
    return cmd_eq(command, "plot")

def list(command):
    return cmd_eq(command, "list")

def help(command):
    return cmd_eq(command, "help")

def x_fig_size(command):
    return cmd_eq(command, "x_fig_size")

def y_fig_size(command):
    return cmd_eq(command, "y_fig_size")


def validate_x_y(var_x, var_y):
    # If var_x and var_y are valid then we'll return an empty String
    ret_var = ""
    
    if(var_x == ""):
        ret_var += "x is not set"

    if(var_y == ""):
        ret_var = "{}y is not set".format("" if ret_var == "" else (ret_var + " and "))

    return ret_var

def set_valid_var_val(var_name, var_val, new_var_val, lower_limit, upper_limit):
    # let's pass in the value we caught off the regex match
    valid_var_val = (new_var_val >= lower_limit) & (new_var_val <= upper_limit)

    if valid_var_val:
        var_val = new_var_val
        print("{} set to {}".format(var_name, bold(var_val)))
    else:
        if new_var_val == -1:
            print("**ERROR** - Please specify a value for {}".format(var_name))
        else:
            print("**ERROR** - {} can be {}-{}".format(var_name, lower_limit, upper_limit))
    
    return var_val

def capture_input(var_name, var_val, new_var_val, possible_values):
    
    # print("new_var_val:{}".format(new_var_val))
    valid_idx = (new_var_val in possible_values.keys())
    if valid_idx:
        var_val = possible_values[new_var_val]
        print("{} set to {}".format(var_name, bold(var_val)))
    else:
        if new_var_val == -1:
            print("**ERROR** - Please specify a value for {}".format(var_name))
        else:
            print("**ERROR** - Index value {} not found in {}, please choose again".format(new_var_val, possible_values))
    return var_val


def save_text(text, path, name, add_rmd_nl=True, save_artefacts=False):
    """
    Saves text to a directory, creating that directory if needed
    Default is not to save, override by passing save_artefacts=True
    """
    if save_artefacts:
        

        if os.path.isdir(path) == False:
            os.makedirs(path)
        
        # Create out file path and name
        file_path_name = "{}/{}".format(path,name)

        with open(file_path_name, "w", encoding='utf-8') as f:
            if add_rmd_nl:
                text = "```\n" + text + "\n```\n"
                # re.sub("\\n", " \\\n", text)
            
            f.write(text)
            
def save_plot(plot, path, name, save_artefacts=False):
    """
    Saves a plot to a directory, creating that directory if needed
    Default is not to save, override by passing save_artefacts=True
    """
    if save_artefacts:
    # Create any directory needed
        if os.path.isdir(path) == False:
            os.makedirs(path)
    
    # Create out file path and name
    file_path_name = "{}/{}".format(path, name)

    save_plot_filename(plot = plot, filename=file_path_name, save_artefacts=save_artefacts)
    
def save_plot_filename(plot, filename, save_artefacts=False):
    """
    Saves a plot to a file, assumes path to file already exists
    """
    if save_artefacts:
        # Remove it if it's already there
        if os.path.isfile(filename):
           os.remove(filename)
        
        # Save it
        try:
            plot.get_figure().savefig(filename, dpi=100, bbox_inches = 'tight')
        except:
            plot.savefig(filename, dpi=100, bbox_inches = 'tight')

def save_df(df, path, name, save_artefacts=False, max_rows=None):
    """
    Saves a dataframe to a directory, creating that directory if needed
    Default is not to save, override by passing save_artefacts=True
    """
    if save_artefacts:
        # Create any directory needed
        if os.path.isdir(path) == False:
            os.makedirs(path)
        
        # Create out file path and name
        file_path_name = "{}/{}".format(path, name)

        # Remove it if it's already there
        if os.path.isfile(file_path_name):
           os.remove(file_path_name)
        
        # Save it
        if max_rows is not None:
            dfi.export(df, file_path_name, max_rows=max_rows)
        else:
            dfi.export(df, file_path_name)
