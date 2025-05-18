import urllib.request, json, tomllib, ssl, time, re
from datetime import datetime, UTC
from bs4 import BeautifulSoup

# Start time
START_TIME = datetime.now(UTC).isoformat() + "Z"

# Configuration URLs
INTERFACES = {
    "namada": {"interface": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/mainnet/interfaces.json"},
    "housefire": {"interface": "https://raw.githubusercontent.com/Luminara-Hub/namada-ecosystem/main/user-and-dev-tools/testnet/housefire/interfaces.json"}
}

LATEST_VERSIONS = {
    "interface": "https://api.github.com/repos/anoma/namada-interface/releases",
    "indexer": "https://api.github.com/repos/anoma/namada-indexer/tags",
    "masp": "https://api.github.com/repos/anoma/namada-masp-indexer/tags",
    "namada": "https://api.github.com/repos/anoma/namada/tags"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}
SSL_CONTEXT = ssl.create_default_context()

# Fetch data from URL
def fetch_url(url, retries=3, timeout=5):
    for _ in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), context=SSL_CONTEXT, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except:
            time.sleep(2)
    return None

# Fetch JSON data
def fetch_json(url):
    data = fetch_url(url)
    try:
        return json.loads(data) if data else {}
    except json.JSONDecodeError:
        return {}

# Check if version is a clean semver like "0.22.1"
def is_valid_semver(v):
    return re.fullmatch(r'\d+\.\d+\.\d+', v) is not None

# Fetch latest versions from GitHub
def fetch_latest_versions():
    latest_versions = {}
    for key, url in LATEST_VERSIONS.items():
        releases = fetch_json(url)

        if key == "interface":
            versions = [
                re.sub(r"namadillo@v", "", r["tag_name"])
                for r in releases if "namadillo@v" in r.get("tag_name", "")
            ]
        else:
            versions = [
                t["name"].lstrip("v")
                for t in releases
                if "name" in t and is_valid_semver(t["name"].lstrip("v"))
            ]

        latest_versions[key] = max(
            versions,
            key=lambda v: list(map(int, v.split('.'))),
            default="n/a"
        )

    return latest_versions

# Extract interface version
def get_interface_version(url):
    if not (r := fetch_url(url)): return "n/a"
    if (t := BeautifulSoup(r, "html.parser").find("script", {"type": "module", "crossorigin": True})) and "src" in t.attrs:
        if (js_r := fetch_url(f"{url.rstrip('/')}/{t['src'].lstrip('/')}")) and (match := re.search(r'version\$1\s*=\s*"([\d.]+)"', js_r)):
            return match.group(1)
    return "n/a"

# Parse config.toml file
def parse_config(url):
    if not (data := fetch_url(f"{url}/config.toml", timeout=3)) or not data.strip():
        return {"rpc": "n/a", "indexer": "n/a", "masp": "n/a"}
    try:
        config = tomllib.loads(data)
        return {
            "rpc": config.get("rpc_url", "n/a"),
            "indexer": config.get("indexer_url", "n/a"),
            "masp": config.get("masp_indexer_url", "n/a")
        }
    except tomllib.TOMLDecodeError:
        return {"rpc": "n/a", "indexer": "n/a", "masp": "n/a"}

# Extract Namada version from moniker
def extract_moniker_version(moniker):
    return (match.group(1) if (match := re.search(r"[-_]v(\d+\.\d+\.\d+)", moniker)) else "n/a")

# Fetch service data
def get_service_data(service, url):
    if service == "rpc":
        rpc_status = fetch_json(f"{url}/status")
        sync_info, node_info = rpc_status.get("result", {}).get("sync_info", {}), rpc_status.get("result", {}).get("node_info", {})
        return {
            "version": node_info.get("version", "n/a"),
            "namada_version": extract_moniker_version(node_info.get("moniker", "")),
            "service": service,
            "url": url,
            "latest_block_height": str(sync_info.get("latest_block_height", "n/a"))
        }
    
    block_data = fetch_json(f"{url}/api/v1/chain/block/latest" if "indexer" in service else f"{url}/api/v1/height")
    return {
        "version": fetch_json(f"{url}/health").get("version", "n/a"),
        "service": service,
        "url": url,
        "latest_block_height": str(block_data.get("block_height") or block_data.get("block") or "n/a")
    }

# Generate JSON data
output_data = {
    "script_start_time": START_TIME,
    "script_end_time": "",
    "latest_versions": fetch_latest_versions(),
    "networks": []
}

for network, sources in INTERFACES.items():
    if not (interfaces_json := fetch_url(sources["interface"], timeout=5)): continue
    try: interfaces = json.loads(interfaces_json)
    except: continue

    network_interfaces = []
    
    for interface in interfaces:
        if "Namadillo" not in interface.get("Interface Name (Namadillo or Custom)", "") or not (interface_url := interface.get("Interface URL", "").rstrip('/')):
            continue

        config = parse_config(interface_url)
        settings = [get_service_data(service, url) for service, url in config.items() if url != "n/a"]
        namada_version = next((s["namada_version"] for s in settings if s["service"] == "rpc"), "n/a")
        settings.insert(0, {"service": "namada", "version": namada_version})

        network_interfaces.append({
            "team": interface.get("Team or Contributor Name", "Unknown"),
            "discord": interface.get("Discord UserName", "Unknown"),
            "url": interface_url,
            "version": get_interface_version(interface_url),
            "settings": settings
        })
    
    output_data["networks"].append({"network": network, "interface": network_interfaces})

output_data["script_end_time"] = datetime.now(UTC).isoformat() + "Z"

# Save JSON
with open("interface.json", "w", encoding="utf-8") as json_file:
    json.dump(output_data, json_file, indent=4)