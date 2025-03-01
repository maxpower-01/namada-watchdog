# 🟡 namada-watchdog
Lightweight and effortless status tracker for the **Namada Ecosystem**. It continuously monitors key components, with results stored in this repository. Currently tracking:
- [namada-interface](https://github.com/anoma/namada-interface) (Namadillo)
- [namada-indexer](https://github.com/anoma/namada-indexer)
- *[namada-masp-indexer](https://github.com/anoma/namada-masp-indexer) soon...*

The [namada-masp-indexer](https://github.com/anoma/namada-masp-indexer) currently doesn't provide a version API endpoint. You can follow the progress here: [feat: add service version to /health endpoint #42](https://github.com/anoma/namada-masp-indexer/issues/42).

| Network | JSON | Markdown |
|-|-|-|
| 🚀 Namada Mainnet | [status_namada.json](status_namada.json) | [STATUS_namada.md](STATUS_namada.md) | 
| 🏠🔥 Housefire Testnet | [status_housefire.json](status_housefire.json) | [STATUS_housefire.md](STATUS_housefire.md) | 

## ⚙️ How It Works

- Twice a day, a GitHub Action runs the scripts:
  - `update_status.py`
  - `update_status_md.py`
- The action fetches the latest component lists from [Namada Ecosystem](https://github.com/Luminara-Hub/namada-ecosystem/).
- It queries component endpoints and compares versions with the latest official releases.
- The results are stored and **automatically updated** in this repository.
