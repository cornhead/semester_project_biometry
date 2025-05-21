pragma circom 2.1.9;

include "miura.circom";
include "commit.circom";
include "ntt.circom";

/*
@brief: takes a number and returns its bitlength (rounded up)
*/
function bitlength(num){
    var bits = 0;
    for (var tmp = num; tmp > 0; tmp >>= 1) {
        bits += 1;
    }
    return bits;
}

template ZeroExtend(n, m){
    signal input in[n];
    signal output out[m];

    for (var i = 0; i < n; i += 1){
        out[i] <== in[i];
    }

    for (var i = 0; i < m-n; i += 1){
        out[n+i] <== 0;
    }
}


template NTTextended(n, m){
    signal input in[n];
    signal input nth_root;
    signal output out[m];

    component ext = ZeroExtend(n, m);
    ext.in <== in;

    signal in_ext[m] <==  ext.out;

    component ntt = NTT(m);
    ntt.in <== in_ext;
    ntt.nth_root <== nth_root;
    
    out <== ntt.out;
}

template MainComponent(len) {
    signal input probe[len];
    signal input model[len];
    signal input r_model;

    signal output C_model;
    signal output miura_dividend;
    signal output miura_divisor;

    signal output conv[2*len];

    /* signal output ntt_model[len]; */
    /* signal output ntt_probe[len]; */
    /* signal output intt_model[len]; */
    /* signal output intt_probe[len]; */

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

    // -----------------
    var FIELD_P = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    assert ((FIELD_P-1) % (2**28) == 0);
    var GENERATOR = 5; // Found with sagemath: F=GF(FIELD_P); g = F.multiplicative_generator();
    var two_to_the_28_th_root = GENERATOR ** ((FIELD_P-1)/(2**28));

    var power = 28 - bitlength(len); // power x for when computing generator^2^x
    var nth_root_var = two_to_the_28_th_root ** (2**power);

    signal nth_root <== nth_root_var;

    signal nth_root_inverse <-- 1/nth_root;
    nth_root_inverse * nth_root === 1;

    /* signal root_intermediate[power+1]; */
    /* root_intermediate[0] <== GENERATOR_FOR_SUBFIELD; */
    /* for (var i = 1; i <= power; i += 1){ */
    /*     root_intermediate[i] <== root_intermediate[i-1]*root_intermediate[i-1]; */
    /* } */
    /* signal nth_root <== root_intermediate[power]; // (primitive) n-th root of unity where n=len */


    component ntt_p = NTTextended(len, 2*len);
    ntt_p.nth_root <== nth_root;
    ntt_p.in <== probe;
    signal ntt_probe[2*len] <== ntt_p.out;

    component ntt_m = NTTextended(len, 2*len);
    ntt_m.nth_root <== nth_root;
    ntt_m.in <== model;
    signal ntt_model[2*len] <== ntt_m.out;

    signal ntt_conv[2*len];
    for (var i = 0; i < 2*len; i += 1){
        ntt_conv[i] <== ntt_probe[i] * ntt_model[i];
    }

    component intt_conv = iNTT(2*len);
    intt_conv.nth_root_inverse <== nth_root_inverse;
    intt_conv.in <== ntt_conv;
    conv <== intt_conv.out;
}

component main  = MainComponent(16);
