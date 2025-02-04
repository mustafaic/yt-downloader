import os
import re
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5 import QtWidgets, QtGui, QtCore
from yt_dlp import YoutubeDL
from downloader_arayuz import Ui_MainWindow


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.button_convert.clicked.connect(self.convert)
        self.ui.button_delete.clicked.connect(self.clear_list)
        self.ui.pushButton.clicked.connect(self.download_video)


    def extract_video_id(self, url):
        """
        YouTube URL'sinden video ID'sini çıkarır.
        """
        # YouTube Video ID için regex
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def get_video_formats(self):
        url = self.ui.url_entry.text().strip()
        if not url:
            self.ui.comboBox.clear()
            self.ui.comboBox.addItem("Geçerli bir URL girin!")
            return

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }

            with YoutubeDL(ydl_opts) as ydl:
                try:
                    info_dict = ydl.extract_info(url, download=False)
                except Exception as e:
                    print(f"URL doğrulama hatası: {e}")
                    self.ui.comboBox.clear()
                    self.ui.comboBox.addItem("Geçersiz URL veya video bulunamadı!")
                    return

                formats = info_dict.get('formats', [])
                if not formats:
                    self.ui.comboBox.clear()
                    self.ui.comboBox.addItem("Bu video için format bulunamadı!")
                    return

                self.ui.comboBox.clear()

                video_formats = {}
                audio_formats = []

                def get_safe_filesize(format_dict):
                    """Güvenli bir şekilde dosya boyutunu al"""
                    # Önce filesize'ı kontrol et
                    filesize = format_dict.get('filesize')
                    if filesize is not None:
                        return filesize

                    # filesize yoksa filesize_approx'a bak
                    filesize_approx = format_dict.get('filesize_approx')
                    if filesize_approx is not None:
                        return filesize_approx

                    # Hiçbiri yoksa 0 dön
                    return 0

                def get_filesize_text(filesize):
                    """Dosya boyutunu MB cinsinden formatla"""
                    if not filesize:
                        return "~MB"
                    size_mb = filesize / (1024 * 1024)
                    return f"{size_mb:.1f} MB"

                for f in formats:
                    ext = f.get('ext', '').lower()
                    vcodec = f.get('vcodec', 'none')
                    height = f.get('height', 0)

                    # MP4 video formatları
                    if ext == 'mp4' and vcodec != 'none' and height:
                        res_key = f"{height}p"
                        current_size = get_safe_filesize(f)

                        if res_key not in video_formats:
                            video_formats[res_key] = f
                        else:
                            existing_size = get_safe_filesize(video_formats[res_key])
                            if current_size > existing_size:
                                video_formats[res_key] = f

                    # Ses formatları
                    elif ext in ['mp3', 'm4a'] and vcodec == 'none':
                        audio_formats.append(f)

                # Ses formatını ekle
                if audio_formats:
                    best_audio = max(audio_formats,
                                     key=lambda x: (x.get('abr', 0), get_safe_filesize(x)))
                    size_text = get_filesize_text(get_safe_filesize(best_audio))
                    format_str = f"MP3 ({size_text})"
                    self.ui.comboBox.addItem(format_str, best_audio['format_id'])

                # Video formatlarını ekle
                for resolution, f in sorted(video_formats.items(),
                                            key=lambda x: int(''.join(filter(str.isdigit, x[0])) or 0),
                                            reverse=True):
                    size_text = get_filesize_text(get_safe_filesize(f))
                    format_str = f"Video: {resolution} ({size_text})"
                    self.ui.comboBox.addItem(format_str, f['format_id'])

                if self.ui.comboBox.count() == 0:
                    self.ui.comboBox.addItem("Desteklenen format bulunamadı!")

                # ComboBox stilini ayarla
                self.ui.comboBox.setStyleSheet("""
                    QComboBox {
                        color: white;
                        padding: 5px;
                        border: 1px solid #555;
                        border-radius: 3px;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                    }
                """)

        except Exception as e:
            self.ui.comboBox.clear()
            self.ui.comboBox.addItem("Hata: Video bilgisi alınamadı!")
            print(f"Hata detayı: {str(e)}")
            import traceback
            traceback.print_exc()


    def convert(self):

        self.get_video_formats()

        API_KEY = "AIzaSyADIOXG3s0DdWRKRE6bassmwUHodtj853A"  # Google Cloud API Key

        # Kullanıcının yazdığı URL'yi al
        url = self.ui.url_entry.text().strip()
        video_id = self.extract_video_id(url)  # Video ID'yi çıkar

        if not video_id:
            self.ui.title_label.setText("Geçerli bir YouTube URL girin!")
            self.ui.thumbnail_label.clear()
            return

        # YouTube API'den video bilgilerini al
        api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}"
        response = requests.get(api_url).json()

        if "items" in response and response["items"]:
            title = response["items"][0]["snippet"]["title"]
            thumbnail_url = response["items"][0]["snippet"]["thumbnails"]["high"]["url"]

            # Başlığı QLabel içine yaz
            self.ui.title_label.setText(title)

            # Thumbnail'i QLabel içine ekle
            img_data = requests.get(thumbnail_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)

            self.ui.thumbnail_label.setPixmap(pixmap)
            self.ui.thumbnail_label.setScaledContents(False)  # Resmi tam oturt
        else:
            self.ui.title_label.setText("Video bulunamadı!")
            self.ui.thumbnail_label.clear()


    def create_video_entry(self, video_title):
        """
        Bu fonksiyon, her indirilen film için bir başlık ve bir ilerleme çubuğu oluşturur.

        :param video_title: Video başlığını belirler.
        """
        # Yeni bir video için frame oluştur
        list_media_frame = QtWidgets.QFrame()
        list_media_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        list_media_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        # Vertical layout ekle
        self.ui.verticalLayout_8 = QtWidgets.QVBoxLayout(list_media_frame)

        # Başlık (title) etiketi oluştur
        list_film_title = QtWidgets.QLabel(list_media_frame)
        list_film_title.setMinimumSize(QtCore.QSize(0, 30))
        list_film_title.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(9)
        list_film_title.setStyleSheet("color: white;")
        list_film_title.setText(video_title)  # Başlık olarak video başlığını kullan
        list_film_title.setObjectName("list_film_title")
        self.ui.verticalLayout_8.addWidget(list_film_title)

        # İlerleme çubuğu oluştur
        progressBar = QtWidgets.QProgressBar(self.ui.list_media_frame)
        progressBar.setMaximumSize(QtCore.QSize(16777215, 30))
        progressBar.setStyleSheet("color: white;")
        progressBar.setProperty("value", 0)  # Başlangıç değeri
        progressBar.setObjectName("progressBar")
        self.ui.verticalLayout_8.addWidget(progressBar)

        # Frame'i sağdaki layout'a ekle
        self.ui.verticalLayout_7.addWidget(list_media_frame, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Frame'i kaydırılabilir alana ekle
        self.ui.scrollArea.setWidget(self.ui.list_area)

        # İlgili widget'ı ekleyin
        self.ui.verticalLayout_6.addWidget(self.ui.scrollArea)
        self.ui.verticalLayout_2.addWidget(self.ui.right_menu_content)
        self.ui.verticalLayout.addWidget(self.ui.right_menu_content_frame)
        self.ui.horizontalLayout_2.addWidget(self.ui.right_menu)
        self.ui.horizontalLayout.addWidget(self.ui.central_right)
        self.ui.setCentralWidget(self.ui.centralwidget)

        # Eğer istediğiniz bir şey varsa eklemek için fonksiyona detaylar eklenebilir

    def download_video(self):
        try:
            # URL kontrolü
            url = self.ui.url_entry.text().strip()
            if not url:
                self.show_message("Hata", "Lütfen bir URL girin!")
                return

            # Seçili format ID'sini al
            current_index = self.ui.comboBox.currentIndex()
            if current_index == -1:
                self.show_message("Hata", "Lütfen bir format seçin!")
                return

            format_id = self.ui.comboBox.itemData(current_index)
            if not format_id:
                self.show_message("Hata", "Format ID bulunamadı!")
                return

            # Dosya konumu seçme dialogu
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.Directory)
            file_dialog.setOption(QFileDialog.ShowDirsOnly, True)

            if file_dialog.exec_():
                selected_directory = file_dialog.selectedFiles()[0]

                # Video başlığını al
                with YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'video')
                    # Dosya adından geçersiz karakterleri temizle
                    video_title = "".join(
                        [c for c in video_title if c.isalpha() or c.isdigit() or c in ' -_.']).rstrip()

                # Format türüne göre dosya uzantısını belirle
                is_audio_only = "MP3" in self.ui.comboBox.currentText()
                file_extension = 'mp3' if is_audio_only else 'mp4'

                # Tam dosya yolu oluştur
                output_path = os.path.join(selected_directory, f"{video_title}.{file_extension}")

                # İndirme seçeneklerini yapılandır
                ydl_opts = {
                    'format': format_id,
                    'outtmpl': output_path,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self.download_progress_hook],
                }

                # MP3 için ek ayarlar
                if is_audio_only:
                    ydl_opts.update({
                        'extractaudio': True,
                        'audioformat': 'mp3',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })


                try:
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    self.show_message("Başarılı", f"İndirme tamamlandı!\nKonum: {output_path}")
                except Exception as e:
                    self.show_message("Hata", f"İndirme sırasında hata oluştu: {str(e)}")


            self.create_video_entry(video_title)

        except Exception as e:
            self.show_message("Hata", f"Beklenmeyen bir hata oluştu: {str(e)}")
            print(f"Hata detayı: {str(e)}")
            import traceback
            traceback.print_exc()

    def show_message(self, title, message):
        """Mesaj kutusu göster"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)

    def download_progress_hook(self, d):
        """İndirme ilerleme durumunu takip et"""
        if d['status'] == 'downloading':
            # İndirme yüzdesi hesapla
            total_bytes = d.get('total_bytes')
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                # Eğer bir progress bar'ınız varsa burada güncelleyebilirsiniz
                # self.ui.progressBar.setValue(int(progress))
                print(f"İndirme ilerleme: {progress:.1f}%")

    def clear_list(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.setWindowTitle("MyTube")
    window.show()
    sys.exit(app.exec_())