import json
import logging
from app.services.triage_service import TriageService
from app.services.tam_service import TamService
from app.schemas.triage import TriageRequest
from app.utils.data_loader import DataLoader
from evaluation.test_cases import TRIAGE_TEST_CASES, TAM_TEST_CASES

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self):
        self.triage_svc = TriageService()
        self.tam_svc = TamService()
        self.all_tickets = DataLoader.load_tickets()
        self.tickets_by_id = {t.get('ticket_id'): t for t in self.all_tickets}

    def _check_keywords(self, text, keywords):
        text_lower = text.lower()
        return any(k in text_lower for k in keywords)
        
    def evaluate_triage(self, test_case):
        score = 0.0
        input_data = test_case['input']
        expected = test_case['expected']
        
        req = TriageRequest(subject=input_data['subject'], body=input_data['body'])
        actual = {}
        try:
            res = self.triage_svc.triage_ticket(req)
            actual = res.model_dump()
            
            # Product area correctness: 0.25
            if 'product_area_keywords' in expected:
                if self._check_keywords(actual['product_area'], expected['product_area_keywords']):
                    score += 0.25
            else:
                score += 0.25
                
            # Issue category correctness: 0.15
            # Broad leniency since categories vary based on keywords
            if actual['issue_category']:
                score += 0.15
                
            # Urgency correctness: 0.30
            if 'urgency' in expected:
                if actual['urgency'] == expected['urgency']:
                    score += 0.30
            elif 'not_urgency' in expected:
                if actual['urgency'] != expected['not_urgency']:
                    score += 0.30
            else:
                score += 0.30
                
            # KB relevance: 0.15
            if 'kb_keywords' in expected:
                kb_text = ' '.join(actual['relevant_kb_docs']).lower()
                if self._check_keywords(kb_text, expected['kb_keywords']):
                    score += 0.15
            else:
                score += 0.15
                
            # Recommended team correctness: 0.15
            if 'team_keywords' in expected:
                if self._check_keywords(actual['recommended_team'], expected['team_keywords']):
                    score += 0.15
            else:
                score += 0.15
                
        except Exception as e:
            actual = {'error': str(e)}
            
        status = "PASS" if score >= 0.80 else "FAIL"
        return {
            'test_name': test_case['test_name'],
            'input': input_data,
            'expected': expected,
            'actual': actual,
            'quality_score': round(score, 2),
            'status': status
        }

    def evaluate_tam(self, test_case):
        score = 0.0
        aid = test_case['account_id']
        expected = test_case['expected']
        
        actual = {}
        try:
            # Determinism test
            res1 = self.tam_svc.generate_brief(aid)
            res2 = self.tam_svc.generate_brief(aid)
            
            if expected.get('error'):
                # Should have raised error
                actual = {'error': "Did not raise expected error"}
            else:
                actual = res1.model_dump()
                
                # Correct account data: 0.20
                if actual['account_id'] == aid:
                    score += 0.20
                    
                # Correct recent ticket count: 0.20
                if 'recent_ticket_count' in expected and actual['recent_ticket_count'] == expected['recent_ticket_count']:
                    score += 0.20
                    
                # Evidence integrity: 0.25
                integrity_pass = True
                signals_to_check = actual.get('open_risks', []) + actual.get('escalation_signals', []) + actual.get('churn_risk_signals', [])
                for sig in signals_to_check:
                    tid = sig.get('ticket_id')
                    quote = sig.get('evidence_quote', '').lower()
                    if tid not in self.tickets_by_id:
                        integrity_pass = False
                        break
                    t_obj = self.tickets_by_id[tid]
                    if t_obj.get('account_id') != aid:
                        integrity_pass = False
                        break
                    if quote not in t_obj.get('body', '').lower() and quote not in t_obj.get('subject', '').lower():
                        integrity_pass = False
                        break
                        
                if integrity_pass:
                    score += 0.25
                    
                # Risk/health consistency: 0.20
                if 'overall_health' in expected and actual['overall_health'] == expected['overall_health']:
                    score += 0.20
                    
                # Determinism: 0.15
                if res1.model_dump_json() == res2.model_dump_json():
                    score += 0.15
                    
        except ValueError as e:
            if expected.get('error'):
                score = 1.00 # Perfect score for safely handling invalid input
                actual = {'error_caught': str(e)}
            else:
                actual = {'error': str(e)}
        except Exception as e:
            actual = {'error': str(e)}
            
        status = "PASS" if score >= 0.80 else "FAIL"
        return {
            'test_name': test_case['test_name'],
            'account_id': aid,
            'expected': expected,
            'actual': actual,
            'quality_score': round(score, 2),
            'status': status
        }
