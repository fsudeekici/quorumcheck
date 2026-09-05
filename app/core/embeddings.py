"""
Embedding katmani.

TASARIM KARARI (mulakatta sorulacak sey): Neden gercek bir embedding
modeli (OpenAI, Voyage AI - Anthropic'in onerdigi embedding partneri)
degil de HashingVectorizer?

1. API key / maliyet gerektirmeden calisiyor - portfolyo projesinde
   herkesin calistirip test edebilmesi onemli.
2. STATELESS: gercek bir corpus'a "fit" edilmesi gerekmiyor. TF-IDF
   kullansaydik, yeni bir return_record geldiginde kelime dagarcigi
   degismis olabilirdi ve tum corpus'u yeniden fit etmemiz gerekirdi.
   HashingVectorizer boyle bir sorun yasamaz, herhangi bir metni
   aninda sabit boyutlu bir vektore cevirir.
3. Tradeoff: bu KELIME ORTUSMESI bazli, semantik anlama sahip degil
   ("iade" ve "geri gonderim" farkli kelimeler oldugu icin yakin
   vektor URETMEZ). Gercek bir semantic embedding modeline gecmek
   icin sadece bu dosyadaki embed() fonksiyonunu degistirmek yeterli
   - RAG katmani (rag.py) hangi embedding kullanildigini bilmez.
"""
from sklearn.feature_extraction.text import HashingVectorizer

EMBEDDING_DIM = 256

_vectorizer = HashingVectorizer(n_features=EMBEDDING_DIM, alternate_sign=False, norm="l2")


def embed(text: str) -> list[float]:
    """Herhangi bir metni sabit boyutlu (256) bir vektore cevirir."""
    vector = _vectorizer.transform([text])
    return vector.toarray()[0].tolist()
