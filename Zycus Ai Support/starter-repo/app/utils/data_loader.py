import json
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from app.config import settings

logger = logging.getLogger(__name__)

class DataLoader:
    @staticmethod
    @lru_cache(maxsize=1)
    def load_accounts():
        with open(settings.data_dir / 'accounts.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    @lru_cache(maxsize=1)
    def load_tickets():
        with open(settings.data_dir / 'tickets.json', 'r', encoding='utf-8') as f:
            tickets = json.load(f)
            for t in tickets:
                if t.get('created_at'):
                    t['_created_at_dt'] = datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
                if t.get('updated_at'):
                    t['_updated_at_dt'] = datetime.fromisoformat(t['updated_at'].replace('Z', '+00:00'))
            return tickets

    @staticmethod
    def get_account(account_id: str):
        accounts = DataLoader.load_accounts()
        for acc in accounts:
            if acc.get('account_id') == account_id:
                return acc
        raise ValueError(f"Account {account_id} not found")

    @staticmethod
    def get_tickets_for_account(account_id: str):
        tickets = DataLoader.load_tickets()
        return [t for t in tickets if t.get('account_id') == account_id]

    @staticmethod
    def get_tickets_last_90_days(account_id: str, reference_date: datetime = None):
        tickets = DataLoader.get_tickets_for_account(account_id)
        if not tickets:
            return []
            
        if reference_date is None:
            all_tickets = DataLoader.load_tickets()
            # Deterministic reference date based on dataset
            valid_tickets = [t for t in all_tickets if '_created_at_dt' in t]
            if valid_tickets:
                max_date = max(t['_created_at_dt'] for t in valid_tickets)
                reference_date = max_date
            else:
                reference_date = datetime.now()
            
        cutoff_date = reference_date - timedelta(days=90)
        
        filtered = [t for t in tickets if t.get('_created_at_dt') and t['_created_at_dt'] >= cutoff_date]
        filtered.sort(key=lambda x: x['_created_at_dt'], reverse=True)
        return filtered
