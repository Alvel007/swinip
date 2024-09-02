import os
import requests

# Указываем URL, откуда будем загружать файл с IP-адресами
url = 'https://raw.githubusercontent.com/Alvel007/swinip/main/ips.txt'

# Локальный путь к конфигурационному файлу network
config_path = 'network'

wg_name = 'sit9'

# Интерфейс WireGuard, который нужно обновить
wg_interface_name = 'amneziawg_sit9'

# Функция для загрузки файла с GitHub
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
            print("Не удалось загрузить файл с IP-адресами")
            return []
    except requests.RequestException as e:
        print(f"Произошла ошибка при загрузке файла: {e}")
        return []


def update_wireguard_config(ip_list):
    with open(config_path, "r", encoding="utf-8") as file:
        config_lines = file.readlines()

    new_config_lines = []
    found_interface = False
    added_ips = False
    found_endpoint_port = False

    for line in config_lines:
        # Проверяем, нашли ли мы нужный интерфейс
        if line.strip().startswith(f"config {wg_interface_name}"):
            found_interface = True
            added_ips = False  # Обнуляем флаг добавления IP для нового интерфейса
            found_endpoint_port = False  # Обнуляем флаг, когда нашли новый интерфейс
            new_config_lines.append(line)
            continue
        
        # Если мы находимся внутри нужного интерфейса
        if found_interface:
            if line.strip().startswith("list allowed_ips"):
                # Пропускаем все старые записи list allowed_ips
                continue
            elif line.strip().startswith("option endpoint_port"):
                found_endpoint_port = True  # Помечаем, что нашли нужную строку
                new_config_lines.append(line)
                continue
            elif found_endpoint_port and not added_ips:
                # Добавляем новые IP-адреса после строки с option endpoint_port
                for ip in ip_list:
                    new_config_lines.append(f"\tlist allowed_ips '{ip}/32'\n")
                added_ips = True  # Устанавливаем флаг, что IP-адреса добавлены
                found_interface = False  # Завершаем обработку текущего интерфейса

            new_config_lines.append(line)
        else:
            new_config_lines.append(line)

    with open(config_path, "w", encoding="utf-8") as file:
        file.writelines(new_config_lines)

    print(f"Обновление конфигурации завершено. Добавлено {len(ip_list)} IP-адресов.")

update_wireguard_config(download_ip_list(url))

# Функция для перезапуска интерфейса WireGuard
def restart_wireguard_interface():
    os.system(f"ifdown {wg_name}")
    os.system(f"ifup {wg_name}")

# Основной процесс
if __name__ == "__main__":
    ip_list = download_ip_list(url)
    if ip_list:
        update_wireguard_config(ip_list)
        restart_wireguard_interface()
        print("Конфигурация WireGuard успешно обновлена и интерфейс перезапущен.")
    else:
        print("Список IP пуст или не удалось его загрузить.")
