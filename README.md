# A zkSNARK for Biometric Finger Vein Recognition

As part of my semester project, I implement a zkSNARK for biometric finger vein recognition over commited finger vein patterns. As matching metric, the Miura metric is used. For implementation, [Circom](https://github.com/iden3/circom/tree/master) and [snarkJS](https://github.com/iden3/snarkjs) are used for rapid prototyping.

To ensure compatibility with across platforms and no need for homebrew installations, we use a Dockerfile written by [Saleel](https://github.com/saleel/circom-docker/).

Find further details in the report.

## Installation

The project was developed on Debian 12. Compatibility with other operating systems is not guaranteed.

Make sure you have the following software installed:

* `docker` (version 28.1.1), including the `docker-compose` plugin
* `python3` (version 3.11.2) including the following packages:

  * `pandas`
  * `numpy`
  * `matplotlib`
  * `seaborn`
  * `yaml`
  * `io`
  * `json`
* `node` (version 22.15.0) and `npm`

For the installation, follow these steps:

1. Clone the Git repository of this project from [https://github.com/cornhead/semester\_project\_biometry](https://github.com/cornhead/semester_project_biometry) to a folder of your choice. All paths in this instruction will be relative to this repository. That is, `./` refers to the root directory of the repository.

2. Additionally, download the file [https://storage.googleapis.com/zkevm/ptau/powersOfTau28\_hez\_final\_23.ptau](https://storage.googleapis.com/zkevm/ptau/powersOfTau28_hez_final_23.ptau) and place it in `./circom_snarkjs_workdir`.

3. Verify that docker works as intended by running the following command inside the root of the repository (`./`):

   ```bash
   docker compose run --remove-orphans -e N=16 -e CFLAGS=--O1 compile
   ```

   Depending on your docker installation and setup, you might need to run the command with root privileges.

4. Go to the directory `./node_app` and run the following command:

   ```bash
   npm install .
   ```

   This will install all required dependencies of the Node app.

5. Verify that the Node app works by running:

   ```bash
   node .
   ```

   inside `./node_app`. The output should be the usage message of the app.

6. Verify that the pattern generator works by running the following command inside `./patter_generator`:

   ```bash
   python3 pattern_generator.py test_pattern 8 5
   ```

   The output should look something like:

   ```json
   {"model": [0, 0, 0, 0, 0, 1, 1, 0], "probes": [[0, 0, 0, 0, 0, 0, 1, 0], [0, 1, 0, 0, 0, 0, 1, 0], [1, 1, 0, 0, 1, 1, 0, 1], [0, 1, 0, 1, 0, 1, 1, 1], [1, 1, 1, 1, 1, 1, 0, 1]], "miura": [0.3333333333333333, 0.25, 0.14285714285714285, 0.2857142857142857, 0.1111111111111111], "convolutions": [[0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 2, 1, 0, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0], [0, 1, 2, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0]]}
   ```

After this, the installation is complete.

## Benchmarking

To run the benchmarks, make sure that the input sizes in `./benchmark/benchmark.py` are set to the value/range you want and run the following command inside `./benchmark`:

```bash
python3 benchmark.py
```

Since the script calls `docker`, you might need to run the command with root privileges, depending on your `docker` installation.

The output is in CSV format and should look like:

```text
vector length;optimization;lin. constr.;non-lin. constr.;P time;V time
16;--O1;8769;7824;2591.3283281;21.986389699999698
16;--O2;0;7728;1585.5795218;26.524081699999783
32;--O1;17537;15648;4932.0203513;23.50202839999929
32;--O2;0;15456;2819.1961022000005;24.710246800000412
64;--O1;35073;31296;9018.771432099998;24.429017899998325
64;--O2;0;30912;5092.257819900001;21.409962400000857
128;--O1;70145;62592;16900.8351329;20.323507699998665
128;--O2;0;61824;9510.852032199999;22.720034600001053
```

If the CSV data is stored to a file, the data can be converted to a LaTeX `tabular` representation using the `csv_to_tabular.py` script. Assuming the data is stored in a file called `mydata.csv` in the `./benchmark` directory, run:

```bash
python3 csv_to_tabular.py mydata.csv
```

The output should look similar to:

```latex
\begin{tabular}{rrrrrr}
	\multicolumn{6}{l}{\large\textbf{Your title goes here}}\\
	\toprule
	$n$ & \makecell{Compilation\\Flags} & \makecell{Linear\\Constraints} & \makecell{Non-Linear\\Constraints} & \makecell{Prover\\Time [s]}  & \makecell{Verifier\\Time [ms]} \\
	\midrule
	\multirow{2}{*}{16}&-{}-O1 & 8 769 & 7 824 & 2.591 & 21 \\
	&-{}-O2 & 0 & 7 728 & 1.586 & 26 \\[0.75em]
	\multirow{2}{*}{32}&-{}-O1 & 17 537 & 15 648 & 4.932 & 23 \\
	&-{}-O2 & 0 & 15 456 & 2.819 & 24 \\[0.75em]
	\multirow{2}{*}{64}&-{}-O1 & 35 073 & 31 296 & 9.019 & 24 \\
	&-{}-O2 & 0 & 30 912 & 5.092 & 21 \\[0.75em]
	\multirow{2}{*}{128}&-{}-O1 & 70 145 & 62 592 & 16.901 & 20 \\
	&-{}-O2 & 0 & 61 824 & 9.511 & 22 \\[0.75em]
	\bottomrule
\end{tabular}
```

This code can be included in any LaTeX project that uses the `multirow` package.

To plot the CSV, use the script `plotting.py` in the `./benchmark` directory. The script requires a YAML file to describe how to plot what. Assume the existence of a file called `myplot.yml` with the following content:

```yaml
plot_options:
  title: "Prover Time [s]"
  x_label: "Image Size/Vector Length [Pixels]"
  y_scaling: 0.001

  font_title:
    weight: 'bold'
    size: 14

  font_axis:
    family: 'serif'
    size: 11

input_files:
  - description: "Base Implementation"
    path: "benchmark1_naive_poseidon_cascade.csv"
    column: "P time"
    marker: 'X'

  - description: "Optimization 1"
    path: "benchmark2_bit_packing.csv"
    column: "P time"
    marker: 'o'
```

Then, you can use a command like the following to create a plot of the CSV data and store it in `plot_prover_time.png`:

```bash
python3 plotting.py --plot "P time" --O2 -o plot\_prover\_time.png myplot.yml

```

If the `-o` option is omitted, the plot is shown but not automatically stored.

## Further Documentation

Almost all tools introduced so far provide more options and arguments for more fine-grained control of their behavior. To get an overview of their usage, call the scripts without any options or use the `--help` option to get the respective usage message.

For documentation on the internal workings, most scripts provide extensive documentation of their functions. This documentation can either be accessed from the source code directly, or compiled into an HTML or PDF document, using **Sphinx** for Python scripts.
