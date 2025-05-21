pragma circom 2.1.9;


template NTT(len) {
    signal input in[len];
    signal input nth_root; // primitive n-th root of unity where n=len
    signal output out[len];

    signal omegas[len];
    omegas[0] <== 1;
    for (var i = 1; i < len; i += 1){
        omegas[i] <== omegas[i-1] * nth_root;
    }

    if (len == 1){
        out <== in;
    }
    else{
        assert (len%2 == 0);
        assert (len < 2**28);

        component ntt_even = NTT(len\2);
        ntt_even.nth_root <== nth_root*nth_root;

        component ntt_odd = NTT(len\2);
        ntt_odd.nth_root<== nth_root*nth_root;

        for (var i = 0; i < len\2; i+=1){
            ntt_even.in[i] <== in[i*2];
            ntt_odd.in[i] <== in[i*2+1];
        }

        for (var i = 0; i < len\2; i+=1){
            out[i] <== ntt_even.out[i] + omegas[i]*ntt_odd.out[i];
            out[i+len\2] <== ntt_even.out[i] - omegas[i]*ntt_odd.out[i];
        }

    }
}
