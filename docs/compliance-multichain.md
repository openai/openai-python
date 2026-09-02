# Multi-Chain Deployment Compliance & Regulatory Review

This document provides a regulatory compliance analysis and technical integration guidelines for deploying Dogecoin nodes and Fantom integrations.

---

## 1. Regulatory Context & Asset Classification

Following the conclusion of the **SEC v. Ripple Labs** lawsuit, the classification of digital assets has become clearer:
- **Programmatic Sales & Secondary Markets:** The court ruled that programmatic sales of digital assets to retail buyers on secondary exchanges do not constitute investment contracts (securities).
- **Institutional Sales:** Direct, structured sales to institutional investors were ruled as securities offerings under the Howey Test.
- **Dogecoin (DOGE) Status:** Dogecoin is a pure proof-of-work cryptocurrency operating solely as a medium of exchange. It behaves identically to Bitcoin and is classified as a commodity rather than a security. Deploying and managing a local Dogecoin node carries low regulatory risk.
- **Fantom (FTM) Status:** Fantom uses a Proof-of-Stake (Lachesis consensus) mechanism. Due to its staking mechanics, developers must monitor potential SEC updates regarding PoS protocols. Staging interactions via private RPC endpoints (rather than public validator hosting) minimizes direct regulatory exposure.

---

## 2. Dogecoin Node Configuration & Health Checks

We run Dogecoin Core (`dogecoind`) in Docker using the configuration at `docker/dogecoin/Dockerfile`.

### Node CLI Commands
To check block sync status:
```bash
dogecoin-cli getblockchaininfo
```

To list peer connections:
```bash
dogecoin-cli getpeerinfo
```

---

## 3. Fantom RPC Integration Example

For interacting with Fantom Opera Mainnet, use `examples/fantom_integration.py` which wraps basic JSON-RPC operations.

```python
from examples.fantom_integration import FantomClient

client = FantomClient()
block = client.get_block_number()
print(f"Current block: {block}")
```
