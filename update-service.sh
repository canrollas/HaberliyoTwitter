#!/bin/bash

# Log fonksiyonu
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Hata kontrolü için fonksiyon
check_error() {
    if [ $? -ne 0 ]; then
        log "HATA: $1"
        exit 1
    fi
}

# Ana dizine git
cd "$(dirname "$0")"
check_error "Proje dizinine geçilemedi"

while true; do
    log "Güncellemeler kontrol ediliyor..."
    
    # Remote'dan son değişiklikleri getir
    git fetch origin master
    check_error "Git fetch başarısız"
    
    # Yerel ve remote commit'leri karşılaştır
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/master)
    
    # Eğer güncelleme varsa
    if [ "$LOCAL" != "$REMOTE" ]; then
        log "Güncelleme bulundu!"
        
        # Servisleri durdur
        log "Servisler durduruluyor..."
        docker-compose down
        check_error "Docker compose down başarısız"
        
        # Kullanılmayan imajları temizle
        log "Kullanılmayan Docker imajları temizleniyor..."
        docker image prune -f
        
        # Değişiklikleri çek
        log "Güncellemeler indiriliyor..."
        git pull origin master
        check_error "Git pull başarısız"
        
        # Servisleri yeniden başlat
        log "Servisler yeniden başlatılıyor..."
        docker-compose up -d --build
        check_error "Docker compose up başarısız"
        
        log "Güncelleme başarıyla tamamlandı!"
    else
        log "Yeni güncelleme yok."
    fi
    
    # 10 dakika bekle
    sleep 600
done 