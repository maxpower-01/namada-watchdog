# 🟡 namada-watchdog
This repository is an effortless status tracker for the Namada ecosystem. It continuously monitors key components. The repository is divided into two main ideas of monitoring. All data is sourced from [Namada Ecosystem](https://github.com/Luminara-Hub/namada-ecosystem/).

| Namadillo | Repository |
|-|-|
| Shows the operational function of the Namada Interface (Namadillo). | Shows and tracks the deployed version of Namada infrastructure. |

## 📖 Components
- [Namada Interface (Namadillo)](https://github.com/anoma/namada-interface)
- [Namada Indexer](https://github.com/anoma/namada-indexer)
- [Namada MASP Indexer](https://github.com/anoma/namada-masp-indexer)
- [Namada](https://github.com/anoma/namada)

# Namadillo

**Versions and health status** of essential services required for the Namada Interface (Namadillo) to function.  

Not all Namadillo services are necessarily operated by the same contributor or hosting provider. Namadillo can be cross-connected to different services to retrieve the required data.

The latest releases section provides an overview of the most recently published versions of various services, such as the Namada Interface, Indexers, and other core components. Operators follow the latest approved and tested CometBFT version specifically for Namada rather than the most recently released one.  

The information shows the Namadillo version in use, the backend services it connects to, and the latest block height recorded at capture time. This helps provide an overview of which Namadillo instances are up-to-date and operational. The data includes **Namada mainnet** and the permanent testnet chain, **Housefire testnet**.  

The status indicators are classified as follows:
- 🟢 Version is up to date or block height is current.
- 🟡 Version is outdated or block height is slightly behind.
- 🔴  The service is unreachable or block height is too far behind.

*A grace period is in place to accommodate script execution delays.*

**This file does not promote any specific operator, interface, or service. The evaluated data is sourced from the Namada Ecosystem repository, which Luminar maintains.**

| JSON | Markdown |
|-|-|
| [interface.json](interface.json) | [INTERFACE.md](INTERFACE.md) |  

# Repository
Lightweight status tracker for the **Namada Ecosystem**. It monitors key components, with results stored in this repository. Currently tracking: Namada Interface, Namada Indexer, Namada MASP Indexer.

The [undexer](https://github.com/hackbg/undexer) currently doesn't provide a version API endpoint. You can follow the progress of a feature request here: [feat: add service version and new endpoint /health endpoint](https://github.com/hackbg/undexer/issues/19).

| JSON | Markdown |
|-|-|
| [status.json](status.json) | [STATUS.md](STATUS.md) |  
