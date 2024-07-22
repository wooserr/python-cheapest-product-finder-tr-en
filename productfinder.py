import requests
from bs4 import BeautifulSoup
import os
import subprocess
import sys


def check_and_install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    check_and_install("beautifulsoup4")
    check_and_install("requests")


def amazon_urunleri_getir(urun_adi):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    url = f"https://www.amazon.com.tr/s?k={urun_adi}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Amazon isteği başarısız oldu:", response.status_code)
        return []
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    urunler = []
    for urun in soup.find_all("div", {"data-component-type": "s-search-result"}):
        try:
            fiyat_whole = urun.find("span", class_="a-price-whole").get_text().replace(".", "").replace(",", "").strip()
            fiyat_fraction = urun.find("span", class_="a-price-fraction").get_text().strip()
            fiyat = float(fiyat_whole + "." + fiyat_fraction)
            link = urun.find("a", class_="a-link-normal s-no-outline")['href']
            urunler.append((fiyat, f"https://www.amazon.com.tr{link}"))
        except (AttributeError, ValueError):
            continue
    
    return urunler

def fiyat_araliginda_urunler(urunler, min_fiyat, max_fiyat):
    uygun_urunler = [link for fiyat, link in urunler if min_fiyat <= fiyat <= max_fiyat]
    return uygun_urunler

def linkleri_txt_kaydet(linkler, urun_adi, min_fiyat, max_fiyat):
    masaustu_yolu = os.path.join(os.path.expanduser("~"), "Desktop")
    dosya_adi = f"{urun_adi}_urunleri_{min_fiyat}-{max_fiyat}.txt"
    dosya_yolu = os.path.join(masaustu_yolu, dosya_adi)
    
    with open(dosya_yolu, "w", encoding="utf-8") as dosya:
        for link in linkler:
            dosya.write(link + "\n")
    
    print(f"En uygun ürün linkleri {dosya_yolu} dosyasına kaydedildi.")

def main():
    urun_adi = input("Aramak istediğiniz ürün adını girin: ")
    min_fiyat = float(input("Minimum fiyatı girin (TL): "))
    max_fiyat = float(input("Maksimum fiyatı girin (TL): "))
    
    urunler = amazon_urunleri_getir(urun_adi)
    if urunler:
        uygun_urunler = fiyat_araliginda_urunler(urunler, min_fiyat, max_fiyat)
        if uygun_urunler:
            linkleri_txt_kaydet(uygun_urunler, urun_adi, min_fiyat, max_fiyat)
        else:
            print(f"Belirtilen fiyat aralığında {urun_adi} bulunamadı.")
    else:
        print(f"{urun_adi} için ürün bulunamadı.")

if __name__ == "__main__":
    main()
