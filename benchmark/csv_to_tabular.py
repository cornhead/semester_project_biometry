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
    eprint(f'Usage: {sys.argv[0]} filename')
    eprint()
    eprint('The filename must point to a CSV file with the following header:')
    eprint(f'\t{";".join(REQUIRED_CSV_HEADERS)}')
    sys.exit(1)

def parse_cli_params(argv):
    if len(argv) != 2:
        eprint(f'Exactly one argument required,  {len(argv)} given.')
        usage()

    filename = argv[1]

    return filename

def check_df_header(df:pd.DataFrame):
    headers = df.columns.values.tolist()
    # eprint('debug: ', headers)
    for req in REQUIRED_CSV_HEADERS:
        if req not in headers:
            eprint(f'Couldn\'t find required header "{req}" in headers of provided CSV file.')
            usage()

def df_to_tabular(df:pd.DataFrame):

    # --------- prologue ---------

    print('\\begin{tabular}{rrrrrr}')
    print('\t\\multicolumn{6}{l}{\large\\textbf{Your title goes here}}\\\\')
    print('\t\\toprule')
    print('\t$n$ & \\makecell{Compilation\\\\Flags} & \\makecell{Linear\\\\Constraints} & \\makecell{Non-Linear\\\\Constraints} & \\makecell{Prover\\\\Time [s]}  & \\makecell{Verifier\\\\Time [ms]} \\\\')
    print('\t\\midrule')

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


        print(
            str_beginning + \
            f'&{current_row[1].replace("--", "-{}-")} & ' + \
            f'{current_row[2]:,} & '.replace(',', ' ') + \
            f'{current_row[3]:,} & '.replace(',', ' ') + \
            f'{current_row[4]/1000:,.3f} & '.replace(',', ' ') + \
            f'{int(current_row[5])}' + \
            str_ending
        )

        previous_vlen = current_row[0]


    # ---------- epilogue ----------

    print('\t\\bottomrule')
    print('\\end{tabular}')

def main(argv):
    filename = parse_cli_params(argv)

    df = pd.read_csv(filename, sep=';')
    check_df_header(df)

    mystr = df_to_tabular(df)



if __name__ == '__main__':
    main(sys.argv)
