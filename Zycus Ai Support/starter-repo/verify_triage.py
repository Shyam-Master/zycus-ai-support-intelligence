import sys
from app.services.triage_service import TriageService
from app.schemas.triage import TriageRequest

def main():
    service = TriageService()
    tests = [
        {
            "name": "1. Critical SSO outage",
            "subject": "All users locked out",
            "body": "SSO configuration broke and all users are denied access.",
            "expected_urgency": "P1",
            "expected_area": "Authentication / SSO",
        },
        {
            "name": "2. Random meaningless text",
            "subject": "asdf",
            "body": "what even is this",
            "expected_urgency": "P3",
            "expected_area": "General / Unknown",
            "expected_team": "General Technical Support"
        },
        {
            "name": "3. Profile settings failure",
            "subject": "Settings not saving",
            "body": "When I try to update my profile, it doesn't save.",
            "expected_area": "Profile / User Settings",
        },
        {
            "name": "4. Report export failure",
            "subject": "CSV export failure",
            "body": "I cannot export the latest report to CSV.",
            "expected_area": "Reporting / Analytics",
        },
        {
            "name": "5. Payment failure affecting many users",
            "subject": "Payment gateway down",
            "body": "Multiple users are reporting that the payment fails.",
            "expected_urgency": "P2",
            "expected_area": "Payments / Billing",
        },
        {
            "name": "6. Entire platform unavailable",
            "subject": "Entire platform is down",
            "body": "All users are unable to access the platform. The application is completely unavailable and our business operations are blocked.",
            "expected_urgency": "P1",
            "expected_area": "Performance / Availability",
            "expected_team": "Platform Engineering"
        },
        {
            "name": "7. Minor UI problem",
            "subject": "UI issue",
            "body": "The button is misaligned.",
            "expected_urgency": "P3",
            "expected_area": "General / Unknown",
        },
        {
            "name": "8. Unknown technical issue",
            "subject": "Weird error",
            "body": "I got an unknown error on the dashboard.",
            "expected_area": "Reporting / Analytics", # error on dashboard goes to reporting
        }
    ]

    failed = 0
    print("Running Automated Triage Tests...\n")
    for t in tests:
        req = TriageRequest(subject=t["subject"], body=t["body"])
        try:
            res = service.triage_ticket(req)
            
            errs = []
            if "expected_urgency" in t and res.urgency != t["expected_urgency"]:
                errs.append(f"Expected urgency {t['expected_urgency']} but got {res.urgency}")
            if "expected_area" in t and res.product_area != t["expected_area"]:
                errs.append(f"Expected area {t['expected_area']} but got {res.product_area}")
            if "expected_team" in t and res.recommended_team != t["expected_team"]:
                errs.append(f"Expected team {t['expected_team']} but got {res.recommended_team}")
                
            if errs:
                print(f"[FAIL] {t['name']}")
                for e in errs:
                    print(f"       - {e}")
                failed += 1
            else:
                print(f"[PASS] {t['name']}")
                
        except Exception as ex:
            print(f"[ERROR] {t['name']}: {str(ex)}")
            failed += 1

    print(f"\nTotal: {len(tests)} | Passed: {len(tests) - failed} | Failed: {failed}")
    if failed > 0:
        sys.exit(1)
        
if __name__ == '__main__':
    main()
