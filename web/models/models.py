from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class KecelakaanKorbanView(db.Model):
    __tablename__ = 'kecelakaan_korban_view'
    id = db.Column(db.Integer, primary_key=True)
    gampong_id = db.Column(db.Integer)
    nama_gampong = db.Column(db.String(255))
    tahun = db.Column(db.Integer)
    jumlah_kecelakaan = db.Column(db.Integer)
    jumlah_meninggal = db.Column(db.Integer)
    luka_berat = db.Column(db.Integer)
    luka_ringan = db.Column(db.Integer)
    total_korban = db.Column(db.Integer)

class JenisKecelakaan(db.Model):
    __tablename__ = 'jenis_kecelakaan'
    id = db.Column(db.Integer, primary_key=True)
    Kecamatan = db.Column(db.String(100))
    Tabrakan = db.Column(db.Integer)
    Terjatuh = db.Column(db.Integer)
    Tertabrak = db.Column(db.Integer)
    Terbalik = db.Column(db.Integer)
    Kecelakaan_Tunggal = db.Column(db.Integer)
    Kecelakaan_Beruntun = db.Column(db.Integer)
    Jumlah = db.Column(db.Integer)
    Tahun = db.Column(db.Integer)

class KorbanUsia(db.Model):
    __tablename__ = 'korban_usia'
    id = db.Column(db.Integer, primary_key=True)
    Kecamatan = db.Column(db.String(100))
    anak_anak = db.Column(db.Integer)
    remaja = db.Column(db.Integer)
    dewasa = db.Column(db.Integer)
    paruh_baya = db.Column(db.Integer)
    lansia = db.Column(db.Integer)
    jumlah = db.Column(db.Integer)
    tahun = db.Column(db.Integer)