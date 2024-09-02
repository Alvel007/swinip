import os
import requests

url = 'https://raw.githubusercontent.com/Alvel007/swinip/main/ips.txt'

config_path = '/etc/config/network'

wg_name = 'sit9'

wg_interface_name = 'amneziawg_sit9'

def download_ip_list(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            seen = set()
            ip_list = []
            for line in response.text.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and line not in seen:
                    ip_list.append(line)
                    seen.add(line)
            return ip_list
        else:
            print("Error download")
            return []
    except requests.RequestException as e:
        print(f"Error download: {e}")
        return []


def update_wireguard_config(ip_list):
    with open(config_path, "r", encoding="utf-8") as file:
        config_lines = file.readlines()

    new_config_lines = []
    found_interface = False
    added_ips = False
    found_endpoint_port = False

    for line in config_lines:
        if line.strip().startswith(f"config {wg_interface_name}"):
            found_interface = True
            added_ips = False
            found_endpoint_port = False
            new_config_lines.append(line)
            continue
        
        if found_interface:
            if line.strip().startswith("list allowed_ips"):
                continue
            elif line.strip().startswith("option endpoint_port"):
                found_endpoint_port = True
                new_config_lines.append(line)
                continue
            elif found_endpoint_port and not added_ips:
                for ip in ip_list:
                    new_config_lines.append(f"\tlist allowed_ips '{ip}/32'\n")
                added_ips = True
                found_interface = False

            new_config_lines.append(line)
        else:
            new_config_lines.append(line)

    with open(config_path, "w", encoding="utf-8") as file:
        file.writelines(new_config_lines)

    print(f"successful {len(ip_list)} IP.")

update_wireguard_config(download_ip_list(url))

def restart_wireguard_interface():
    os.system(f"ifdown {wg_name}")
    os.system(f"ifup {wg_name}")

# Основной процесс
if __name__ == "__main__":
    ip_list = download_ip_list(url)
    if ip_list:
        update_wireguard_config(ip_list)
        restart_wireguard_interface()
        print("Everything was successful.")
    else:
        print("It doesn't work.")
