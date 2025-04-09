DIR = ./build
CFLAGS = --O1
N = 16

.PHONY:all
all: build/verification_key.json

.PHONY:clean
clean:
	rm -rf build/

.PHONY:help
help:
	@echo "Available Targets:"
	@echo "  * all"
	@echo "  * clean"
	@echo "  * compile"
	@echo "  * setup"
	@echo "  * extract_vkey"
	@echo "  * targets"
	@echo ""
	@echo "Available Variables:"
	@echo "  * DIR    ... output directory, default: ./build"
	@echo "  * CFLAGS ... compiler flags, default: --O1"
	@echo "  * N      ... vector length, default: 16"


.PHONY:compile
compile: ${DIR}/main.r1cs

${DIR}/main.r1cs: main.circom
	mkdir -p ${DIR}
	head -n -1 main.circom > .tmp.main_${N}.circom
	@echo "component main {public [prng_stream]} = MainComponent(${N});" >> .tmp.main_${N}.circom
	circom --r1cs --wasm --sym -o ${DIR} ${CFLAGS} .tmp.main_${N}.circom
	rm .tmp.main_${N}.circom
	mv ${DIR}/.tmp.main_${N}.r1cs ${DIR}/main.r1cs
	mv ${DIR}/.tmp.main_${N}.sym ${DIR}/main.sym
	mv ${DIR}/.tmp.main_${N}_js/.tmp.main_${N}.wasm ${DIR}/.tmp.main_${N}_js/main.wasm
	mv ${DIR}/.tmp.main_${N}_js ${DIR}/main_js

.PHONY:setup
setup: ${DIR}/circuit_final.zkey

${DIR}/circuit_final.zkey: ${DIR}/main.r1cs powersOfTau28_hez_final_23.ptau
	snarkjs groth16 setup $^ ${DIR}/circuit_0000.zkey
	snarkjs zkey contribute ${DIR}/circuit_0000.zkey ${DIR}/circuit_0001.zkey --name="Contribution Name" -v -e="Another random entropy"
	snarkjs zkey beacon ${DIR}/circuit_0001.zkey $@ 0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f 10 -n="Final Beacon phase2"

.PHONY:extract_vkey
extract_vkey: ${DIR}/verification_key.json

${DIR}/verification_key.json: ${DIR}/circuit_final.zkey
	snarkjs zkey export verificationkey $< $@
