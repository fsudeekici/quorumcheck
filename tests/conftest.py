"""
pytest, bir test klasorune girdiginde herhangi bir test dosyasini
import etmeden ONCE conftest.py'yi calistirir. Bu yuzden DATABASE_URL
gibi "import zamaninda donan" ayarlar burada, tek yerde set edilmeli -
tek tek test dosyalarinin icinde os.environ.setdefault(...) yapmak
import sirasina bagli oldugu icin kirilgandi (bkz. bu dosyanin
eklenmesine sebep olan bug: ilk import edilen test dosyasi DB'yle
ilgisi olmasa bile zincirleme import yuzunden app.core.config'i
tetikliyor ve settings o an ki (yanlis) env'e gore donuyordu).
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
