import json
from datetime import datetime, timedelta
from app.utils.data_loader import DataLoader
from app.services.risk_detector import RiskDetector
from collections import defaultdict

def audit():
    accounts = DataLoader.load_accounts()
    all_tickets = DataLoader.load_tickets()
    rd = RiskDetector()
    
    # 90-day logic
    valid_tickets = [t for t in all_tickets if '_created_at_dt' in t]
    max_date = max(t['_created_at_dt'] for t in valid_tickets)
    cutoff = max_date - timedelta(days=90)
    
    acc_map = {a['account_id']: a['company'] for a in accounts}
    
    recent_tickets = [t for t in valid_tickets if t['_created_at_dt'] >= cutoff]
    
    print('=== PART 1: AUDIT RECENT TICKETS ===')
    print(f'Total recent tickets: {len(recent_tickets)}')
    
    for t in recent_tickets:
        aid = t.get('account_id')
        name = acc_map.get(aid, 'Unknown')
        tid = t.get('ticket_id')
        status = t.get('status', '')
        urgency = t.get('urgency', '')
        cat = t.get('category', '')
        
        churn_sigs = rd.detect_churn(t)
        esc_sigs = rd.detect_escalation(t)
        
        is_open = status.lower() not in ['closed', 'resolved']
        
        flags = []
        if churn_sigs: flags.append('CHURN')
        if esc_sigs: flags.append('ESCALATION')
        if urgency in ['P1', 'P2']: flags.append(urgency)
        if is_open: flags.append('OPEN')
        
        if flags:
            print(f'Account: {aid} ({name}) | Ticket: {tid} | Status: {status} | Urg: {urgency} | Cat: {cat} | Flags: {flags}')
            for c in churn_sigs:
                print(f'  CHURN MATCH: {c["signal"]} -> "{c["evidence_quote"]}"')
            for e in esc_sigs:
                print(f'  ESC MATCH: {e["signal"]} -> "{e["evidence_quote"]}"')

    print('\n=== PART 2: INVESTIGATE ACC-3336 ===')
    acc_3336_tickets = [t for t in valid_tickets if t.get('account_id') == 'ACC-3336']
    for t in acc_3336_tickets:
        in_window = t['_created_at_dt'] >= cutoff
        print(f"Ticket: {t.get('ticket_id')} | Created: {t.get('created_at')} | In 90d window: {in_window} | Status: {t.get('status')} | Urg: {t.get('urgency')} | Cat: {t.get('category')} | Subj: {t.get('subject')}")

if __name__ == '__main__':
    audit()
