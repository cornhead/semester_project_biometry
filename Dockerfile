# Original Author: "saleel" <saleel@saleel.xyz>
# Source: https://github.com/saleel/circom-docker/
# Date of Access: 23.02.2025

FROM rust:1.71.0 as circom-instaler
WORKDIR /
RUN git clone https://github.com/iden3/circom.git && \
    cd circom && \
    cargo build --release && \
    cargo install --path circom
RUN strip -g /usr/local/cargo/bin/circom \
  && echo "CARGO_VERSION='$(cargo --version)'" >> /etc/image-info \
  && echo "RUST_VERSION='$(rustc --version)'" >> /etc/image-info


FROM node:18.17.0
COPY --from=circom-instaler /usr/local/cargo/bin/circom /bin/
RUN npm install -g snarkjs@latest


# ----------- My Own Edit starts here ---------

WORKDIR /
ENTRYPOINT bash
