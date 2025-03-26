#! /usr/bin/env node

// needed because app is of type 'module' 
import { createRequire } from "module";
const require = createRequire(import.meta.url);

import { program }  from 'commander';
import chalk from 'chalk';
import storage from 'node-persist';
import {performance} from 'perf_hooks';

const snarkjs = require("snarkjs");
import fs from 'fs';

const max_r = 21888242871839275222246405745257275088548364400416034343698204186575808495617; // order of the bn128 curve

const wasm_file = "../circom_snarkjs_workdir/main_js/main.wasm";

storage.initSync();

program.version("1.0.0").description("A SNARK for proving matching finger vein patterns over committed data");

async function set_zkey_file(file_path) {
    storage.setItem('zkey_file', file_path);

    console.log( "Setting zkey file to " + file_path);
    console.log( chalk.green("Success"));
}

async function set_vkey_file(file_path) {
    storage.setItem('vkey_file', file_path);

    console.log( "Setting vkey file to " + file_path);
    console.log( chalk.green("Success"));
}

async function status(){
    console.log(chalk.yellow("Storage Status:") + "The following values are stored in persistant storage:" );
    var keys = await storage.keys();
    for (var i = 0; i < keys.length; i += 1){
        console.log("\t"+keys[i]+"\t"+ await storage.getItem(keys[i]));
    }
}

async function load_testpattern_file(file_path){
    var f = fs.readFileSync(file_path, 'utf8');
    var pattern = JSON.parse(f);
    return pattern;
}

async function extract_testcase_from_testpattern(mypattern, i){
    var model = mypattern.model;
    var pattern = mypattern.patterns[i];
    var miura = mypattern.miura[i];

    return {
        "model" : model,
        "pattern" : pattern,
        "miura" : miura
    };
}

async function init_game(){
    var pattern = await load_testpattern_file("../pattern_generation/patterns1.json");
    var testcase = await extract_testcase_from_testpattern(pattern, 3);


    var zkey_file = await storage.getItem('zkey_file');
    if (zkey_file == undefined){
        console.log(chalk.red("Error:") + "You first have to set a zkey file.");
        process.exit(1);
    }

    // Sample a random element `r` from Z_q (q = `max_r`)
    // ------------------------------------
    var r_model = Math.floor(Math.random() * max_r);
    var r_pattern = Math.floor(Math.random() * max_r);

    // Compute a dummy proof on input
    //     in_guess = [1, 1, 1, 1, ...]
    //     in_solution = color_sequence
    //     in_r = r
    // --------------------------------


    var input_json = {
        "model": testcase.model,
        "probe": testcase.pattern,
        "r_model": r_model,
        "r_probe" : r_pattern
    };

    const t0 = performance.now(); // https://developer.mozilla.org/en-US/docs/Web/API/Performance/now
    const { proof, publicSignals } = await snarkjs.groth16.fullProve( input_json, wasm_file, zkey_file);
    const t1 = performance.now();
    const prover_time = t1-t0;

    // Read the commitment from the public signals generated together with the proof
    // -----------------------------------------------------------------------------

    console.log(publicSignals);

    var commitment = publicSignals[0];

    // console.log(chalk.green("Color Sequence: ") + color_sequence);
    // console.log(chalk.green("Commitment: ") + commitment);
    console.log(chalk.green("Success"), "(Prover Time ", prover_time/1000, " sec.)");

    process.exit(0);
}

async function verify(proof_str, public_signals_str){
    var vkey_file = await storage.getItem('vkey_file');
    if (vkey_file == undefined){
        console.log(chalk.red("Error: ") + "You first have to set a vkey file.");
        process.exit(1);
    }

    var proof = JSON.parse(proof_str);
    var publicSignals = JSON.parse(public_signals_str);

    var vkey_path = await storage.getItem("vkey_file");
    const vKey = JSON.parse(fs.readFileSync(vkey_path));

    // Verify the proof using `vKey`, `publicSignals` and `proof`
    // ----------------------------------------------------------
    
    const res = await snarkjs.groth16.verify(vKey, publicSignals, proof);

    if (res === true) {
        console.log(chalk.green("Verification OK"));
        console.log(chalk.green("Number of correct positions: ") + publicSignals[1]);
        console.log(chalk.green("Commitment: ") + publicSignals[0]);
        console.log(chalk.yellow("(Don't forget to check that the commitment didn't change.)"));
        process.exit(0);
    } else {
        console.log(chalk.red("Invalid proof"));
        process.exit(1);
    }

}

program
    .command('set_zkey_file <file>')
    .description('Takes a path to the zkey file (circuit specific)')
    .action((file) => set_zkey_file(file))

program
    .command('set_vkey_file <file>')
    .description('Takes a path to the verification key file (circuit specific)')
    .action((file) => set_vkey_file(file))

program
    .command('init')
    .description('Initializes the game by setting the random color sequence and committing to it.')
    .action(() => init_game())

program
    .command('compute_proof <guess...>')
    .description('')
    .action((guess) => compute_proof(guess))

program
    .command('verify <proof> <publicSignals>')
    .description('takes a proof and public signals als stringified JSON objects and verifies the SNARK')
    .action((proof, publicSignals) => verify(proof, publicSignals))

program
    .command('status')
    .description('Prints the status of the persitant storage (e.g. file paths to prover and verifier keys)')
    .action((proof, publicSignals) => status())

program.parse()
