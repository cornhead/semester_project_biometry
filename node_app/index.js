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
    var probe = mypattern.probes[i];
    var miura = mypattern.miura[i];

    return {
        "model" : model,
        "probe" : probe,
        "miura" : miura
    };
}

async function test(file_path){
    const EPSILON = 0.000001;

    var pattern = await load_testpattern_file(file_path);
    var len = pattern.probes.length;

    var testcases_failed = 0;
    var prover_times = [];
    var verifier_times = [];
    
    for (var i = 0; i < len; i += 1){
        process.stdout.write("Running test case " + (i+1) + "/" + len + "...\r");

        var testcase = await extract_testcase_from_testpattern(pattern, i);

        var r_model = Math.floor(Math.random() * max_r);
        var r_probe = Math.floor(Math.random() * max_r);

        var input_json = {
            "model": testcase.model,
            "probe": testcase.probe,
            "r_model": r_model,
            "r_probe" : r_probe
        };

        var resP = await prove_internal(input_json);
        prover_times.push(resP.prover_time);

        var num = resP.public_signals[2];
        var den = resP.public_signals[3];
        var miura = num/den;

        if (Math.abs(miura-testcase.miura) > EPSILON) {
            testcases_failed += 1;

            console.log(chalk.red("Testcase Failed: "));
            console.log("\tTest case ", (i+1), "/", len, " failed because the Miura score was incorrect.");
            console.log("\tExpected ", testcase.miura, ", got ", num, "/", den, "=", miura);

            continue;
        }


        var resV = await verify_internal(resP.proof, resP.public_signals);
        verifier_times.push(resV.verifier_time);

        if (!resV.accept){
            console.log(chalk.red("FATAL ERROR:"));
            console.log("\tTest case ", (i+1), "/", len, " failed because the verifier did not accept the proof by the prover.");
            console.log("\t", resP.proof);

            process.exit(1);
        }

    }

    console.log(); // needed to go to next line after carriage return for progress indicator

    if (testcases_failed == 0){
        console.log(chalk.green("ALL TEST CASES PASSED"));
        
        var avg_prover_time = prover_times.reduce( (a,b) => a+b, 0) / len;
        var avg_verifier_time = verifier_times.reduce( (a,b) => a+b, 0) / len;
        console.log("Avg. prover time:   ", avg_prover_time, "ms");
        console.log("Avg. verifier time: ", avg_verifier_time, "ms");
    }
    else {
        console.log(chalk.red(testcases_failed, "/", len, " TEST CASES FAILED"));
    }

    process.exit( testcases_failed == 0 ? 1 : 0 );
}

async function prove_internal(input_json){
    var zkey_file = await storage.getItem('zkey_file');
    if (zkey_file == undefined){
        console.log(chalk.red("Error:") + "You first have to set a zkey file.");
        process.exit(1);
    }

    const t0 = performance.now(); // https://developer.mozilla.org/en-US/docs/Web/API/Performance/now
    const { proof, publicSignals } = await snarkjs.groth16.fullProve( input_json, wasm_file, zkey_file);
    const t1 = performance.now();
    const prover_time = t1-t0;

    // Read the commitment from the public signals generated together with the proof
    // -----------------------------------------------------------------------------


    var commitment = publicSignals[0];

    // process.exit(0);
    return {
        "proof" : proof,
        "public_signals" : publicSignals,
        "prover_time" : prover_time
    };
}

async function prove(file_path) {
    var f = fs.readFileSync(file_path, 'utf8');
    var input_json = JSON.parse(f);

    var res = await prove_internal(input_json);

    console.log(chalk.green("Public Signals: "), JSON.stringify(res.public_signals));
    console.log(chalk.green("Proof: "), JSON.stringify(res.proof));
    console.log(chalk.green("Success"), "(Prover Time ", res.prover_time/1000, " sec.)");
    
    process.exit(0);
}

async function verify_internal(proof, public_signals) {
    var vkey_file = await storage.getItem('vkey_file');
    if (vkey_file == undefined){
        console.log(chalk.red("Error: ") + "You first have to set a vkey file.");
        process.exit(1);
    }

    var vkey_path = await storage.getItem("vkey_file");
    const vKey = JSON.parse(fs.readFileSync(vkey_path));

    const t0 = performance.now();
    const res = await snarkjs.groth16.verify(vKey, public_signals, proof);
    const t1 = performance.now();
    const verifier_time = t1-t0;

    return {
        "accept" : (res === true),
        "verifier_time" : verifier_time
    };
}

async function verify(proof_str, public_signals_str){
    var proof = JSON.parse(proof_str);
    var public_signals = JSON.parse(public_signals_str);

    var res = await verify_internal(proof, public_signals);

    if (res.accept) {
        console.log(chalk.green("Verification OK"), "(Verifier Time: ", res.verifier_time/1000," sec.)");
        console.log(chalk.green("Miura Score: ") + public_signals[2]/public_signals[3]);
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
    .command('prove <file>')
    .description('Takes a JSON file with the input parameters to the circuit, computes the output of the circuit and provides a proof of correctness')
    .action((input) => prove(input))

program
    .command('test <file>')
    .description('Takes the path to a JSON file with test patterns and performs tests and benchmarkings')
    .action((file) => test(file))

program
    .command('verify <proof> <publicSignals>')
    .description('takes a proof and public signals as stringified JSON objects and verifies the SNARK')
    .action((proof, publicSignals) => verify(proof, publicSignals))

program
    .command('status')
    .description('Prints the status of the persitant storage (e.g. file paths to prover and verifier keys)')
    .action((proof, publicSignals) => status())

program.parse()
