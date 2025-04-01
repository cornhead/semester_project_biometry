import pandas as pd
import sys

REQUIRED_CSV_HEADERS = [
    'vector length',
    'optimization',
    'lin. constr.',
    'non-lin. constr.',
    'P time',
    'V time'
]

def eprint(*args, **kwargs):
    '''
    Print an error message to stderr. (Simple wrapper around print())
    '''
    print(*args, file=sys.stderr, **kwargs)

def usage():
    '''
    Print a usage message to describe how to use the script.
    The message is printed to stderr.
    At the end, the function terminates the execution with exit code 1.
    '''

    eprint(f'Usage: {sys.argv[0]} <filename>')
    eprint()
    eprint('The filename must point to a CSV file with the following header:')
    eprint(f'\t{";".join(REQUIRED_CSV_HEADERS)}')
    eprint()
    eprint(f'The output of the script is printed to stdout.')
    eprint(f'The script produces LaTeX code for a tabular with')
    eprint(f'the code from the benchmarking.')
    sys.exit(1)

def parse_cli_params(argv):
    '''
    Takes the script arguments (argv) and parses them.
    Exactly one argument is expected, which is interpreted as filename.
    On error, the function prints the usage message and terminates execution.
    '''

    if len(argv) != 2:
        eprint(f'Exactly one argument required,  {len(argv)} given.')
        usage()

    filename = argv[1]

    return filename

def check_df_header(df:pd.DataFrame):
    '''
    Takes a pandas data frame and checks that it contains all required headers.
    Otherwise, the function prints the usage message and terminates execution.
    '''

    headers = df.columns.values.tolist()
    # eprint('debug: ', headers)
    for req in REQUIRED_CSV_HEADERS:
        if req not in headers:
            eprint(f'Couldn\'t find required header "{req}" in headers of provided CSV file.')
            usage()

def df_to_tabular(df:pd.DataFrame):
    '''
    Takes a pandas data frame that contains all required headers (cf. `REQUIRED_HEADERS`)
    and compiles the data to a LaTeX tabular.
    '''

    mystr = ''

    # --------- prologue ---------

    mystr += '\\begin{tabular}{rrrrrr}\n'
    mystr += '\t\\multicolumn{6}{l}{\large\\textbf{Your title goes here}}\\\\\n'
    mystr += '\t\\toprule\n'
    mystr += '\t$n$ & \\makecell{Compilation\\\\Flags} & \\makecell{Linear\\\\Constraints} & \\makecell{Non-Linear\\\\Constraints} & \\makecell{Prover\\\\Time [s]}  & \\makecell{Verifier\\\\Time [ms]} \\\\\n'
    mystr += '\t\\midrule\n'

    # --------- main part --------

    previous_vlen = None

    for i in range(len(df)):
        current_row = list(df.take([i]).values[0])
        # print(current_row)

        str_beginning = '\t'
        str_ending = ' \\\\'

        if current_row[0] != previous_vlen:
            colspan = 0
            for j in range(i,len(df)):
                if df['vector length'].iloc[j] != current_row[0]:
                    break
                colspan += 1

            str_beginning += f'\\multirow{{2}}{{*}}{{' + f'{current_row[0]:,}'.replace(',', ' ') + '}'
        else:
            str_ending += '[0.75em]'


        mystr += \
            str_beginning + \
            f'&{current_row[1].replace("--", "-{}-")} & ' + \
            f'{current_row[2]:,} & '.replace(',', ' ') + \
            f'{current_row[3]:,} & '.replace(',', ' ') + \
            f'{current_row[4]/1000:,.3f} & '.replace(',', ' ') + \
            f'{int(current_row[5])}' + \
            str_ending + '\n'

        previous_vlen = current_row[0]


    # ---------- epilogue ----------

    mystr += '\t\\bottomrule\n'
    mystr += '\\end{tabular}'

    return mystr

def main(argv):
    '''
    Main function of the program.
    Takes the CLI arguments (argv) with a filename
    and tries to compile the CSV file under the specified filename
    to LaTeX tabular.
    '''


    filename = parse_cli_params(argv)

    df = pd.read_csv(filename, sep=';')
    check_df_header(df)

    mystr = df_to_tabular(df)

    print(mystr)


if __name__ == '__main__':
    main(sys.argv)
