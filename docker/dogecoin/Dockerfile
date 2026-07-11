# Stage 1: Download and prepare Dogecoin Core binary
FROM debian:12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV DOGECOIN_VERSION=1.14.8

RUN wget https://github.com/dogecoin/dogecoin/releases/download/v${DOGECOIN_VERSION}/dogecoin-${DOGECOIN_VERSION}-x86_64-linux-gnu.tar.gz \
    && tar -xzvf dogecoin-${DOGECOIN_VERSION}-x86_64-linux-gnu.tar.gz \
    && mv dogecoin-${DOGECOIN_VERSION}/bin/dogecoind /usr/local/bin/ \
    && mv dogecoin-${DOGECOIN_VERSION}/bin/dogecoin-cli /usr/local/bin/

# Stage 2: Optimized production runner
FROM debian:12-slim AS runner

# Create dedicated non-root user and group
RUN groupadd -r dogecoin && useradd -r -m -g dogecoin dogecoin

# Copy binaries from builder
COPY --from=builder /usr/local/bin/dogecoind /usr/local/bin/dogecoind
COPY --from=builder /usr/local/bin/dogecoin-cli /usr/local/bin/dogecoin-cli

# Run as non-root user
USER dogecoin
WORKDIR /home/dogecoin

# Set up configuration and data directories
RUN mkdir -p /home/dogecoin/.dogecoin

# Expose standard P2P and RPC ports
EXPOSE 9332 9333 19332 19333

# Copy configuration template
COPY dogecoin.conf.template /home/dogecoin/.dogecoin/dogecoin.conf

# Health check utilizing dogecoin-cli
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD dogecoin-cli getblockchaininfo || exit 1

ENTRYPOINT ["dogecoind"]
CMD ["-printtoconsole"]
