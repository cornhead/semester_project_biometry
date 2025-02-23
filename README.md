# A zkSNARK for Biometric Finger Vein Recognition

As part of my semester project, I implement a zkSNARK for biometric finger vein recognition over commited finger vein patterns. As matching metric, the Miura metric is used. For implementation, [Circom](https://github.com/iden3/circom/tree/master) and [snarkJS](https://github.com/iden3/snarkjs) are used for rapid prototyping.

To ensure compatibility with across platforms and no need for homebrew installations, we use a Dockerfile written by [Saleel](https://github.com/saleel/circom-docker/).


docker build -t circom_snarkjs:1.0.0 .
docker-compose run circom_snarkjs
