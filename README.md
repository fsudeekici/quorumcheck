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

## Kurulum (yerel)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```