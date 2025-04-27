pragma circom 2.1.9;

include "miura.circom";
include "commit.circom";

template MainComponent(len) {
    signal input probe[len];
    signal input model[len];
    // signal input r_probe;
    signal input r_model;

    //signal output C_probe;
    signal output C_model;
    signal output miura_dividend;
    signal output miura_divisor;

    // component ComProbe = CommitToBits(len);
    // ComProbe.in <== probe;
    // ComProbe.r <== r_probe;
    // C_probe <== ComProbe.out;
    for (var i = 0; i < len; i += 1){
        probe[i] * (1-probe[i]) === 0; // enforce binarity
    }

    component ComModel = CommitToBits(len);
    ComModel.in <== model;
    ComModel.r <== r_model;
    C_model <== ComModel.out;

    component M = Miura_dividend_divisor_binary(len);
    M.a <== probe;
    M.b <== model;
    miura_dividend <== M.dividend;
    miura_divisor <== M.divisor;
}

component main  = MainComponent(16);
