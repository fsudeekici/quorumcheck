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

```
Yeni kayıt → [Validator 1, Validator 2, ... Validator N] (paralel, RAG+LLM)
           → Quorum Aggregator (çoğunluk oyu + CAP tradeoff)
           → PostgreSQL (multi-tenant)
```

CAP tradeoff kararı `app/core/quorum.py` içinde açıkça kodlanmıştır:
quorum sağlanamadığında CP modu karar vermeyi reddeder (`needs_review`),
AP modu elindeki oyla best-effort karar verir.

## Stack

FastAPI, PostgreSQL, Redis, Celery, RAG (embedding + vector search), LLM API, Docker Compose.

## Haftalık ilerleme (branch stratejisi)

Her hafta ayrı bir feature branch'te geliştirilir, hafta sonunda
`main`'e PR ile merge edilir:

| Branch | İçerik |
|---|---|
| `week1-planning` | Consensus/CAP teorisi, mimari, multi-tenant şema tasarımı |
| `week2-skeleton` | FastAPI + Docker + PostgreSQL iskeleti, sentetik veri üretici |
| `week3-single-validator` | Tek validator worker + RAG (tek-LLM baseline) |
| `week4-consensus` | Celery + Redis ile N validator paralel, quorum/timeout/fallback |
| `week5-evaluation` | Consensus vs tek-LLM precision/recall/F1 karşılaştırması |
| `week6-polish` | Cilalama, CI/CD, README, CV güncelleme |

Her branch kendi PR'ında açıklanır (ne yapıldı, neden), böylece
`main`'in geçmişi haftalık ilerlemenin okunabilir bir kaydı olur.

## Kurulum (yerel)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```
