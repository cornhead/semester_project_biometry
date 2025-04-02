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

def usage():
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
        eprint(f'Unable to parse option "{arg}"')
        usage()

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
            eprint('No input files specified.')
            usage()
        else:
            first_input_idx = 1

    if first_input_idx >= l:
        eprint('No input files specified.')
        usage()

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
        eprint(f'Expected exactly one iput file, got {l-first_input_idx}.')
        usage()

    config['input_file'] = argv[first_input_idx]

    return config

def check_yaml(yml:dict):
    print(yml)

def draw_plot(data:pd.DataFrame, metadata:dict[str], plot_function:str):
    y_col = ('cycles' if plot_function == 'cylces' else 'P(n)')
    ax = sns.lineplot(
        data=data,
        x='n',
        y=y_col,
        estimator='median',
        **metadata['plot_kwargs']
    )

    ax.text(data['n'].max(), data[y_col].iloc[-1], metadata['tag'], **metadata['tag_kwargs'])

if __name__ == '__main__':
    config = parse_cli_arguments(sys.argv)
    if 'help' in config:
        usage()

    print(config)


    try:
        with open(config['input_file']) as f:
            yml = yaml.safe_load(f)
    except FileNotFoundError:
        eprint(f'Unable to open file "{config["input_file"]}"')
        sys.exit(1)

    check_yaml(yml)



    # title = "Performance [Ops/Cycle]" if config['plot function'] == 'performance' else 'Execution Time [Cycles]'
    # x_label = "Image Size [Pixels]"

    # font_title = {
    #     'weight': 'bold',
    #     'size': 14
    # }

    # font_axis = {
    #     'family': 'serif',
    #     'size': 11
    # }

    # plt.figure(figsize=(10, 5))
    # ax = plt.axes()
    # ax.set_facecolor((0.9, 0.9, 0.9))
    # plt.grid(visible=True, which="major", ls="-", color="white", axis='y', lw=1)
    # plt.title(title, loc='left', fontdict=font_title)
    # plt.xlabel(x_label, fontdict=font_axis)
    # ax.ticklabel_format(style='plain')
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)


    # for (md, d) in data:
    #     draw_plot(data=d, metadata=md, plot_function=config['plot function'])

    # plt.ylabel('')

    # if 'output file' in config:
    #     plt.savefig(config['output file'], orientation='landscape',  dpi=300)
    # else:
    #     plt.show()
