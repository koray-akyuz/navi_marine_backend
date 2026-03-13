import os
import subprocess

def ingest_geospatial_data(file_path, table_name):
    """
    ogr2ogr aracını kullanarak uzaysal veriyi PostGIS'e yükler.
    """
    db_conn = "PG:host=localhost user=postgres password=postgres dbname=navi_marine"
    
    # Komut açıklaması:
    # -overwrite: Tablo varsa üstüne yazar
    # -progress: Yükleme durumunu gösterir
    # -nlt PROMOTE_TO_MULTI: Poligonları MultiPolygon'a zorlar (standartlaştırma)
    # -lco GEOMETRY_NAME=geom: Kolon ismini 'geom' yapar
    
    command = [
        "ogr2ogr",
        "-f", "PostgreSQL",
        db_conn,
        file_path,
        "-nln", table_name,
        "-overwrite",
        "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "GEOMETRY_NAME=geom",
        "-t_srs", "EPSG:4326",
        "-progress"
    ]

    try:
        print(f"🚀 {table_name} tablosu yükleniyor...")
        subprocess.run(command, check=True)
        print(f"✅ {table_name} başarıyla yüklendi.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    # İndirdiğin dosyanın yolu (Örn: ne_10m_ocean.shp)
    shapefile_path = "/Users/koray/Downloads/ne_50m_ocean/ne_50m_ocean.shp"
    ingest_geospatial_data(shapefile_path, "sea_areas")