pragma circom 2.1.9;

include "circomlib/circuits/poseidon.circom";

template LongPoseidon(len) {
    signal input inputs[len];
    signal output out;

    if (len <= 2){
        component H = Poseidon(len);
        for (var i = 0; i < len; i += 1){
            H.inputs[i] <== inputs[i];
        }
        out <== H.out;
    }
    else {
        component H = Poseidon(2);
        H.inputs[0] <== inputs[len-1];
        H.inputs[1] <== inputs[len-2];

        component LH = LongPoseidon(len-1);
        for (var i = 0; i < len-2; i += 1){
           LH.inputs[i] <== inputs[i]; 
        }
        LH.inputs[len-2] <== H.out;

        out <== LH.out;
    }
}

template Commit(len) {
    signal input in[len];
    signal input r;
    signal output out;

    component H = LongPoseidon(len+1);

    for (var i = 0; i < len; i += 1){
        H.inputs[i] <== in[i];
    }

    H.inputs[len] <== r;

    out <== H.out;
}
