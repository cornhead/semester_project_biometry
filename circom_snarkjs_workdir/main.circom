pragma circom 2.1.9;

include "miura.circom";
include "commit_with_prng.circom";


template MainComponent(len) {
    var len_randomness = 128;

    signal input probe[len];
    signal input model[len];
    signal input r_probe[len_randomness];
    signal input r_model[len_randomness];
    signal input prng_stream[len+len_randomness];

    signal output C_probe;
    signal output C_model;
    signal output miura_dividend;
    signal output miura_divisor;

    component ComProbe = CommitToBits(len, len_randomness);
    ComProbe.in <== probe;
    ComProbe.r <== r_probe;
    ComProbe.prng_stream <== prng_stream;
    C_probe <== ComProbe.out;

    component ComModel = CommitToBits(len, len_randomness);
    ComModel.in <== model;
    ComModel.r <== r_model;
    ComModel.prng_stream <== prng_stream;
    C_model <== ComModel.out;

    component M = Miura_dividend_divisor(len);
    M.a <== probe;
    M.b <== model;
    miura_dividend <== M.dividend;
    miura_divisor <== M.divisor;
}

component main {public [prng_stream]} = MainComponent(16);
