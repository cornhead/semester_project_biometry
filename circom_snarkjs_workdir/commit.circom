pragma circom 2.1.9;

include "circomlib/circuits/poseidon.circom";
include "bin2field.circom";

template LongPoseidon(len) {
    signal input inputs[len];
    signal output out;

    if (len <= 16){
        component H = Poseidon(len);
        for (var i = 0; i < len; i += 1){
            H.inputs[i] <== inputs[i];
        }
        out <== H.out;
    }
    else {
        component H = Poseidon(16);
        for (var i = 0; i < 16; i += 1){
            H.inputs[i] <== inputs[len-i-1];
        }

        component LH = LongPoseidon(len-15);
        for (var i = 0; i < len-16; i += 1){
           LH.inputs[i] <== inputs[i]; 
        }
        LH.inputs[len-16] <== H.out;

        out <== LH.out;
    }
}

template CommitToFieldElements(len) {
    signal input in[len];
    signal input r;
    signal output out;

    component H = LongPoseidon(len+1);
    for (var i = 0; i < len; i += 1){
        H.inputs[i] <== in[i];
    }
    H.inputs[len] <== r;

    H.out ==> out;
}

function ceil_div(a, b) {
    // Here, we basically re-implement the ceiling-division.
    // The backslash is integer division
    // and the percentage is modulo
    var res = a \ b;
    if (a % b != 0 ) {
        res += 1;
    }

    return res;
}

function min(a, b) {
    if (b < a) {
        return b;
    }

    return a;
}



template CommitToBits(len) {
    signal input in[len];
    signal input r;
    signal output out;

    // Since we are working over Z/pZ with
    // p = 21888242871839275222246405745257275088548364400416034343698204186575808495617,
    // we can pack up to floor(log(p))=253 bits into one field element
    var BITS_PER_FIELD_ELEMENT = 253;

    var num_field_elements = ceil_div(len, BITS_PER_FIELD_ELEMENT);

    signal field_elements[num_field_elements];
    component b2f[num_field_elements];

    for (var i = 0; i < num_field_elements; i += 1) {
        // compute how many bits, the current instance of bin2field should take in.
        // Either it's the maximum one instance can take, or it's the number of remaining bits.
        // Whatever is smaller.
        var len_this_instance = min( BITS_PER_FIELD_ELEMENT, len - i*BITS_PER_FIELD_ELEMENT ); 

        b2f[i] = bin2field(len_this_instance);

        for (var j = 0; j < len_this_instance; j += 1) {
            b2f[i].in[j] <== in[i*BITS_PER_FIELD_ELEMENT + j];
        }

        field_elements[i] <== b2f[i].out;
    }

    component ctf = CommitToFieldElements(num_field_elements);
    ctf.in <== field_elements;
    ctf.r <== r;
    ctf.out ==> out;
}

