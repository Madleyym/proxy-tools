def convert_to_socks5(proxies):
    socks5_proxies = []
    for proxy in proxies:
        if proxy.strip():  
            parts = proxy.strip().split(':')
            if len(parts) == 4:
                hostname = parts[0]
                port = parts[1]
                username = parts[2]
                password = parts[3]
                socks5_proxy = f"socks5://{username}:{password}@{hostname}:{port}"
                socks5_proxies.append(socks5_proxy)
    return socks5_proxies

# Membaca daftar proxy dari file proxies.txt
try:
    with open("proxies.txt", "r") as f:
        http_proxies = [line.strip() for line in f.readlines()]
    
    # Konversi ke format SOCKS5
    socks5_proxies = convert_to_socks5(http_proxies)
    
    # Simpan hasil ke file logs
    with open("logs", "w") as f:
        for proxy in socks5_proxies:
            f.write(proxy + "\n")
    
    print(f"Konversi selesai! {len(socks5_proxies)} proxy telah dikonversi ke format SOCKS5 dan disimpan dalam file 'logs'")

except FileNotFoundError:
    print("Error: File 'proxies.txt' tidak ditemukan.")
except Exception as e:
    print(f"Terjadi kesalahan: {e}")