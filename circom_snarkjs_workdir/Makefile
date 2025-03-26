.PHONY:clean
clean:
	rm -f circuit_0000.zkey circuit_0001.zkey circuit_0002.zkey challenge_phase2_0003 response_phase2_0003 circuit_0003.zkey

main.r1cs main.wasm: main.circom
	circom --r1cs --wasm $<

circuit_final.zkey: main.r1cs powersOfTau28_hez_final_23.ptau
	snarkjs groth16 setup $< $2 circuit_0000.zkey
	snarkjs zkey contribute circuit_0000.zkey circuit_0001.zkey --name="1st Contributor Name" -v
	snarkjs zkey contribute circuit_0001.zkey circuit_0002.zkey --name="Second contribution Name" -v -e="Another random entropy"
	snarkjs zkey export bellman circuit_0002.zkey  challenge_phase2_0003
	snarkjs zkey bellman contribute bn128 challenge_phase2_0003 response_phase2_0003 -e="some random text"
	snarkjs zkey import bellman circuit_0002.zkey response_phase2_0003 circuit_0003.zkey -n="Third contribution name"
	snarkjs zkey beacon circuit_0003.zkey $@ 0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f 10 -n="Final Beacon phase2"
	rm circuit_0001.zkey circuit_0002.zkey challenge_phase2_0003 response_phase2_0003 circuit_0003.zkey

verification_key.json: circuit_final.zkey
	snarkjs zkey export verificationkey $< $@
