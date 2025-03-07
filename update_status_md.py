import json, requests, re
from datetime import datetime, timezone

STATUS_FILES = {"namada": "STATUS_namada.md", "housefire": "STATUS_housefire.md"}
STATUS_JSON_FILES = {"namada": "status_namada.json", "housefire": "status_housefire.json"}
LATEST_VERSIONS = {
    "interface": "https://api.github.com/repos/anoma/namada-interface/releases",
    "indexer": "https://api.github.com/repos/anoma/namada-indexer/tags"
}

def load_status(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return None

def parse_version(version):
    return tuple(map(int, re.findall(r'\d+', version))) if version and version != "unknown" else (0,)

def fetch_latest_versions():
    versions = {"interface": "unknown", "indexer": "unknown"}

    try:
        r = requests.get(LATEST_VERSIONS["interface"], timeout=5).json()
        versions["interface"] = max(
            (re.sub(r"namadillo@v", "", rel["tag_name"]) for rel in r if "namadillo@" in rel["tag_name"]),
            key=parse_version, default="unknown"
        )
    except:
        pass

    try:
        r = requests.get(LATEST_VERSIONS["indexer"], timeout=5).json()
        versions["indexer"] = max(
            (tag["name"].lstrip("v") for tag in r if re.match(r'^v\d+\.\d+\.\d+$', tag["name"])),
            key=parse_version, default="unknown"
        )
    except:
        pass

    return versions

def process_status_data(status, latest_versions):
    teams = {}
    for category in ["interface", "indexer"]:
        for item in status.get(category, []):
            team = item.get("team", "n/a")
            if team not in teams:
                teams[team] = {
                    "discord": re.sub(r'[,;]+', '<br>', item.get("discord", "n/a").replace("|", "\\|")),
                    "interface": "n/a",
                    "indexer": "n/a"
                }
            
            version, url = item.get("version", "unavailable"), item.get("url", "")

            if version != "unavailable":
                url = url.rstrip("/") + "/health" if category == "indexer" and url else url
                link = f" [[>]]({url})" if url else ""
                emoji = "🎉" if parse_version(version) == parse_version(latest_versions[category]) else "⚠️"
                teams[team][category] = f"{emoji} {version} {link}"
            else:
                teams[team][category] = "💀"
    
    return teams

def update_status_md(network):
    latest_versions = fetch_latest_versions()
    status = load_status(STATUS_JSON_FILES[network])
    if not status: return

    teams = process_status_data(status, latest_versions)

    md_content = f"""# 🟡 namada-watchdog - Status: {network.capitalize()}

## 🔥 Latest Releases
- Interface (Namadillo): {latest_versions['interface']}
- Indexer: {latest_versions['indexer']}

## {network.capitalize()}
| Team | Discord | Interface | Indexer |
|-|-|-|-|
"""
    md_content += "\n".join(f"| {t} | {d['discord']} | {d['interface']} | {d['indexer']} |" for t, d in teams.items())

    with open(STATUS_FILES[network], "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    for net in STATUS_FILES.keys():
        update_status_md(net)
