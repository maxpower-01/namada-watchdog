import json

INTERFACE_JSON_FILE = "interface.json"
INTERFACE_MD_FILE = "INTERFACE.md"

def load_status():
    try:
        with open(INTERFACE_JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("networks", [])
    except:
        return []

def get_latest_block_height(network_data):
    heights = [
        int(service["latest_block_height"]) for interface in network_data.get("interface", [])
        for service in interface.get("settings", [])
        if service.get("service") == "rpc" and service.get("latest_block_height", "").isdigit()
    ]
    return max(heights) if heights else 0

def determine_status(block_height, latest_block, network):
    green_grace = 100 if network == "namada" else 200
    yellow_grace = 300 if network == "namada" else 600

    if block_height >= latest_block - green_grace:
        return f"🟢 {block_height}"
    elif block_height >= latest_block - yellow_grace:
        return f"🟡 {block_height}"
    return f"🔴 {block_height or '-'}"

def process_interface_data(network_data, latest_block):
    teams = {}

    for item in network_data.get("interface", []):
        team = item.get("team", "").strip()
        if team not in teams:
            teams[team] = {
                "url": f"[{item.get('url', '')}]({item.get('url', '')})",
                "cometbft": "🔴 -",
                "indexer": "🔴 -",
                "masp": "🔴 -"
            }

    network_name = network_data.get("network", "")

    for interface in network_data.get("interface", []):
        team = interface.get("team", "").strip()
        if team in teams:
            rpc_height = max(
                int(s["latest_block_height"]) for s in interface.get("settings", [])
                if s.get("service") == "rpc" and s.get("latest_block_height", "").isdigit()
            ) if any(s.get("service") == "rpc" and s.get("latest_block_height", "").isdigit() for s in interface.get("settings", [])) else 0
            teams[team]["cometbft"] = determine_status(rpc_height, latest_block, network_name)

            for service in ["indexer", "masp"]:
                service_height = max(
                    int(s["latest_block_height"]) for s in interface.get("settings", [])
                    if s.get("service") == service and s.get("latest_block_height", "").isdigit()
                ) if any(s.get("service") == service and s.get("latest_block_height", "").isdigit() for s in interface.get("settings", [])) else 0
                teams[team][service] = determine_status(service_height, latest_block, network_name)

    return teams

def generate_interface_md():
    status_data = load_status()
    if not status_data:
        return

    md_content = "# 🟡 namada-watchdog - Interface\n\n"

    for network_data in status_data:
        network_name = "🚀 Namada (mainnet)" if network_data["network"] == "namada" else "🏠🔥 Housefire (testnet)"
        latest_block = get_latest_block_height(network_data)
        block_text = f"- Latest Block Height - {latest_block} *(This block height was recorded when this file was generated and may be outdated later.)*" if latest_block else ""

        teams = process_interface_data(network_data, latest_block)
        md_content += f"## {network_name}\n{block_text}\n\n"
        md_content += "| Team | Namadillo | CometBFT | Indexer | MASP Indexer |\n|-|-|-|-|-|\n"
        md_content += "\n".join(
            f"| {t} | {d['url']} | {d['cometbft']} | {d['indexer']} | {d['masp']} |"
            for t, d in teams.items()
        ) + "\n\n"

    with open(INTERFACE_MD_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_interface_md()
