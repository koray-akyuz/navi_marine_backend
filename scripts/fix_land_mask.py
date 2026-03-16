import subprocess
import os

def run():
    # RDS Connection string
    db_conn = "PG:host=ls-a5ad1b260b195f323cd3b9091ae79e32877778de.cfyc6yasm15y.eu-central-1.rds.amazonaws.com user=dbmasteruser password='ec2;&=6KtFJi9#J{RE1#OC52w5STi8it' dbname=navi_marine"
    
    print("🌍 Türkiye yüksek çözünürlüklü kara sınırı indiriliyor...")
    # GitHub'da güvenilir bir kaynaktan Türkiye sınırını çekelim
    url = "https://raw.githubusercontent.com/alpers/turkey-geojson/master/turkey.json"
    
    try:
        # ogr2ogr ile GeoJSON'ı direkt PostGIS'e aktaralım
        command = [
            "ogr2ogr",
            "-f", "PostgreSQL",
            db_conn,
            f"/vsicurl/{url}",
            "-nln", "land_areas_temp",
            "-overwrite",
            "-nlt", "PROMOTE_TO_MULTI",
            "-lco", "GEOMETRY_NAME=geom",
            "-t_srs", "EPSG:4326"
        ]
        
        print("🚀 Veritabanına aktarılıyor...")
        subprocess.run(command, check=True)
        
        # SQL ile ana tabloya taşıma
        print("🧹 Tablo optimize ediliyor...")
        psql_conn = "postgresql://dbmasteruser:ec2;&=6KtFJi9#J%7BRE1#OC52w5STi8it@ls-a5ad1b260b195f323cd3b9091ae79e32877778de.cfyc6yasm15y.eu-central-1.rds.amazonaws.com:5432/navi_marine"
        subprocess.run(["psql", psql_conn, "-c", "DROP TABLE IF EXISTS land_areas; ALTER TABLE land_areas_temp RENAME TO land_areas; CREATE INDEX idx_land_areas_geom ON land_areas USING GIST(geom);"], check=True)
        
        print("✅ İşlem tamamlandı! Artık Ankara'ya rota çizemeyeceksin kaptan.")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    run()
