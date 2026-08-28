import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)

class RiskDetector:
    ESCALATION_PHRASES = [
        "escalate", "escalation", "unacceptable",
        "sla breach", "breach of sla"
    ]
    
    CHURN_PHRASES = [
        "considering alternatives", "alternative vendor", "switching",
        "cancel", "termination", "renewal concern", "move away", "evaluate other"
    ]

    def _extract_sentence(self, text: str, phrase: str) -> str:
        # Better sentence extraction avoiding false positives
        sentences = re.split(r'(?<=[.!?]) +|\n+', text)
        for s in sentences:
            if phrase in s.lower():
                return s.strip()
        return "" # Fallback

    def detect_signals(self, ticket: dict, phrases: List[str]) -> List[dict]:
        signals = []
        body = ticket.get('body', '')
        body_lower = body.lower()
        for phrase in phrases:
            # Word boundary matching to avoid partial word matches if needed
            # but simple string match is requested, we just use the refined phrases
            if phrase in body_lower:
                quote = self._extract_sentence(body, phrase)
                # Deduplicate same exact signal logic if needed
                if quote and not any(s['signal'] == phrase for s in signals):
                    signals.append({
                        "signal": phrase,
                        "evidence_quote": quote,
                        "ticket_id": ticket.get('ticket_id')
                    })
        return signals

    def detect_escalation(self, ticket: dict) -> List[dict]:
        return self.detect_signals(ticket, self.ESCALATION_PHRASES)

    def detect_churn(self, ticket: dict) -> List[dict]:
        return self.detect_signals(ticket, self.CHURN_PHRASES)
