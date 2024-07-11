import requests
import requests
import json
import time
from colorama import init, Fore, Style
import sys
import os
import random
init(autoreset=True)

with open('data.txt', 'r') as file:
    doc_data = file.readlines()

with open('proxy.txt', 'r') as proxy_file:
    proxy_list = proxy_file.readlines()
def get_public_ip(proxy):
    try:
        proxies = {
            "http": f"{proxy}",
        }
        response = requests.get("http://httpbin.org/ip", proxies=proxies)
        if response.status_code == 200:
            ip = response.json()['origin']
            print(f"\nĐịa chỉ IP hiện tại: {ip}")
            return ip
        else:
            print("Không thể lấy địa chỉ IP.")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy địa chỉ IP: {e}")
        
def get_access_token(tao_data_dc, proxy):
    proxies = {
        "http": f"{proxy}",
    }
    url = "https://api.tapswap.ai/api/account/login"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Origin": "https://app.tapswap.club",
        "Referer": "https://app.tapswap.club/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "x-app": "tapswap_server",
        "x-cv": "622",
        "x-bot": "no",
    }
    chr_value, query_id = tao_data_dc.split('|')
    payload = {
        "init_data": query_id,
        "referrer": "",
        "chr" : int(chr_value),
        "bot_key": "app_bot_1"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), proxies=proxies)

    if response.status_code == 201:
        data = response.json()
        if 'access_token' in data:
            access_token = data['access_token']
            name = data['player']['full_name']
            coin = data['player']['shares']
            energy = data['player']['energy']
            level_energy = data['player']['energy_level']
            level_charge = data['player']['charge_level']
            level_tap = data['player']['tap_level']
            boosts = data['player']['boost']
            energy_boost = next((b for b in boosts if b["type"] == "energy"), None)
            turbo_boost = next((b for b in boosts if b["type"] == "turbo"), None)
            boost_ready = turbo_boost['cnt']
            energy_ready = energy_boost['cnt']

            print(f"{Fore.BLUE+Style.BRIGHT}\n==========================\n")  
            print(f"{Fore.GREEN+Style.BRIGHT}[*] Name: {name}")    
            print(f"{Fore.YELLOW+Style.BRIGHT}[*] Balance: {coin}")
            print(f"{Fore.YELLOW+Style.BRIGHT}[*] Năng lượng: {energy}")
            print(f"{Fore.CYAN+Style.BRIGHT}[*] Level tap/energy/recharge: {level_tap}/{level_energy}/{level_charge}")
            print(f"{Fore.MAGENTA+Style.BRIGHT}[*] Boost: Tăng tốc {turbo_boost['cnt']} | Full Energy : {energy_boost['cnt']}")

            return access_token, energy, boost_ready, energy_ready
        else:
            print("Access Token không phản hồi")
            return None, None, None, None
    elif response.status_code == 408:
        print("Hết thời gian yêu cầu")
    else:
        print(response.json())
        print(f"Không thể lấy access token, mã trạng thái: {response.status_code}")
    
    return None, None, None, None
turbo_activated = False    
def apply_turbo_boost(access_token, proxy):
    proxies = {
        "http": f"{proxy}",
    }
    global turbo_activated
    url = "https://api.tapswap.ai/api/player/apply_boost"
    headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Origin": "https://app.tapswap.club",
            "Referer": "https://app.tapswap.club/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "x-app": "tapswap_server",
            "x-cv": "622",
            "x-bot": "no",
        }

    
    payload = {"type": "turbo"}
    if turbo_activated == False:
        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        if response.status_code == 201:

            print(f"\r{Fore.GREEN+Style.BRIGHT}Turbo được kích hoạt thành công", flush=True)
            turbo_activated = True
            return True

        else:
            print(f"{Fore.RED+Style.BRIGHT}Không thể kích hoạt turbo, mã trạng thái: {response.json()}")
            return False
    else:
        print(f"\r{Fore.GREEN+Style.BRIGHT}Turbo đã kích hoạt")
        return True


