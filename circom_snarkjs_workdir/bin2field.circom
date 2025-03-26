pragma circom 2.1.9;

template bin2field(len) {
    signal input in[len];
    signal output out;

    var lin_constraint = 0;
    for (var i = 0; i < len; i += 1){
        in[i] * (1-in[i]) === 0; // enforce binarity
        lin_constraint += in[i] * 2**i; // accumulate integer
    }

    out <== lin_constraint;
}
