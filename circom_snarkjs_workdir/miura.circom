pragma circom 2.1.9;

include "inner_product.circom";


/*
@brief:
    computes the (non-binary) Miura metric of the two given inputs a,b and outputs the result as dividend and divisor
@detail:
    The inputs are of size len.
*/
template Miura_dividend_divisor(len) {
    signal input a[len];
    signal input b[len];
    signal output dividend;
    signal output divisor;

    component ab = InnerProduct(len);
    component aa = InnerProduct(len);
    component bb = InnerProduct(len);

    ab.in1 <== a;
    ab.in2 <== b;

    aa.in1 <== a;
    aa.in2 <== a;

    bb.in1 <== b;
    bb.in2 <== b;

    dividend <== ab.out;
    divisor <== aa.out+ bb.out;
}

/*
@brief:
    computes the (non-binary) Miura metric of the two given inputs a,b up to a certain number of decimal digits
@detail:
    The inputs are of size len.
    Since the computation of the metric consists of a divison with quotient between 0 and 0.5, the output consists of two values: a quotient and a remainder.
    The quotient is scaled with 10**precision, as specified, and all decimal digits are truncated.
    The remainder is computed as part of the witness computation, but its validity is not verified.
    IMPORTANT!: This means that the end user has to check himself that the remainder does not exceed    the divisor.
*/
template Miura(len, precision) {
    signal a[len];
    signal b[len];
    signal output miura_score;
    signal output miura_remainder;

    var scaling = 10**precision;

    component Mdd = Miura_dividend_divisor(len);
    Mdd.a <== a;
    Mdd.b <== b;


    miura_remainder <-- (Mdd.dividend*scaling) % Mdd.divisor; /* IMPORTANT this is only assigned, not verified */

    miura_score <-- (Mdd.dividend*scaling - miura_remainder) / Mdd.divisor;
    miura_score * Mdd.divisor === Mdd.dividend*scaling - miura_remainder;
}
