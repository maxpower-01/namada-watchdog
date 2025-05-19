import requests, json, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# Start time
START_TIME = datetime.now(timezone.utc).isoformat() + "Z"

# Configuration URLs
NETWORKS = {
    "namada": {
        "indexer": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/mainnet/namada-indexers.json",
        "masp": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/mainnet/masp-indexers.json",
        "interface": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/mainnet/interfaces.json"
    },
    "housefire": {
        "indexer": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/testnet/housefire/namada-indexers.json",
        "masp": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/testnet/housefire/masp-indexers.json",
        "interface": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/testnet/housefire/interfaces.json"
    }
}

LATEST_VERSIONS = {
    "interface": "https://api.github.com/repos/anoma/namada-interface/releases",
    "indexer": "https://api.github.com/repos/anoma/namada-indexer/tags",
    "masp": "https://api.github.com/repos/anoma/namada-masp-indexer/tags",
    "namada": "https://api.github.com/repos/anoma/namada/tags"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Fetch JSON data from URL
def fetch_json(url):
    try:
        r = requests.get(url, timeout=5, headers=HEADERS)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException:
        return {}

# Fetch latest versions from GitHub
def fetch_latest_versions():
    def extract_numeric_version(v):
        # Extracts the leading numeric version part (e.g., "1.2.3-hotfix2" -> [1,2,3])
        base = v.split('-')[0]
        parts = base.split('.')
        return [int(p) if p.isdigit() else 0 for p in parts]

    latest_versions = {}
    for key, url in LATEST_VERSIONS.items():
        releases = fetch_json(url)

        if key == "interface":
            versions = [
                re.sub(r"namadillo@v", "", r.get("tag_name", ""))
                for r in releases
                if "namadillo@v" in r.get("tag_name", "")
            ]
        else:
            versions = [
                t.get("name", "").lstrip("v")
                for t in releases
            ]

        # Only keep versions that look like X.Y.Z or X.Y.Z-suffix
        versions = [v for v in versions if re.match(r"^\d+\.\d+\.\d+", v)]

        latest_versions[key] = max(
            versions,
            key=extract_numeric_version,
            default="n/a"
        )

    return latest_versions

# Fetch version and commit hash for indexers (Indexer & MASP)
def get_indexer_version(url):
    try:
        r = requests.get(f"{url.rstrip('/')}/health", timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("version", "n/a"), data.get("commit", "n/a")
    except requests.exceptions.RequestException:
        return "n/a", "n/a"

# Fetch Namadillo (Interface) version
def get_interface_version(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        s = BeautifulSoup(r.text, "html.parser")
        t = s.find("script", {"type": "module", "crossorigin": True})
        if not t or "src" not in t.attrs:
            return "n/a"
        js_r = requests.get(f"{url.rstrip('/')}/{t['src'].lstrip('/')}", timeout=5)
        js_r.raise_for_status()
        match = re.search(r'version\$1\s*=\s*"([\d.]+)"', js_r.text)
        return match.group(1) if match else "n/a"
    except requests.exceptions.RequestException:
        return "n/a"

# Process data for each network
def update_status():
    output_data = {
        "script_start_time": START_TIME,
        "script_end_time": "",
        "latest_versions": fetch_latest_versions(),
        "networks": []
    }

    for network, components in NETWORKS.items():
        network_status = {
            "network": network,
            "interface": [],
            "indexer": [],
            "masp": []
        }

        for key, url in components.items():
            for item in fetch_json(url):
                component_url = item.get("Indexer API URL" if key in ["indexer", "masp"] else "Interface URL", "n/a")
                discord = item.get("Discord UserName", "n/a")
                team = item.get("Team or Contributor Name", "n/a")

                if key in ["indexer", "masp"]:
                    version, commit = get_indexer_version(component_url)
                else:
                    version, commit = get_interface_version(component_url), None

                entry = {"team": team, "discord": discord, "url": component_url, "version": version}
                if commit:
                    entry["commit"] = commit

                network_status[key].append(entry)

        output_data["networks"].append(network_status)

    output_data["script_end_time"] = datetime.now(timezone.utc).isoformat() + "Z"

    # Save JSON file
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

# Run the script
if __name__ == "__main__":
    update_status()