not_enough_balance = {
    "tap": False,
    "energy": False,
    "charge": False
}
def upgrade_level(headers, upgrade_type, proxy):
    proxies = {
        "http": f"{proxy}",
    }
    global not_enough_balance
    if not_enough_balance[upgrade_type]:
        return False
    for i in range(5):
        print(f"\r{Fore.WHITE+Style.BRIGHT}Đang nâng cấp {upgrade_type} {'.' * (i % 4)}", end='', flush=True)
    url = "https://api.tapswap.ai/api/player/upgrade"
    payload = {"type": upgrade_type}
    response = requests.post(url, headers=headers, json=payload, proxies=proxies)
    if response.status_code == 201:
        print(f"\r{Fore.GREEN+Style.BRIGHT}Nâng cấp {upgrade_type} thành công", flush=True)
        return True
    else:
        response_json = response.json()
        if 'message' in response_json and 'not_enough_shares' in response_json['message']:
            print(f"\r{Fore.RED+Style.BRIGHT}Không đủ balance để nâng cấp {upgrade_type}", flush=True)
            not_enough_balance[upgrade_type] = True
            return False
        else:
            print(f"\r{Fore.RED+Style.BRIGHT}Lỗi khi nâng cấp {upgrade_type}: {response_json['message']}", flush=True)
        return False



use_booster = input("Sử dụng booster tự động? (Y/N): ").strip().lower()
if use_booster in ['y', 'n', '']:
    use_booster = use_booster or 'n'
else:
    print("Phải là 'Y' hoặc 'N'")
    sys.exit()


use_upgrade = input("Nâng cấp tự động? (Y/N): ").strip().lower()
if use_upgrade in ['y', 'n', '']:
    use_upgrade = use_upgrade or 'n'
else:
    print("Phải là 'Y' hoặc 'N'")
    sys.exit()

def submit_taps(access_token, energy, boost_ready, energy_ready, content_id, time_stamp, tao_data_dc, proxy):
    proxies = {
        "http": f"{proxy}",
    }
    global turbo_activated
    turbo_not_ready_notified = False 

    while True:
        url = "https://api.tapswap.ai/api/player/submit_taps"

        if use_booster == 'y' and boost_ready > 0:
            if not turbo_activated:
                print(f"\r{Fore.WHITE+Style.BRIGHT}Turbo đã sẵn sàng, mua turbo", end='', flush=True)
                apply_turbo_boost(access_token, proxy)
            else:
                print(f"\r{Fore.WHITE+Style.BRIGHT}Turbo đã kích hoạt", end='', flush=True)
        elif use_booster == 'y' and boost_ready == 0 and not turbo_not_ready_notified:
            turbo_not_ready_notified = True

        if energy < 50:
            print(f"\r{Fore.RED+Style.BRIGHT}Năng lượng thấp", end='', flush=True)
            if use_booster == 'y' and energy_ready > 0:
                print(f"\r{Fore.WHITE+Style.BRIGHT}Năng lượng sẵn sàng, mua năng lượng", end='', flush=True)
                if apply_energy_boost(access_token, proxy):
                    energy = 300  
                    continue  
                else:
                    print(f"\r{Fore.RED+Style.BRIGHT}Không thể mua năng lượng, chuyển tài khoản", end='', flush=True)
                    return
            else:
                time.sleep(3)
                print(f"\r{Fore.RED+Style.BRIGHT}Chuyển sang tài khoản tiếp theo", end='', flush=True)
                return
        else:
            print(f"\r{Fore.WHITE+Style.BRIGHT}Bắt đầu tap", end='', flush=True)

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {access_token}",
            "Connection": "keep-alive",
            "Content-Id": content_id,
            "Content-Type": "application/json",
            "Origin": "https://app.tapswap.club",
            "Referer": "https://app.tapswap.club/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "x-app": "tapswap_server",
            "x-bot": "no",
            "x-cv": "622",
        }

        total_taps = random.randint(100000, 1000000) if turbo_activated else random.randint(50, 250)
        payload = {"taps": total_taps, "time": int(time_stamp)}

        if turbo_activated:
            for _ in range(22):
                response = requests.post(url, headers=headers, json=payload, proxies=proxies)
                if response.status_code == 201:
                    response_data = response.json()
                    energy_dc = response_data.get("player", {}).get("energy", 0)
                    coin_balance = response_data.get("player", {}).get("shares", 0)
                    print(f"\r{Fore.GREEN+Style.BRIGHT}Tap thành công: balance {coin_balance} / năng lượng còn lại {energy_dc}", flush=True)
                else:
                    print(f"\r{Fore.RED+Style.BRIGHT}Không thể tap, mã trạng thái: {response.status_code}")
            turbo_activated = False
        else:
            response = requests.post(url, headers=headers, json=payload, proxies=proxies)
            if response.status_code == 201:
                response_data = response.json()
                energy_dc = response_data.get("player", {}).get("energy", 0)
                coin_balance = response_data.get("player", {}).get("shares", 0)
                print(f"\r{Fore.GREEN+Style.BRIGHT}Tap thành công: balance {coin_balance} / năng lượng còn lại {energy_dc}", flush=True)

                if use_upgrade == 'y':
                    if not not_enough_balance["tap"]:
                        upgrade_level(headers, "tap", proxy)
                    if not not_enough_balance["energy"]:
                        upgrade_level(headers, "energy", proxy)
                    if not not_enough_balance["charge"]:
                        upgrade_level(headers, "charge", proxy)
                energy = energy_dc  
                if energy < 50:
                    if use_booster == 'y' and energy_ready > 0:
                        print(f"\r{Fore.WHITE+Style.BRIGHT}Năng lượng sẵn sàng, mua năng lượng", end='', flush=True)
                        if apply_energy_boost(access_token, proxy):
                            energy = 300 
                        else:
                            print(f"\r{Fore.RED+Style.BRIGHT}Không thể mua năng lượng, chuyển tài khoản", end='', flush=True)
                            return
                    else:
                        print(f"\r{Fore.RED+Style.BRIGHT}Năng lượng thấp, kiểm tra tài khoản\n", end='', flush=True)
                        return
            else:
                print(f"\n\r{Fore.RED+Style.BRIGHT}Không thể tap, mã trạng thái: {response.status_code}")
                print(response.text)

