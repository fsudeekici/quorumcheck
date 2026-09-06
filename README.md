# QuorumCheck

Konsensüs tabanlı dağıtık veri doğrulama motoru. Sahte e-ticaret
iade/sipariş verisi üzerinde, N paralel LLM validator worker'ının RAG
ile kural tabanlı karar verdiği ve bir quorum/aggregator'ın çoğunluk
oyu + CAP theorem tradeoff'uyla nihai kararı verdiği bir sistem.

## Neden bu proje

Distributed systems (CAP theorem, consensus, quorum) ve LLM/RAG'i tek
bir sistemde birleştirip hem teoriyi hem pratik tooling'i (Docker,
Redis, Celery, async, multi-tenant Postgres) göstermek için.

## Mimari

Yeni kayıt → [Validator 1, Validator 2, ... Validator N] (paralel, RAG+LLM)
→ Quorum Aggregator (çoğunluk oyu + CAP tradeoff)
→ PostgreSQL (multi-tenant)


CAP tradeoff kararı `app/core/quorum.py` içinde açıkça kodlanmıştır:
quorum sağlanamadığında CP modu karar vermeyi reddeder (`needs_review`),
AP modu elindeki oyla best-effort karar verir.

## Stack

FastAPI, PostgreSQL, Redis, Celery, RAG (embedding + vector search), LLM API, Docker Compose.

## Geliştirme aşamaları (branch stratejisi)

Her aşama ayrı bir feature branch'te geliştirilir, tamamlanınca
`main`'e PR ile merge edilir. Branch adları içeriğe göre isimlendirilir
(hafta numarası yerine ne yapıldığını anlatır):

| Branch | İçerik |
|---|---|
| `feat/consensus-architecture-planning` | Consensus/CAP teorisi, mimari, multi-tenant şema tasarımı |
| `feat/fastapi-docker-postgres-skeleton` | FastAPI + Docker + PostgreSQL iskeleti, sentetik veri üretici |
| `feat/single-validator-rag-baseline` | Tek validator worker + RAG (tek-LLM baseline) |
| `feat/celery-quorum-consensus` | Celery + Redis ile N validator paralel, quorum/timeout/fallback |
| `feat/consensus-evaluation-metrics` | Consensus vs tek-LLM precision/recall/F1 karşılaştırması |
| `chore/polish-ci-cd-docs` | Cilalama, CI/CD, README, CV güncelleme |

Her branch kendi PR'ında açıklanır (ne yapıldı, neden), böylece
`main`'in geçmişi ilerlemenin okunabilir bir kaydı olur.

## Kurulum (yerel, Docker olmadan)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

Not: `scripts/` altındaki script'leri çalıştırırken `PYTHONPATH=.`
gerekli, aksi halde `app` paketi bulunamaz (`ModuleNotFoundError`).

## Docker ile çalıştırma

```bash
cp .env.example .env
docker compose up --build
```

API `http://localhost:8000/health` üzerinden ayakta olduğunu doğrular.
Tablo oluşturma FastAPI `startup` event'inde otomatik yapılır (dev
kolaylığı; prod'da Alembic migration'a geçilecek).

## N validator paralel + quorum consensus (Hafta 4)

```bash
docker compose up --build   # api + worker + postgres + redis birlikte ayağa kalkar
curl -X POST http://localhost:8000/returns/1/validate-consensus
```

`app/core/config.py` içindeki `CAP_MODE` (`CP` veya `AP`) quorum
sağlanamadığında (timeout, LLM hatası, yetersiz oy) sistemin ne
yapacağını belirler — `app/core/quorum.py`'deki `resolve_consensus()`
fonksiyonu bu kararı somut kod olarak uygular.

`tests/test_aggregator.py`, Celery'nin `task_always_eager` modunu
kullanarak gerçek Redis/worker kurmadan (CI'da da çalışacak şekilde)
quorum sağlanan/sağlanamayan ve CP/AP senaryolarını doğrular.

## Sentetik veri üretme

```bash
PYTHONPATH=. python scripts/generate_synthetic_data.py --tenants 2 --orders 50 --violation-rate 0.2
```

`--violation-rate`, "iade tutarı sipariş tutarını aşamaz" kuralının ne
sıklıkla kasıtlı ihlal edileceğini belirler — Hafta 3+'ta validator
worker'ların bu ihlalleri yakalayıp yakalamadığını ölçmek için kullanılacak.

## Tek validator + RAG baseline (Hafta 3)

```bash
PYTHONPATH=. python scripts/embed_rules.py     # kuralları embed'ler
# ANTHROPIC_API_KEY'i .env dosyasına ekle, sonra:
curl -X POST http://localhost:8000/returns/1/validate
```

Embedding katmanı `HashingVectorizer` (scikit-learn) kullanıyor —
kelime örtüşmesi bazlı, semantik anlama sahip değil, ama API key
gerektirmiyor ve stateless (yeni metinler için yeniden fit gerekmiyor).
Gerçek bir semantic embedding modeline (örn. Voyage AI) geçmek için
sadece `app/core/embeddings.py` değişir, RAG/validator katmanları
etkilenmez — bu ayrım kasıtlı bir mimari karar.
