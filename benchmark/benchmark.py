import subprocess
import re

regex_circuit_info = re.compile(r'(linear constraints|non-linear constraints|wires): (\d+)')
regex_avg_times = re.compile(r'(Avg\. .* time):\s*([0-9\.]*) ms')

def execute_command(command):
    return subprocess.Popen(
        command.split(' '),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def set_key_files():
    execute_command('node ./node_app set_zkey_file ./circom_snarkjs_workdir/build/circuit_final.zkey')
    execute_command('node ./node_app set_vkey_file ./circom_snarkjs_workdir/build/verification_key.json')

'''
    n ... vector length
    cflags ... compilation flags for circom
    m ... number of test cases
'''
def benchmark_with_params(n:int, optimization:str, m:int=10):
    docker = execute_command(f'docker compose run --remove-orphans -e N={n} -e CFLAGS={optimization} compile')

    output = docker.stdout.read().decode()
    errormsg = docker.stderr.read().decode()

    print(output)
    print(errormsg)

    res = regex_circuit_info.findall(output)
    circuit_info = {key: int(value) for key, value in res}

    pattern_generator = subprocess.Popen(
        f'python3 pattern_generation/pattern_generator.py test_pattern {n} {m} > .tmp.mytestpattern.json',
        stderr=subprocess.PIPE,
        shell=True
    )

    errormsg = pattern_generator.stderr.read().decode()
    assert len(errormsg) == 0
    print(errormsg)


    node = execute_command('node ./node_app test .tmp.mytestpattern.json')

    output = node.stdout.read().decode()
    errormsg = node.stderr.read().decode()

    print(output)
    print(errormsg)

    res = regex_avg_times.findall(output)
    avg_times = {key: float(value) for key, value in res}

    print(avg_times)

    return (n, optimization, circuit_info['linear constraints'], circuit_info['non-linear constraints'], avg_times['Avg. prover time'], avg_times['Avg. verifier time'])

def benchmark_size(n:int):
    return [benchmark_with_params(n, opt) for opt in ['--O1', '--O2']]

if __name__=='__main__':
    set_key_files()

    res = [(16, '--O1', 8769, 7824, 2591.3283281, 21.986389699999698), (16, '--O2', 0, 7728, 1585.5795218, 26.524081699999783), (32, '--O1', 17537, 15648, 4932.0203513, 23.50202839999929), (32, '--O2', 0, 15456, 2819.1961022000005, 24.710246800000412), (64, '--O1', 35073, 31296, 9018.771432099998, 24.429017899998325), (64, '--O2', 0, 30912, 5092.257819900001, 21.409962400000857), (128, '--O1', 70145, 62592, 16900.8351329, 20.323507699998665), (128, '--O2', 0, 61824, 9510.852032199999, 22.720034600001053), (256, '--O1', 140289, 125184, 33031.91652639999, 20.404472900005203), (256, '--O2', 0, 123648, 18126.208784099996, 25.827575800007253)]

    for i in range(9, 10):
        n = 2**i
        res += benchmark_size(n)
        # print(res)

    print('vector length;optimization;lin. constr.;non-lin. constr.;P time; V time')

    for line in res:
        print(';'.join([str(val) for val in line]))
