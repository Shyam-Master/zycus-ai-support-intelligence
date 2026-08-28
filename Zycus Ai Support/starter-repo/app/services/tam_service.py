import logging
from collections import defaultdict
from app.schemas.tam import TamBriefResponse
from app.utils.data_loader import DataLoader
from app.services.risk_detector import RiskDetector

logger = logging.getLogger(__name__)

class TamService:
    def __init__(self):
        self.risk_detector = RiskDetector()
        
    def generate_brief(self, account_id: str) -> TamBriefResponse:
        logger.info(f'Generating TAM brief for account: {account_id}')
        
        # Will raise ValueError if not found
        account = DataLoader.get_account(account_id)
        tickets = DataLoader.get_tickets_last_90_days(account_id)
        
        escalation_signals = []
        churn_risk_signals = []
        open_risks = []
        
        category_counts = defaultdict(int)
        
        for t in tickets:
            ticket_id = t.get('ticket_id')
            status = t.get('status', '').strip().lower()
            urgency = t.get('urgency', '').strip().upper()
            cat = t.get('category', 'Unknown')
            
            category_counts[cat] += 1
            
            e_signals = self.risk_detector.detect_escalation(t)
            c_signals = self.risk_detector.detect_churn(t)
            
            escalation_signals.extend(e_signals)
            churn_risk_signals.extend(c_signals)
            
            is_open = status not in ['closed', 'resolved']
            
            # Risk Detection logic
            if c_signals:
                open_risks.append({
                    "risk": "Explicit churn signal",
                    "severity": "High",
                    "evidence_quote": c_signals[0]['evidence_quote'],
                    "ticket_id": ticket_id,
                    "reason": "Customer explicitly mentioned churn-related keywords."
                })
            elif e_signals:
                open_risks.append({
                    "risk": "Explicit escalation signal",
                    "severity": "High",
                    "evidence_quote": e_signals[0]['evidence_quote'],
                    "ticket_id": ticket_id,
                    "reason": "Customer explicitly escalated the issue."
                })
            elif is_open and urgency == 'P1':
                open_risks.append({
                    "risk": "Unresolved P1 Ticket",
                    "severity": "High",
                    "evidence_quote": t.get('subject', ''),
                    "ticket_id": ticket_id,
                    "reason": "Critical P1 issue remains unresolved."
                })
            elif is_open and urgency == 'P2':
                open_risks.append({
                    "risk": "Unresolved P2 Ticket",
                    "severity": "Medium",
                    "evidence_quote": t.get('subject', ''),
                    "ticket_id": ticket_id,
                    "reason": "Major P2 issue remains unresolved."
                })
                
        # Repeated issues risk
        for cat, count in category_counts.items():
            if count >= 3:
                # Find the latest ticket in this category to quote
                latest_t = next((tk for tk in tickets if tk.get('category') == cat), None)
                if latest_t:
                    open_risks.append({
                        "risk": f"Repeated {cat} issues",
                        "severity": "Medium",
                        "evidence_quote": latest_t.get('subject', ''),
                        "ticket_id": latest_t.get('ticket_id'),
                        "reason": f"Account has {count} recent tickets related to {cat}."
                    })

        # Determine Overall Health
        overall_health = "Healthy"
        if any(r['severity'] == 'High' for r in open_risks) or churn_risk_signals:
            overall_health = "At Risk"
        elif any(r['severity'] == 'Medium' for r in open_risks) or escalation_signals:
            overall_health = "Watch"
            
        # Deduplicate open risks by ticket_id and risk to avoid clutter
        unique_risks = []
        seen = set()
        for r in open_risks:
            key = (r['ticket_id'], r['risk'])
            if key not in seen:
                seen.add(key)
                unique_risks.append(r)

        # Generate Executive Summary
        account_name = account.get('company', 'Unknown')
        tier = account.get('plan_tier', 'Unknown')
        recent_ticket_count = len(tickets)
        
        summary = f"{account_name} is a {tier} tier customer with {recent_ticket_count} tickets in the last 90 days. "
        summary += f"The overall account health is currently marked as {overall_health}. "
        
        if overall_health == "At Risk":
            summary += "Immediate attention is required due to high-severity risks or churn signals."
        elif overall_health == "Watch":
            summary += "There are active issues or escalations that require monitoring."
        else:
            summary += "No significant open support risks were identified in the available 90-day ticket history."

        # Generate Grounded Talking Points
        talking_points = []
        if overall_health == "Healthy":
            talking_points.append("Conduct a routine account check-in.")
            talking_points.append("Confirm whether there are any new support concerns.")
            if recent_ticket_count > 0:
                talking_points.append("Review the status of the recent support interactions and confirm resolution.")
        else:
            if churn_risk_signals:
                talking_points.append("Address explicit churn concerns and reaffirm value proposition.")
            if escalation_signals:
                talking_points.append("Review escalated issues and provide a clear remediation timeline.")
            for r in unique_risks:
                if r['severity'] == 'High' and "churn" not in r['risk'].lower() and "escalation" not in r['risk'].lower():
                    talking_points.append(f"Provide an update on critical issue {r['ticket_id']}: {r['evidence_quote']}")
            if not talking_points:
                talking_points.append("Discuss current open medium-priority issues to prevent escalation.")

        return TamBriefResponse(
            account_id=account_id,
            account_name=account_name,
            executive_summary=summary,
            open_risks=unique_risks,
            escalation_signals=escalation_signals,
            churn_risk_signals=churn_risk_signals,
            recommended_talking_points=talking_points[:5],
            recent_ticket_count=recent_ticket_count,
            overall_health=overall_health
        )
