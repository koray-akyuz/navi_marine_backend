#!/bin/bash

# Proje dizinine git
cd /home/ubuntu/navi_marine_backend || exit

# Temp klasörü oluştur
mkdir -p ./temp_osm && cd ./temp_osm

echo "🌐 OSM Yüksek Çözünürlüklü Su Poligonları indiriliyor (Türkiye odağı)..."
# Not: Geofabrik Türkiye shp paketini kullanacağız
wget -O turkey-latest.shp.zip https://download.geofabrik.de/asia/turkey-latest-free.shp.zip

echo "📦 Dosyalar ayıklanıyor..."
unzip turkey-latest.shp.zip

# ogr2ogr ile PostGIS'e aktar
# gis_osm_water_a_free_1.shp genellikle göller ve deniz kıyılarını içerir
echo "🚀 Veritabanına aktarılıyor (sea_areas tablosu güncelleniyor)..."
ogr2ogr -f "PostgreSQL" "PG:host=localhost user=postgres password=postgres dbname=navi_marine" \
    gis_osm_water_a_free_1.shp \
    -nln sea_areas \
    -overwrite \
    -nlt PROMOTE_TO_MULTI \
    -lco GEOMETRY_NAME=geom \
    -t_srs "EPSG:4326" \
    -progress

echo "✅ İşlem tamamlandı. Geçici dosyalar temizleniyor..."
cd ..
rm -rf ./temp_osm

echo "⚓️ Pruvanız Neta! OSM verisi başarıyla yüklendi."
