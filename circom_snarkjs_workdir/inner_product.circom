pragma circom 2.1.9;

template InnerProduct(len) {
    signal input in1[len];
    signal input in2[len];
    signal output out;

    signal intermediate[len];
    intermediate[0] <== in1[0]*in2[0];
    for (var i = 1; i < len; i += 1){
        intermediate[i] <== intermediate[i-1] + in1[i]*in2[i];
    }

    out <== intermediate[len-1];
}
