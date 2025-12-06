import asyncio
import aioping
import ipaddress

# Progress tracking
progress = {
    "total": 0,
    "scanned": 0
}

# Store active IPs
active_ips = []

def update_progress():
    percent = (progress["scanned"] / progress["total"]) * 100
    bar_length = 30
    filled = int(percent / 100 * bar_length)
    bar = "█" * filled + "-" * (bar_length - filled)
    print(
        f"\rProgress: |{bar}| {percent:6.2f}% ({progress['scanned']}/{progress['total']})",
        end="",
        flush=True
    )

# Lock for progress updating
progress_lock = asyncio.Lock()

# Ping function
async def ping_ip(ip):
    async with sem:
        try:
            delay = await aioping.ping(str(ip), timeout=1)
            async with progress_lock:
                active_ips.append(str(ip))
        except asyncio.TimeoutError:
            pass
        finally:
            async with progress_lock:
                progress["scanned"] += 1
                update_progress()

# Ping hosts in the subnet
async def scan_network(subnet):
    tasks = []
    for ip in subnet.hosts():
        tasks.append(asyncio.create_task(ping_ip(ip)))

    await asyncio.gather(*tasks)

def print_banner():
    banner = r"""
           _    _      _                            _                   
          | |  | |    | |                          | |                  
          | |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___             
          | |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \            
          \  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) |           
           \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/            
                                                                        
                                                                        
 _   _      _                      _     ______ _                       
| \ | |    | |                    | |    | ___ (_)                      
|  \| | ___| |___      _____  _ __| | __ | |_/ /_ _ __   __ _  ___ _ __ 
| . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ / |  __/| | '_ \ / _` |/ _ \ '__|
| |\  |  __/ |_ \ V  V / (_) | |  |   <  | |   | | | | | (_| |  __/ |   
\_| \_/\___|\__| \_/\_/ \___/|_|  |_|\_\ \_|   |_|_| |_|\__, |\___|_|   
                                                         __/ |          
                                                        |___/           
"""
    print(banner)

print_banner()

# User input
network_to_scan = input("\nWhat is the network you want to scan? (e.g: 192.168.1.0/24): ")
print(" ")

sem = asyncio.Semaphore(100)

network_to_scan = ipaddress.ip_network(network_to_scan)

progress["total"] = network_to_scan.num_addresses - 2

# Run the scan
asyncio.run(scan_network(network_to_scan))

# Print results at the end
print("\nScan complete!\n")
print(f"Active IPs ({len(active_ips)}):")
for ip in active_ips:
    print(ip)
