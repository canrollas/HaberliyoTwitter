<div align="center">
  <img src="assets/haberliyo-logo.png" alt="Haberliyo Logo" width="200"/>
  <h1>🗞️ Haberliyo Twitter Bot</h1>
  <p><strong>Your instant Turkish news aggregator on Twitter | Twitter'da anlık haber bülteni</strong></p>

  [![Twitter Follow](https://img.shields.io/twitter/follow/Haberliyo?style=social)](https://twitter.com/haberliyobulten)
  ![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
  ![License](https://img.shields.io/badge/license-MIT-green)
</div>

---

## 📰 About

Haberliyo is a sophisticated Twitter bot that brings you the latest Turkish news in real-time. By aggregating content from various trusted news sources, it delivers concise, accurate, and timely news updates directly to your Twitter feed.

## ✨ Features

- 🔄 **Real-time Updates**: Continuous monitoring and sharing of breaking news
- 🎯 **Smart Filtering**: Advanced algorithms to filter out duplicate news and ensure quality
- 📱 **Multi-source Integration**: Aggregates news from multiple reliable Turkish news sources
- 🤖 **Fully Automated**: 24/7 operation with automated error handling and recovery
- 📊 **Analytics**: Built-in analytics for tracking engagement and performance

## 🛠️ Technology Stack

- Python 3.8+
- Twitter API v2
- Docker & Docker Compose
- MongoDB
- FastAPI
- Celery
- Redis
- Beautiful Soup 4
- Requests
- Pytest

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Twitter API credentials
- Docker and Docker Compose
- MongoDB instance

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kullanici/haberliyo-twitter.git
   cd haberliyo-twitter
   ```

2. **Docker Installation:**
   ```bash
   docker-compose up -d
   ```

3. **Manual Installation:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Configuration

1. Copy `.env.example` to `.env`
2. Add your Twitter API credentials to `.env`
3. Configure MongoDB connection string in `.env`
4. Adjust other settings in `.env` as needed

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Contact

- Twitter: [@haberliyobulten](https://twitter.com/haberliyobulten)

# Haber API

Bu API, çeşitli haber kaynaklarından toplanan haberleri sorgulamak için tasarlanmıştır. MongoDB veritabanında depolanan haberleri farklı filtrelerle getirmenize olanak tanır.

## Kullanılan Teknolojiler

- Flask
- MongoDB
- Python 3.x

## Kurulum

1. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. MongoDB'nin çalıştığından emin olun ve bağlantı bilgilerini ayarlayın:
   ```bash
   export MONGODB_URI="mongodb://localhost:27017"
   ```

3. Uygulamayı başlatın:
   ```bash
   python app.py
   ```
   
## API Kullanımı

### Haberleri Getirme

**Endpoint:** `GET /api/news`

**Query Parametreleri:**

| Parametre  | Açıklama                                                | Varsayılan Değer |
|------------|--------------------------------------------------------|-----------------|
| source     | Haber kaynağı (virgülle ayrılmış birden fazla kaynak) | -               |
| category   | Haber kategorisi                                        | -               |
| start_date | Başlangıç tarihi (ISO format: YYYY-MM-DDTHH:MM:SS)     | -               |
| end_date   | Bitiş tarihi (ISO format: YYYY-MM-DDTHH:MM:SS)         | -               |
| shared     | Paylaşım durumu (true/false)                           | -               |
| limit      | Sayfalama için limit                                    | 20              |
| skip       | Sayfalama için atlama                                   | 0               |
| sort_by    | Sıralama alanı                                          | created_at      |
| sort_order | Sıralama yönü (-1: azalan, 1: artan)                    | -1              |

**Örnek İstek:**
```
GET /api/news?source=t24,hurriyet&limit=10&start_date=2023-01-01T00:00:00
```

**Örnek Yanıt:**
```json
{
  "success": true,
  "count": 10,
  "total": 245,
  "skip": 0,
  "limit": 10,
  "data": [
    {
      "_id": { "$oid": "60f1e5a3c1d2a1c3d4e5f6a7" },
      "source": "t24",
      "date": "2023-05-01T12:30:45",
      "image": "https://example.com/image.jpg",
      "title": "Örnek Haber Başlığı",
      "description": "Haber içeriği özeti...",
      "created_at": "2023-05-01T12:35:00.000Z",
      "url": "https://t24.com.tr/haber/ornek-haber,123456",
      "last_updated": { "$date": "2023-05-01T12:35:00.000Z" },
      "shared": false
    },
    // ...diğer haberler
  ]
}
```

### Haber Kaynaklarını Listeleme

**Endpoint:** `GET /api/sources`

**Örnek Yanıt:**
```json
{
  "success": true,
  "count": 5,
  "data": ["hurriyet", "milliyet", "cnnturk", "t24", "bbc"]
}
```

### Kategorileri Listeleme

**Endpoint:** `GET /api/categories`

**Örnek Yanıt:**
```json
{
  "success": true,
  "count": 8,
  "data": ["ekonomi", "gundem", "politika", "saglik", "spor", "teknoloji", "turkiye", "yasam"]
}
```

### Haberlerde Arama Yapma

**Endpoint:** `GET /api/news/search`

**Query Parametreleri:**

| Parametre | Açıklama                  | Varsayılan Değer |
|-----------|--------------------------|-----------------|
| q         | Arama sorgusu (gerekli)  | -               |
| limit     | Sayfalama için limit      | 20              |
| skip      | Sayfalama için atlama     | 0               |

**Örnek İstek:**
```
GET /api/news/search?q=ekonomi&limit=5
```

**Örnek Yanıt:**
```json
{
  "success": true,
  "count": 5,
  "total": 42,
  "query": "ekonomi",
  "skip": 0,
  "limit": 5,
  "data": [
    // Arama sonuçları
  ]
}
```

## Haber Objesi Yapısı

MongoDB'de saklanan haber belgeleri aşağıdaki yapıdadır:

```json
{
  "_id": ObjectId,
  "source": String,         // Haber kaynağı (t24, hurriyet, milliyet vb.)
  "date": String,           // Haberin yayınlanma tarihi (orijinal formatta)
  "image": String,          // Haber resmi URL'si
  "title": String,          // Haber başlığı
  "description": String,    // Haber özeti/içeriği
  "created_at": String,     // Veri tabanına eklenme tarihi (ISO format)
  "url": String,            // Haberin tam URL'si
  "last_updated": Date,     // Son güncelleme tarihi
  "shared": Boolean         // Paylaşılma durumu
}
```

## Docker ile Çalıştırma

```bash
docker-compose up -d
```

## Lisans

Bu proje açık kaynak olarak lisanslanmıştır.
