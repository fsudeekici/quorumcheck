"""
LLM'e "bu kayit gecerli mi" diye soran istemci.

Yapilandirilmis (JSON) cikti istiyoruz cunku bu ciktiyi hem DB'ye
kaydedecegiz hem de Hafta 4'te N validator'in oylarini otomatik
sayacagiz - serbest metin parse etmek kirilgan olurdu.
"""
import json
from dataclasses import dataclass

import anthropic

from app.core.config import settings

SYSTEM_PROMPT = """Sen bir e-ticaret iade doğrulama asistanısın. Sana bir iade kaydı ve \
uyulması gereken iş kuralları verilecek. Kaydın bu kurallara uyup uymadığını değerlendir.

SADECE aşağıdaki formatta, başka hiçbir metin eklemeden bir JSON nesnesi döndür:
{"decision": "approved" | "rejected" | "uncertain", "confidence": 0.0-1.0, "reasoning": "kısa gerekçe"}
"""


@dataclass
class LlmDecision:
    decision: str
    confidence: float
    reasoning: str


def _build_user_prompt(context: str, rules: list[str]) -> str:
    rules_block = "\n".join(f"- {r}" for r in rules) if rules else "(bu tenant için tanımlı kural bulunamadı)"
    return f"İade kaydı:\n{context}\n\nUyulması gereken kurallar:\n{rules_block}"


def decide_validation(context: str, rules: list[str]) -> LlmDecision:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(context, rules)}],
    )

    raw_text = response.content[0].text
    parsed = json.loads(raw_text)

    return LlmDecision(
        decision=parsed["decision"],
        confidence=float(parsed["confidence"]),
        reasoning=parsed["reasoning"],
    )
