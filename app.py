from flask import Flask, jsonify, request
import pymongo
import os
from datetime import datetime, timedelta
from bson.json_util import dumps
import json

app = Flask(__name__)

# MongoDB bağlantısı
def get_db():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = pymongo.MongoClient(mongodb_uri)
    return client.news_db

@app.route("/")
def hello_world():
    return "<p>Initial Backend for Web development!</p>"

@app.route("/api/news", methods=["GET"])
def get_news():
    # Query parametrelerini al
    source = request.args.get("source")
    category = request.args.get("category")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    shared = request.args.get("shared")
    limit = int(request.args.get("limit", 20))  # Varsayılan 20 haber
    skip = int(request.args.get("skip", 0))
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = int(request.args.get("sort_order", -1))  # Varsayılan en yeniden eskiye
    
    # Filtre oluştur
    query_filter = {}
    
    if source:
        # Virgülle ayrılmış birden fazla kaynak filtreleme desteği
        sources = source.split(",")
        if len(sources) > 1:
            query_filter["source"] = {"$in": sources}
        else:
            query_filter["source"] = source
    
    if category:
        # RSS URL'inde kategori genellikle son kısımda olur
        # Bu örnek için RSS URL'inden kategori çıkarıldığı varsayılmıştır
        # Gerçek uygulamada bu veritabanı yapınıza göre ayarlanmalıdır
        query_filter["url"] = {"$regex": f"/{category}", "$options": "i"}
    
    # Tarih aralığı filtreleme
    date_filter = {}
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            date_filter["$gte"] = start_datetime.isoformat()
        except ValueError:
            return jsonify({"error": "Geçersiz başlangıç tarihi formatı. ISO format kullanın (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            date_filter["$lte"] = end_datetime.isoformat()
        except ValueError:
            return jsonify({"error": "Geçersiz bitiş tarihi formatı. ISO format kullanın (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    if date_filter:
        query_filter["created_at"] = date_filter
    
    # Paylaşım durumu filtreleme
    if shared is not None:
        query_filter["shared"] = shared.lower() == "true"
    
    # MongoDB'den haberleri getir
    db = get_db()
    news_collection = db.news
    
    try:
        # Toplam kayıt sayısını al
        total_count = news_collection.count_documents(query_filter)
        
        # Haberleri getir
        cursor = news_collection.find(
            query_filter
        ).sort(
            sort_by, sort_order
        ).skip(skip).limit(limit)
        
        # BSON formatını JSON'a çevir
        news_list = json.loads(dumps(list(cursor)))
        
        # Sonuç formatı
        result = {
            "success": True,
            "count": len(news_list),
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "data": news_list
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/sources", methods=["GET"])
def get_sources():
    """Mevcut haber kaynaklarını listele"""
    db = get_db()
    news_collection = db.news
    
    try:
        # Distinct kaynak listesini getir
        sources = news_collection.distinct("source")
        return jsonify({
            "success": True,
            "count": len(sources),
            "data": sources
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Haber URL'lerinden kategorileri çıkararak listele"""
    db = get_db()
    news_collection = db.news
    
    try:
        # URL'lerden kategorileri çıkar
        all_urls = news_collection.distinct("url")
        categories = set()
        
        for url in all_urls:
            # URL'yi parçalara ayır ve kategori olabilecek kısmı bul
            # Örnek: https://t24.com.tr/rss/haber/gundem -> gundem
            parts = url.split("/")
            if len(parts) >= 5:  # En az 5 parça olmalı (https://domain.com/rss/haber/kategori)
                categories.add(parts[-1])
                if len(parts) >= 6:
                    categories.add(parts[-2])
        
        # Çok kısa ve anlamsız olabilecek parçaları temizle
        filtered_categories = [c for c in categories if len(c) > 3 and not c.startswith("http")]
        
        return jsonify({
            "success": True,
            "count": len(filtered_categories),
            "data": sorted(filtered_categories)
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/news/search", methods=["GET"])
def search_news():
    """Haber içeriklerinde arama yap"""
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Arama sorgusu belirtilmedi."}), 400
    
    limit = int(request.args.get("limit", 20))
    skip = int(request.args.get("skip", 0))
    
    db = get_db()
    news_collection = db.news
    
    try:
        # Başlık ve açıklamada aramamızı sağlayan filtreleme
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }
        
        # Toplam eşleşme sayısını al
        total_count = news_collection.count_documents(search_filter)
        
        # Eşleşen haberleri getir
        cursor = news_collection.find(search_filter).sort("created_at", -1).skip(skip).limit(limit)
        news_list = json.loads(dumps(list(cursor)))
        
        return jsonify({
            "success": True,
            "count": len(news_list),
            "total": total_count,
            "query": query,
            "skip": skip,
            "limit": limit,
            "data": news_list
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

