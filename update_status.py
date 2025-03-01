import requests, json, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

NETWORKS = {
    "namada": {
        "indexer": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/mainnet/namada-indexers.json",
        "interface": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/mainnet/interfaces.json"
    },
    "housefire": {
        "indexer": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/testnet/housefire/namada-indexers.json",
        "interface": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/testnet/housefire/interfaces.json"
    }
}

def fetch_data(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException:
        return []

def get_indexer_version(url):
    try:
        r = requests.get(f"{url.rstrip('/')}/health", timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("version", "unavailable"), data.get("commit", "unavailable")
    except requests.exceptions.RequestException:
        return "unavailable", "unavailable"

def get_interface_version(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        s = BeautifulSoup(r.text, "html.parser")
        t = s.find("script", {"type": "module", "crossorigin": True})
        if not t or "src" not in t.attrs:
            return "unavailable"
        js_r = requests.get(f"{url.rstrip('/')}/{t['src'].lstrip('/')}", timeout=5)
        js_r.raise_for_status()
        match = re.search(r'version\$1\s*=\s*"([\d.]+)"', js_r.text)
        return match.group(1) if match else "unavailable"
    except requests.exceptions.RequestException:
        return "unavailable"

def update_status(network):
    status = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "network": network,
        "interface": [],
        "indexer": []
    }
    
    for key, url in NETWORKS[network].items():
        for item in fetch_data(url):
            component_url = item.get("Indexer API URL" if key == "indexer" else "Interface URL", "n/a")
            discord = item.get("Discord UserName", "n/a")
            team = item.get("Team or Contributor Name", "n/a")
            version, commit = get_indexer_version(component_url) if key == "indexer" else (get_interface_version(component_url), None)
            
            entry = {"team": team, "discord": discord, "url": component_url, "version": version}
            if commit:
                entry["commit"] = commit
            
            status[key].append(entry)

    with open(f"status_{network}.json", "w") as f:
        json.dump(status, f, indent=4)

if __name__ == "__main__":
    for net in NETWORKS:
        update_status(net)
