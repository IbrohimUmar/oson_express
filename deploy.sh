#!/bin/bash

# Proje dizinine git
cd /home/ozar

# En son kodları GitHub'dan çek
echo "Kodlar çekiliyor..."
git pull origin main || { echo "Git pull başarısız!"; exit 1; }

# Virtual environment'ı aktifleştir
echo "Virtual environment aktif ediliyor..."
source /home/ozar/venv/bin/activate || { echo "Virtual environment aktifleştirilemedi!"; exit 1; }

# Migrasyonları çalıştır
echo "Migrasyonlar uygulanıyor..."
python manage.py migrate || { echo "Migrasyon işlemi başarısız!"; exit 1; }

# Statik dosyaları topla
#echo "Statik dosyalar toplanıyor..."
#python manage.py collectstatic --noinput || { echo "Statik dosyalar toplanamadı!"; exit 1; }

# Servisi yeniden başlat
echo "Uygulama yeniden başlatılıyor..."
systemctl restart ozar.service || { echo "Servis yeniden başlatılamadı!"; exit 1; }

echo "Deploy işlemi başarıyla tamamlandı!"