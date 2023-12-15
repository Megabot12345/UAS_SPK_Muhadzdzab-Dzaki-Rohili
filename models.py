from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class LP(Base):
    __tablename__ = "tbl_laptop"
    id = Column(Integer, primary_key=True)
    brand = Column(String)
    ram = Column(String)
    cpu = Column(String)
    gpu = Column(String)
    battery = Column(String)
    harga = Column(String)
    ukuran_layar = Column(String)

    def __repr__(self):
        return f"(brand={self.brand!r}, ram={self.ram!r}, cpu={self.cpu!r}, gpu={self.gpu!r}, battery={self.battery!r}, harga={self.harga!r}, ukuran_layar={self.ukuran_layar!r})"