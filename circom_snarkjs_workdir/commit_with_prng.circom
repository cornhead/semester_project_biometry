pragma circom 2.1.9;


template CommitToBits(len_input, len_randomness) {
    signal input in[len_input];
    signal input prng_stream[len_input+len_randomness];
    signal input r[len_randomness];
    signal output out;

    component ip = InnerProduct(len_input+len_randomness);

    for (var i = 0; i < len_input; i += 1){
        in[i]*(1-in[i]) === 0; // enforce binarity
        ip.in1[i] <== in[i];
    }

    for (var i = 0; i < len_randomness; i += 1){
        r[i]*(1-r[i]) === 0; // enforce binarity
        ip.in1[i+len_input] <== r[i];
    }

    ip.in2 <== prng_stream;

    out <== ip.out;
    
}
