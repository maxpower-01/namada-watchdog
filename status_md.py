import json, re

STATUS_JSON_FILE = "status.json"
STATUS_MD_FILE = "STATUS.md"

def load_status():
    """ Load the status JSON file. """
    try:
        with open(STATUS_JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("networks", []), data.get("latest_versions", {})
    except:
        return [], {}

def parse_version(version):
    """ Convert version string into a tuple of integers for proper comparison. """
    return tuple(map(int, re.findall(r'\d+', version))) if version and version != "n/a" else (0,)

def process_status_data(network_data, latest_versions):
    teams = {}

    for category in ["interface", "indexer", "masp"]:
        latest_version = parse_version(latest_versions.get(category, "0.0.0"))

        for item in network_data.get(category, []):
            team = item.get("team", "n/a").strip()
            version = parse_version(item.get("version", "n/a"))

            if team not in teams:
                teams[team] = {"interface": "🔴 -", "indexer": "🔴 -", "masp": "🔴 -"}

            if version == (0,):
                status = "🔴"
            elif version >= latest_version:
                status = "🟢"
            elif version < latest_version:
                status = "🟡"
            else:
                status = "🔴"

            teams[team][category] = f"{status} {'.'.join(map(str, version))}" if version != (0,) else "🔴 -"

    return teams

def generate_status_md():
    networks, latest_versions = load_status()

    if not networks:
        return

    md_content = "# 🟡 namada-watchdog - Repository\n\n"

    for network_data in networks:
        network_name = "🚀 Namada (mainnet)" if network_data["network"] == "namada" else "🏠🔥 Housefire (testnet)"
        teams = process_status_data(network_data, latest_versions)

        md_content += f"## {network_name}\n\n"
        md_content += "| Team | Namadillo | Indexer | MASP Indexer |\n|-|-|-|-|\n"
        md_content += "\n".join(f"| {t} | {d['interface']} | {d['indexer']} | {d['masp']} |" for t, d in teams.items()) + "\n\n"

    with open(STATUS_MD_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_status_md()
