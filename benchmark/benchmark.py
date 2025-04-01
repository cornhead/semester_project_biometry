import subprocess
import re
import sys

regex_circuit_info = re.compile(r'(linear constraints|non-linear constraints|wires): (\d+)')
regex_avg_times = re.compile(r'(Avg\. .* time):\s*([0-9\.]*) ms')

def eprint(*args, **kwargs):
    '''
        Print an error message to stderr. (Simple wrapper around print())
    '''
    print(*args, file=sys.stderr, **kwargs)

def eprint_output_and_errormsg(output:str, errormsg:str):
    '''
        Takes the stdout and stderr of a subprocess and
        prints and prints it to stderr of the current process
        in a formatted way.
    '''

    eprint('----------------- STDOUT --------------')
    eprint(output)
    eprint('----------------- STDERR --------------')
    eprint(errormsg)
    eprint('---------------------------------------')

def execute_command(command:str, **kwargs):
    '''
        Takes a command as string and executes it in a subprocess.
        The stdout and stderr are available via pipes.
        Unless the keyword argument 'shell' is set to True, the command string
        will be split, as recommended in the documentation of the subprocess module

        :return: a reference to the subprocess
    '''

    if not 'shell' in kwargs or kwargs['shell'] == False:
        command = command.split(' ')

    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs
    )

def set_key_files():
    '''
        Calles the node app and specifies the paths to the  prover and
        verifier keys of the SNARK.
    '''
    execute_command('node ../node_app set_zkey_file ../circom_snarkjs_workdir/build/circuit_final.zkey')
    execute_command('node ../node_app set_vkey_file ../circom_snarkjs_workdir/build/verification_key.json')

def benchmark_with_params(n:int, optimization:str, m:int=10) -> tuple[int, str, int, int, float, float]:
    '''
        Takes parameters to run one test pattern (i.e. a set of multiple
        test cases of equal size) and executes the benchmarking.

        The following steps are taken:
            - Compile the circuit for size n using the given flags. (This is done via the docker-compose command 'compile'. A Makefile inside the Dockercontainer then takes care of everything.)
            - Generate a test pattern for size n with m test cases. For details, refer to the documentation of the pattern generator module
            - Call the node app for testing with the given test pattern. At the end, this will print the average prover and verifier time.

        The individual steps may produce output like information on the circuit size or execution times. This output is read and parsed using regular expressions.

        The output is a six-tuple containing the relevant metrics in the order:
            - vector length
            - optimization flags
            - number of linear constraints in the circuit
            - number of non-linear constraints in the circuit
            - average prover time (taken over all n test cases)
            - average verifier time (taken over all n test cases)

        :param n:  vector length
        :param cflags: compilation flags for circom (mostly just '--O1' or '--O2')
        :param m: number of test cases to be generated for this test pattern
        :return: a six-tuple of relevant metrics (see description above)
    '''
    docker = execute_command(f'docker compose run --remove-orphans -e N={n} -e CFLAGS={optimization} compile')
    output = docker.stdout.read().decode()
    errormsg = docker.stderr.read().decode()

    res = regex_circuit_info.findall(output)
    circuit_info = {key: int(value) for key, value in res}

    if len(circuit_info) == 0:
        eprint('Error: It looks like the circuit could not be compiled.')
        eprint('Here is the output of the compiler:\n')
        eprint_output_and_errormsg(output, errormsg)
        sys.exit(1)


    pattern_generator = execute_command(
        f'python3 ../pattern_generation/pattern_generator.py test_pattern {n} {m} > .tmp.mytestpattern.json',
        shell=True
    )
    errormsg = pattern_generator.stderr.read().decode()

    if len(errormsg) > 0:
        eprint('Error: Could not generate test pattern.')
        eprint('Here is the output of the pattern generator:\n')
        eprint_output_and_errormsg(output, errormsg)
        sys.exit(1)


    node = execute_command('node ../node_app test .tmp.mytestpattern.json')
    output = node.stdout.read().decode()
    errormsg = node.stderr.read().decode()

    if len(errormsg) > 0:
        eprint('Error: Could not run test pattern.')
        eprint('Here is the output of the node app:\n')
        eprint_output_and_errormsg(output, errormsg)
        sys.exit(1)

    res = regex_avg_times.findall(output)
    avg_times = {key: float(value) for key, value in res}

    if any( [kw not in avg_times for kw in ['Avg. prover time', 'Avg. verifier time']]):
        eprint('Error: Could not parse Avg. prover time or Avg. verifier time from output of node app.')
        eprint('Here is the output of the node app:\n')
        eprint_output_and_errormsg(output, errormsg)
        sys.exit(1)

    return (
        n,
        optimization,
        circuit_info['linear constraints'],
        circuit_info['non-linear constraints'],
        avg_times['Avg. prover time'],
        avg_times['Avg. verifier time']
    )

def main():
    '''
        Main Function of this Program.

        The following steps are taken:
            - Set the prover and verifier keys in the node app
            - For specified problem sizes, benchmark the circuit and store the result
            - print the results as CSV

        As soon as a one measurement is finished, its result will be printed to
        stdout, so that even in the case of later failure, the resulst so far
        are available. The output is in CSV format.
    '''

    print('vector length;optimization;lin. constr.;non-lin. constr.;P time;V time')

    set_key_files()

    benchmarks = []

    for i in range(4, 14):
        n = 2**i
        for opt in ['--O1', '--O2']:
            eprint(f'Benchmarking for size {n} with {opt}...\r', end='')
            res = benchmark_with_params(n, opt)
            print(';'.join([str(val) for val in res]))
            benchmarks += res

if __name__=='__main__':
    main()
