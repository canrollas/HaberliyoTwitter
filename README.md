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
- Email: [iletisim@haberliyo.com](mailto:iletisim@haberliyo.com)
