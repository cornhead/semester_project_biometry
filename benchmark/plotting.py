import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sys
import os
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import ScalarFormatter
import io
import yaml

OPTIONS = [
     {
        'options': ['--help', '-h'],
        'needs_parameter': False,
        'maps_to': 'help',
        'description': 'Prints this message'
    },
    {
        'options': ['--output', '-o'],
        'needs_parameter': True,
        'maps_to': 'output_file',
        'description': 'Set an output file to write the plot to. I\n\t\t\tIf not specified, the plot is shown on display.'
    },
    {
        'options': ['--plot', '-p'],
        'needs_parameter': True,
        'maps_to': 'metric_to_plot',
        'description': 'Defines which column to plot against $n$'
    },
    {
        'options': ['--O2', '-O2'],
        'needs_parameter': False,
        'maps_to': 'only_O2',
        'description': 'If specified, only datapoints with optimizaion --O2 are plotted.'
    },
    {
        'options': ['--title', '-t'],
        'needs_parameter': True,
        'maps_to': 'title',
        'description': 'Sets the title of the plot'
    },
]

OPTIONS_DICT = { o:opt for opt in OPTIONS for o in opt['options'] }

def eprint(*args, **kwargs):
    '''
    Print an error message to stderr. (Simple wrapper around `print()`)
    '''
    print(*args, file=sys.stderr, **kwargs)

def die(*args, **kwargs):
    eprint(*args, **kwargs)
    sys.exit(1)

def usage(*args, **kwargs):
    if len(*args) > 0:
        eprint(*args)

    eprint(f'Usage: {sys.argv[0]} [Options] <plot decription file>')
    eprint()
    eprint('Options:')
    for opt in OPTIONS:
        eprint(f'\t{", ".join(opt["options"])}\t{opt["description"]}')

    eprint()
    eprint('Plot Description File:')
    eprint('\tThe plot description file is a yaml file that allows the user')
    eprint('\tto specifiy options for the plot and set input files.')
    eprint('\t')
    eprint('\tThe format is as follows:')
    eprint('\t\tplot_options: <dict of options for plot>')
    eprint('\t\tinput_files: <list of input file descriptions>')
    eprint('\t')
    eprint('\tThe list of options for the plot can contain, e.g.:')
    eprint('\t\ttitle')
    eprint('\t')
    eprint('\tEach input file description needs to contain at')
    eprint('\tleast the following parameters:')
    eprint('\t\tdescription')
    eprint('\t\tpath')
    eprint('\t\tcolumn')

    sys.exit(1)


def look_up_cli_argument(arg) -> str:
    if arg not in OPTIONS_DICT.keys():
        usage(f'Unable to parse option "{arg}"')

    opt = OPTIONS_DICT[arg]

    return opt


def parse_cli_arguments(argv) -> dict:
    config  = {}

    l = len(argv)

    # ------ find first input file ------

    first_input_idx = -1
    for i in range(l-1, 0, -1):
        if argv[i].startswith('-'):
            opt = look_up_cli_argument(argv[i])
            first_input_idx = ( i+2 if opt['needs_parameter'] else i+1)
            break

    if first_input_idx < 0:
        if l < 2:
            usage('No input files specified.')
        else:
            first_input_idx = 1

    if first_input_idx >= l:
        usage('No input files specified.')

    # ------- parse options --------

    skip_next = False

    for i in range(1, first_input_idx):
        if skip_next:
            skip_next = False
            continue

        opt = look_up_cli_argument(argv[i])

        if opt['needs_parameter']:
            config[opt['maps_to']] = argv[i+1]
            skip_next = True
        else:
            config[opt['maps_to']] = True

    # --------- parse input files -----

    if first_input_idx != l-1:
        usage(f'Expected exactly one iput file, got {l-first_input_idx}.')

    config['input_file'] = argv[first_input_idx]

    return config

def check_yaml(yml:dict):
    # print(yml)

    if 'plot_options' not in yml or 'input_files' not in yml:
        eprint('The input yml file must contain at least the following entries:')
        eprint('\tplot_options')
        eprint('\tinput_files')
        sys.exit(1)

    if not isinstance(yml['plot_options'], dict):
        die('Error in input yml file: "plot_options" must be a dictionary')

    if not isinstance(yml['input_files'], list):
        die('Error in input yml file: "input_files" must be a list')

    for in_f in yml['input_files']:
        if not isinstance(in_f, dict):
            die('Error in input yml file: each "input_files" entry must be a dict')

        required_fields = ['description', 'path', 'column']

        for rf in required_fields:
            if rf not in in_f.keys():
                die(f'Error in input yml file: One of the "input_files" entries is missing the required "{rf}" field')


def draw_plot(df:pd.DataFrame, column_to_plot:str, description:str, **kwargs):

    ax = sns.lineplot(
        data=df,
        x='vector length',
        y=column_to_plot,
        errorbar=None,
        **kwargs
    )

    ax.text(df['vector length'].max(), df[column_to_plot].iloc[-1], description)

if __name__ == '__main__':
    config = parse_cli_arguments(sys.argv)
    if 'help' in config:
        usage()

    # print(config)


    try:
        with open(config['input_file']) as f:
            yml = yaml.safe_load(f)
    except FileNotFoundError:
        die(f'Unable to open file "{config["input_file"]}"')

    check_yaml(yml)

    plt_opts = yml['plot_options']

    plt.figure(figsize=(10, 5))
    ax = plt.axes()
    ax.set_facecolor((0.9, 0.9, 0.9))
    plt.grid(visible=True, which="major", ls="-", color="white", axis='y', lw=1)
    plt.title(plt_opts['title'], loc='left', fontdict=plt_opts['font_title'])
    plt.xlabel(plt_opts['x_label'], fontdict=plt_opts['font_axis'])
    ax.ticklabel_format(style='plain')
    ax.set_xticks( [2**x for x in [5] + list(range(10,16))])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    for in_f in yml['input_files']:
        desc = in_f['description']
        path = in_f['path']
        column = in_f['column']

        del in_f['description']
        del in_f['path']
        del in_f['column']

        df = pd.read_csv(path, sep=';')

        if 'only_O2' in config.keys():
            df = df[ df['optimization'] == '--O2' ]

        if 'y_scaling' in plt_opts:
            df[column] *= plt_opts['y_scaling']

        draw_plot(df, column_to_plot=column, description=desc, **in_f)

    plt.ylabel('')

    if 'output_file' in config.keys():
        plt.savefig(config['output_file'], orientation='landscape',  dpi=500)
    else:
        plt.show()
