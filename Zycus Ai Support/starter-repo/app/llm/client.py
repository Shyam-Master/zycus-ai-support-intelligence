import logging
import json
import re
from app.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = settings.api_key
        self.use_fallback = self.api_key == 'dummy_key' or not self.api_key
        
    def generate_triage(self, subject: str, body: str, kb_context: str) -> dict:
        if self.use_fallback:
            logger.info("Using improved deterministic fallback mode for Triage.")
            return self._fallback_triage(subject, body, kb_context)
        else:
            raise NotImplementedError("Real LLM integration not implemented yet.")

    def _fallback_triage(self, subject: str, body: str, kb_context: str) -> dict:
        text = (subject + " " + body).lower()
        kb_lower = kb_context.lower()
        
        # 1. Product Area & 2. Issue Category
        product_area = "General / Unknown"
        issue_category = "General Technical Issue"
        
        # 1A. High Priority: Outages and Major Platform Unavailability
        if "entire platform" in text or "outage" in text or "system down" in text or "complete downtime" in text or "platform unavailable" in text or "application unavailable" in text or "all users unable to access" in text:
            product_area = "Performance / Availability"
            issue_category = "Service Outage / Platform Unavailable"
            
        elif "sso" in text or "login" in text or "log in" in text or "authenticate" in text or "password" in text or "access denied" in text:
            product_area = "Authentication / SSO"
            if "sso" in text and "config" in text:
                issue_category = "SSO configuration issue"
            elif "password" in text or "reset" in text:
                issue_category = "Password/reset issues"
            elif "access denied" in text:
                issue_category = "Access denied"
            else:
                issue_category = "Login failure"
                
        elif "profile" in text or "setting" in text or "preference" in text or "dark mode" in text:
            product_area = "Profile / User Settings"
            if "update profile" in text:
                issue_category = "Unable to update profile"
            elif "saving" in text or "save" in text or "revert" in text:
                issue_category = "Settings not saving"
            else:
                issue_category = "User preference issues"
                
        elif "billing" in text or "payment" in text or "invoice" in text or "pricing" in text or " plan" in text or "plans" in text:
            # Removed raw 'business' keyword to avoid false positives with 'business operations'
            product_area = "Payments / Billing"
            if "payment" in text and "fail" in text:
                issue_category = "Payment failure"
            elif "invoice" in text:
                issue_category = "Invoice issue"
            elif "pricing" in text or "difference" in text or "plan" in text:
                issue_category = "Pricing / Plan Information"
            else:
                issue_category = "Billing discrepancy"
                
        elif "report" in text or "export" in text or "csv" in text or "pdf" in text or "dashboard" in text or "analyticshub" in text:
            product_area = "Reporting / Analytics"
            if "csv" in text:
                issue_category = "CSV export failure"
            elif "pdf" in text:
                issue_category = "PDF export failure"
            elif "fail" in text or "generate" in text:
                issue_category = "Report generation failure"
            elif "analyticshub" in text:
                product_area = "AnalyticsHub"
                issue_category = "Dashboard/report loading issues"
            else:
                issue_category = "Dashboard/report loading issues"

        elif "slow" in text or "timeout" in text or "down" in text or "unavailable" in text or "latency" in text or "performance" in text:
            product_area = "Performance / Availability"
            if "timeout" in text:
                issue_category = "Timeout"
            elif "unavailable" in text:
                issue_category = "Service unavailable"
            else:
                issue_category = "Performance / Latency"

        elif "cloudsync" in text or "webhook" in text or "integration" in text or "snowflake" in text:
            if "cloudsync" in text:
                product_area = "CloudSync"
            else:
                product_area = "Performance / Integrations"
            if "webhook" in text:
                issue_category = "Webhook Failure"
            elif "snowflake" in text:
                issue_category = "Snowflake Integration"
            else:
                issue_category = "Integration Error"
                
        elif "databridge" in text:
            product_area = "DataBridge Pro"
            issue_category = "Data Pipeline Error"
        elif "workflowengine" in text:
            product_area = "WorkflowEngine"
            issue_category = "Workflow Execution Error"
        elif "securevault" in text:
            product_area = "SecureVault"
            issue_category = "Key Management Error"
        else:
            product_area = "General / Unknown"
            if "ui" in text or "interface" in text:
                issue_category = "UI issues"
            elif "error" in text:
                issue_category = "Unknown errors"
            else:
                issue_category = "Miscellaneous technical problems"

        # 3. Urgency
        urgency = "P3"
        urgency_reason = "the issue appears to have limited impact, affects a single user, or is a general request"
        
        if "entire platform" in text or "all users" in text or "everyone" in text or "security" in text or "critical business" in text:
            urgency = "P1"
            urgency_reason = "the issue explicitly affects all users, critical business functionality, or involves security"
        elif "multiple users" in text or "major functionality" in text or "significant business impact" in text or "no workaround" in text:
            urgency = "P2"
            urgency_reason = "multiple users are affected or major functionality is broken with significant impact"
        elif "explain" in text or "difference" in text or "question" in text or "documentation" in text:
            urgency = "P4"
            urgency_reason = "it is a general question or documentation request"
        elif "ignore all previous" in text:
            # Prompt injection adversarial fallback
            urgency = "P3"
            urgency_reason = "adversarial/ambiguous input detected without genuine critical impact"
            
        # 4. Recommended Team
        team = "General Technical Support"
        if product_area == "Authentication / SSO":
            team = "Identity & Access Support"
        elif product_area == "Payments / Billing":
            team = "Billing Support"
        elif product_area == "Performance / Availability":
            team = "Platform Engineering"
        elif product_area == "Reporting / Analytics":
            team = "Data Services Team"
        elif product_area == "Profile / User Settings":
            team = "Product Support"

        # 5. Known Issue Patterns
        known_issues = []
        if product_area == "Authentication / SSO" and "new users" in kb_lower:
            known_issues.append("New users cannot authenticate via SSO")
        elif "csv" in text and "limit" in kb_lower:
            known_issues.append("Export limits exceeded")

        # 6. Reasoning Transparency
        reasoning = (
            f"Product Area '{product_area}' was selected because the description relates to {product_area.lower().split('/')[0].strip()}. "
            f"Issue Category '{issue_category}' was chosen to classify the specific failure mode detected. "
            f"Urgency {urgency} was assigned because {urgency_reason}. "
            f"{'Knowledge base evidence confirms a related pattern.' if known_issues else 'No specific known issue patterns were strongly matched in the KB.'}"
        )

        # 7. Draft Response
        draft_response = "Thank you for contacting support. We have received your request and our team is looking into it."
        if product_area == "General / Unknown":
            draft_response = "Thank you for reaching out. Your request is a bit ambiguous, so it has been routed to our general technical team for initial review. We will contact you if more details are needed."
        elif urgency == "P1":
            draft_response = "We acknowledge the critical nature of this issue. Our engineering team has been paged and we are prioritizing a resolution immediately."
        elif product_area == "Payments / Billing":
            draft_response = "Thank you for reaching out regarding your billing inquiry. Our billing team will review your account details shortly."
        elif product_area == "Reporting / Analytics":
            draft_response = "We apologize for the difficulties with reports/exports. Our data team is investigating the underlying queries."
        elif product_area == "Profile / User Settings":
            draft_response = "Thanks for reporting this account preference issue. A product specialist will assist you soon."
        elif product_area == "Authentication / SSO":
            draft_response = "We understand you are experiencing access issues. Identity & Access Support is investigating."

        return {
            "product_area": product_area,
            "issue_category": issue_category,
            "urgency": urgency,
            "reasoning": reasoning,
            "relevant_kb_docs": [], # populated in service
            "known_issue_patterns": known_issues,
            "recommended_team": team,
            "draft_response": draft_response
        }
