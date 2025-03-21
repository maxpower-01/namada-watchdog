import requests, json
from collections import Counter
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set UTC alias
UTC = timezone.utc

# RPC source definitions
RPCS = {
    "namada": {
        "rpc": "https://github.com/Luminara-Hub/namada-ecosystem/raw/main/user-and-dev-tools/mainnet/rpc.json"
    },
    "housefire": {
        "rpc": "https://github.com/Luminara-Hub/namada-ecosystem/raw/main/user-and-dev-tools/testnet/housefire/rpc.json"
    }
}

TIMEOUT = 5
FILTER_LIMITS = {
    "namada": 10,
    "housefire": 3
}

# Download JSON with fail-safe
def safe_get_json(url):
    try:
        return requests.get(url, timeout=TIMEOUT).json()
    except:
        return {}

# Get list of RPC endpoints
def extract_rpcs(source_url):
    return [entry.get("RPC Address") for entry in safe_get_json(source_url) if "RPC Address" in entry]

# Get remote IPs from /net_info endpoint
def extract_ips(rpc_url):
    peers = safe_get_json(f"{rpc_url}/net_info").get("result", {}).get("peers", [])
    return [peer.get("remote_ip") for peer in peers if "remote_ip" in peer]

# Process one network (e.g. namada or housefire)
def process_network(name, config):
    rpc_endpoints = extract_rpcs(config["rpc"])
    all_ips = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(extract_ips, rpc) for rpc in rpc_endpoints]
        for future in as_completed(futures):
            try:
                all_ips.extend(future.result() or [])
            except:
                pass

    ip_counts = Counter(all_ips)

    return {
        "network": name,
        "total_connections": len(all_ips),
        "total_unique_ips": len(ip_counts),
        "ip_counts": ip_counts.most_common()
    }

# Generate markdown summary
def generate_markdown(data, output="CONNECTION.md"):
    with open(output, "w", encoding="utf-8") as f:
        f.write("# 🟡 namada-watchdog - Connection\n\n")

        for net_name, net_data in data["networks"].items():
            f.write("## 🚀 Namada (mainnet)\n" if net_name == "namada" else "## 🏠🔥 Housefire (testnet)\n\n")

            threshold = FILTER_LIMITS[net_name]
            filtered = [(ip, count) for ip, count in net_data["ip_counts"] if count >= threshold]

            f.write(f"- Total connections - {net_data['total_connections']}\n")
            f.write(f"- Unique IPs (filtered) - {len(filtered)}\n\n")

            f.write("| Remote IP | Connections |\n")
            f.write("|-----------|-------------|\n")
            for ip, count in filtered:
                f.write(f"| `{ip}` | {count} |\n")
            f.write("\n")

# Main entry point
def main():
    output_data = {
        "script_start_time": datetime.now(UTC).isoformat() + "Z"
    }

    results = {name: process_network(name, conf) for name, conf in RPCS.items()}
    output_data["script_end_time"] = datetime.now(UTC).isoformat() + "Z"
    output_data["networks"] = results

    with open("connection.json", "w") as f:
        json.dump(output_data, f, indent=2)

    generate_markdown(output_data)

if __name__ == "__main__":
    main()
