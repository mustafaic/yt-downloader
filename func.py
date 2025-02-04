from yt_dlp import YoutubeDL


def download(url, kayit_dizini='.'):
    try:
        # Yapılandırma ayarları
        ydl_opts = {
            'outtmpl': f'{kayit_dizini}/%(title)s.%(ext)s',  # Kayıt dizini ve dosya adı formatı
            'format': 'best',  # En iyi kaliteyi seç
        }

        # YouTubeDL nesnesi oluştur
        with YoutubeDL(ydl_opts) as ydl:
            print(f"İndiriliyor: {url}")
            ydl.download([url])  # Videoyu indir
            print("İndirme tamamlandı.")
    except Exception as e:
        print(f"Hata oluştu: {e}")


if __name__ == "__main__":
    # İndirilecek video URL'si
    video_url = input("Lütfen YouTube video URL'sini girin: ")

    # İndirme dizini (isteğe bağlı)
    kayit_dizini = input("İndirme dizinini girin (boş bırakılırsa bulunduğunuz dizine kaydedilir): ")

    # Videoyu indir
    download(video_url, kayit_dizini if kayit_dizini else '.')