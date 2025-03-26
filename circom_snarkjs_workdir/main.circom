pragma circom 2.1.9;

include "miura.circom";

template MainComponent(len) {
    signal input probe[len];
    signal input model[len];
    signal output miura_dividend;
    signal output miura_divisor;

    component M = Miura_dividend_divisor(len);
    M.a <== probe;
    M.b <== model;
    miura_dividend <== M.dividend;
    miura_divisor <== M.divisor;
}

component main  = MainComponent(9000);