def clear_console():

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
def apply_energy_boost(access_token, proxy):
    proxies = {
        "http": f"{proxy}",
    }
    url = "https://api.tapswap.ai/api/player/apply_boost"
    headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Origin": "https://app.tapswap.club",
            "Referer": "https://app.tapswap.club/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "x-app": "tapswap_server",
            "x-cv": "622",
            "x-bot": "no",
        }

    payload = {"type": "energy"}
    response = requests.post(url, headers=headers, json=payload, proxies=proxies)
    if response.status_code == 201:
        print(f"\r{Fore.GREEN+Style.BRIGHT}Đã mua năng lượng", flush=True)
        submit_taps(access_token, 100, 0, 0, content_id, time_stamp, tao_data_dc, proxy)  
        return True

    else:
        print(f"{Fore.RED+Style.BRIGHT}Không thể mua năng lượng, mã trạng thái: {response.status_code}")
        return False
proxy_index = 0
while True:
    for xuly_data_dc in doc_data:
        if proxy_index >= len(proxy_list):
            print("Đã hết proxy trong danh sách.")
            proxy_index = 0
        proxy = proxy_list[proxy_index].strip()
        proxy_index += 1
        get_public_ip(proxy)
        parts = xuly_data_dc.strip().split('|')
        if len(parts) != 4:
            print(f"Dữ liệu không hợp lệ: {xuly_data_dc}")
            continue
        content_id = parts[0]
        time_stamp = parts[1]
        chr_value = parts[2]
        query_id = parts[3]
        tao_data_dc = chr_value + '|' + query_id
        access_token, energy, boost_ready, energy_ready = get_access_token(tao_data_dc.strip(), proxy)
        if access_token:
            submit_taps(access_token, energy, boost_ready, energy_ready, content_id, time_stamp, tao_data_dc.strip(), proxy)

    print(f"\n\n{Fore.CYAN+Style.BRIGHT}==============Tất cả tài khoản đã được xử lý=================\n")
    for giay in range(60, 0, -1):
        print(f"\rBắt đầu lại sau {giay} giây...", end='')
        time.sleep(1)
    clear_console()