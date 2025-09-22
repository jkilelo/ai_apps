# Notification System Implementation Audit Checklist
## Comprehensive Email & SMS Integration for User Signup and Engagement
### *Building a Modern Multi-Channel Notification Infrastructure with MCP Integration*

---

## Executive Summary

This audit document provides a comprehensive bottom-up implementation strategy for integrating email and SMS notifications throughout the user signup and engagement journey. Based on 2025 research, we recommend a multi-layered approach using **SendGrid** for email, **Plivo** for SMS, **Knock** for orchestration, and **MCP servers** for AI integration, ensuring maximum deliverability, compliance, and user engagement.

**Core Strategy**: Implement a notification orchestration layer that unifies email and SMS providers while maintaining flexibility through MCP integration for AI-powered personalization and automation.

---

## 1. Infrastructure Foundation Layer (Critical - Week 1)

### 1.1 Database Schema for Notifications
```sql
-- REQUIREMENT: Extend existing schema with notification tables
-- Notification Templates Table
CREATE TABLE notification_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    channel TEXT CHECK(channel IN ('email', 'sms', 'push', 'in_app', 'slack')),
    subject TEXT,  -- For email
    body_html TEXT,  -- For email HTML
    body_text TEXT NOT NULL,  -- Plain text for SMS/fallback
    variables JSON,  -- Template variables like {{user_name}}
    category TEXT,  -- signup, onboarding, security, marketing
    active BOOLEAN DEFAULT TRUE,

    -- A/B Testing
    variant TEXT DEFAULT 'control',  -- control, variant_a, variant_b
    test_percentage INTEGER DEFAULT 100,

    -- Compliance
    requires_consent BOOLEAN DEFAULT FALSE,
    compliance_category TEXT,  -- transactional, marketing, security

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification Queue Table
CREATE TABLE notification_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER,
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,  -- email address or phone number

    -- Message content
    subject TEXT,
    body_html TEXT,
    body_text TEXT,
    variables JSON,  -- Dynamic content

    -- Scheduling
    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority INTEGER DEFAULT 5,  -- 1-10, 1 being highest

    -- Status tracking
    status TEXT DEFAULT 'pending',  -- pending, processing, sent, failed, cancelled
    provider TEXT,  -- sendgrid, plivo, twilio, etc.
    provider_message_id TEXT,

    -- Retry logic
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_attempt TIMESTAMP,
    error_message TEXT,

    -- Tracking
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    bounced_at TIMESTAMP,
    complained_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES notification_templates(id)
);

-- User Notification Preferences
CREATE TABLE user_notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,

    -- Channel preferences
    email_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    push_enabled BOOLEAN DEFAULT FALSE,
    in_app_enabled BOOLEAN DEFAULT TRUE,

    -- Category preferences
    security_notifications BOOLEAN DEFAULT TRUE,  -- Can't be disabled
    onboarding_notifications BOOLEAN DEFAULT TRUE,
    marketing_notifications BOOLEAN DEFAULT FALSE,
    product_updates BOOLEAN DEFAULT TRUE,
    infrastructure_alerts BOOLEAN DEFAULT TRUE,

    -- Frequency settings
    digest_frequency TEXT DEFAULT 'realtime',  -- realtime, hourly, daily, weekly
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone TEXT DEFAULT 'UTC',

    -- Contact information
    primary_email TEXT,
    verified_email BOOLEAN DEFAULT FALSE,
    backup_email TEXT,
    primary_phone TEXT,
    verified_phone BOOLEAN DEFAULT FALSE,
    phone_country_code TEXT,

    -- Compliance
    marketing_consent BOOLEAN DEFAULT FALSE,
    marketing_consent_date TIMESTAMP,
    gdpr_consent BOOLEAN DEFAULT FALSE,
    gdpr_consent_date TIMESTAMP,

    -- Unsubscribe tokens
    email_unsubscribe_token TEXT UNIQUE,
    sms_unsubscribe_token TEXT UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Notification Events Log
CREATE TABLE notification_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER,
    user_id INTEGER,
    event_type TEXT NOT NULL,  -- sent, delivered, opened, clicked, bounced, complained, unsubscribed
    channel TEXT NOT NULL,
    provider TEXT,

    -- Event details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    metadata JSON,  -- Provider-specific data

    -- Link tracking
    clicked_url TEXT,

    FOREIGN KEY (notification_id) REFERENCES notification_queue(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Provider Configuration
CREATE TABLE notification_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- sendgrid, plivo, twilio, etc.
    channel TEXT NOT NULL,

    -- API Configuration
    api_key TEXT,  -- Encrypted
    api_secret TEXT,  -- Encrypted
    webhook_secret TEXT,  -- For webhook validation

    -- Settings
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 5,

    -- Rate limits
    rate_limit_per_second INTEGER,
    rate_limit_per_minute INTEGER,
    rate_limit_per_hour INTEGER,

    -- Cost tracking
    cost_per_message DECIMAL(10,6),
    monthly_quota INTEGER,
    monthly_usage INTEGER DEFAULT 0,

    -- Configuration
    config JSON,  -- Provider-specific settings

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_queue_status_scheduled ON notification_queue(status, scheduled_for);
CREATE INDEX idx_queue_user_id ON notification_queue(user_id);
CREATE INDEX idx_events_notification ON notification_events(notification_id);
CREATE INDEX idx_events_user ON notification_events(user_id, event_type);
CREATE INDEX idx_preferences_user ON user_notification_preferences(user_id);
```

**Tasks:**
- [ ] Create notification database schema
- [ ] Add foreign key relationships
- [ ] Implement JSON field support
- [ ] Create performance indexes
- [ ] Add triggers for updated_at
- [ ] Set up cascade deletes
- [ ] Create views for reporting
- [ ] Add partitioning for large tables

---

## 2. Provider Integration Layer (Critical - Week 1)

### 2.1 Email Provider Setup - SendGrid
```python
# providers/sendgrid_provider.py
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
import base64
from typing import Dict, List, Optional

class SendGridProvider:
    """SendGrid email provider implementation"""

    def __init__(self, api_key: str):
        self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
        self.from_email = "noreply@infrastructure-audit.com"
        self.from_name = "Infrastructure Audit Platform"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        template_id: Optional[str] = None,
        variables: Optional[Dict] = None,
        attachments: Optional[List] = None,
        headers: Optional[Dict] = None,
        categories: Optional[List[str]] = None,
        send_at: Optional[int] = None,
    ) -> Dict:
        """Send email via SendGrid"""

        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email)
        )

        if template_id:
            # Use SendGrid dynamic template
            message.template_id = template_id
            if variables:
                message.dynamic_template_data = variables
        else:
            message.subject = subject
            message.content = [
                Content("text/plain", body_text),
                Content("text/html", body_html)
            ]

        # Add custom headers
        if headers:
            message.header = headers

        # Add tracking categories
        if categories:
            message.category = categories

        # Schedule send
        if send_at:
            message.send_at = send_at

        # Add attachments
        if attachments:
            for att in attachments:
                attachment = Attachment()
                attachment.file_content = base64.b64encode(att['content']).decode()
                attachment.file_type = att['type']
                attachment.file_name = att['name']
                attachment.disposition = "attachment"
                message.attachment = attachment

        # Add custom headers for tracking
        message.custom_arg = {
            "user_id": str(variables.get('user_id', '')),
            "notification_id": str(variables.get('notification_id', ''))
        }

        try:
            response = self.sg.send(message)
            return {
                "success": True,
                "message_id": response.headers.get('X-Message-Id'),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e, 'status_code', 500)
            }

    async def send_bulk(self, messages: List[Dict]) -> List[Dict]:
        """Send bulk emails"""
        results = []
        for msg in messages:
            result = await self.send_email(**msg)
            results.append(result)
        return results

    async def validate_email(self, email: str) -> bool:
        """Validate email address using SendGrid validation API"""
        # SendGrid email validation endpoint
        response = self.sg.client.validations.email.post(
            request_body={"email": email}
        )
        return response.body.get('result', {}).get('verdict') == 'Valid'
```

### 2.2 SMS Provider Setup - Plivo
```python
# providers/plivo_provider.py
import plivo
from typing import Dict, List, Optional

class PlivoProvider:
    """Plivo SMS provider implementation"""

    def __init__(self, auth_id: str, auth_token: str):
        self.client = plivo.RestClient(auth_id, auth_token)
        self.from_number = "+1234567890"  # Your Plivo number

    async def send_sms(
        self,
        to_phone: str,
        message: str,
        from_number: Optional[str] = None,
        url_callback: Optional[str] = None,
        method: str = "POST",
    ) -> Dict:
        """Send SMS via Plivo"""

        # Format phone number
        if not to_phone.startswith('+'):
            to_phone = f"+{to_phone}"

        try:
            response = self.client.messages.create(
                src=from_number or self.from_number,
                dst=to_phone,
                text=message,
                url=url_callback,
                method=method,
                log=True  # Enable message logging
            )

            return {
                "success": True,
                "message_id": response.message_uuid[0],
                "status": "sent",
                "cost": getattr(response, 'total_amount', None)
            }
        except plivo.exceptions.PlivoRestError as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": e.status_code
            }

    async def send_bulk_sms(self, messages: List[Dict]) -> List[Dict]:
        """Send bulk SMS messages"""
        results = []
        for msg in messages:
            result = await self.send_sms(**msg)
            results.append(result)
        return results

    async def lookup_number(self, phone: str) -> Dict:
        """Lookup phone number information"""
        try:
            response = self.client.lookup.get(phone)
            return {
                "valid": True,
                "carrier": response.carrier,
                "country": response.country_name,
                "format": response.format
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def get_message_status(self, message_id: str) -> Dict:
        """Get SMS delivery status"""
        try:
            response = self.client.messages.get(message_id)
            return {
                "status": response.message_state,
                "delivered_at": response.message_time,
                "cost": response.total_amount
            }
        except Exception as e:
            return {"error": str(e)}
```

**Tasks:**
- [ ] Configure SendGrid API integration
- [ ] Configure Plivo SMS integration
- [ ] Set up Twilio as backup provider
- [ ] Implement provider failover logic
- [ ] Add provider health checks
- [ ] Create provider cost tracking
- [ ] Implement rate limiting per provider
- [ ] Set up webhook endpoints

---

## 3. Authentication & Compliance Layer (Critical - Week 1)

### 3.1 Email Authentication Setup
```python
# auth/email_authentication.py
import dns.resolver
from typing import Dict, List

class EmailAuthentication:
    """Email authentication and compliance setup"""

    def __init__(self, domain: str):
        self.domain = domain

    def generate_spf_record(self, providers: List[str]) -> str:
        """Generate SPF record for domain"""
        spf_includes = []

        # Add provider SPF includes
        provider_spf = {
            'sendgrid': 'include:sendgrid.net',
            'ses': 'include:amazonses.com',
            'mailgun': 'include:mailgun.org',
            'resend': 'include:resend.com'
        }

        for provider in providers:
            if provider in provider_spf:
                spf_includes.append(provider_spf[provider])

        # Build SPF record
        spf = f"v=spf1 {' '.join(spf_includes)} ~all"
        return spf

    def generate_dkim_instructions(self, provider: str) -> Dict:
        """Generate DKIM setup instructions"""
        instructions = {
            'sendgrid': {
                'selector': 's1._domainkey',
                'steps': [
                    'Navigate to SendGrid Settings > Sender Authentication',
                    'Add your domain for authentication',
                    'Copy the DKIM records provided',
                    'Add CNAME records to your DNS'
                ]
            },
            'plivo': {
                'selector': 'plivo._domainkey',
                'steps': [
                    'Access Plivo Console > Messaging > Alphanumeric Sender ID',
                    'Add domain for SMS authentication',
                    'Configure DKIM if using Plivo Email'
                ]
            }
        }

        return instructions.get(provider, {})

    def generate_dmarc_record(self, policy: str = 'quarantine') -> str:
        """Generate DMARC record"""
        dmarc = (
            f"v=DMARC1; "
            f"p={policy}; "
            f"rua=mailto:dmarc@{self.domain}; "
            f"ruf=mailto:forensics@{self.domain}; "
            f"pct=100; "
            f"adkim=s; "
            f"aspf=s"
        )
        return dmarc

    def verify_dns_records(self) -> Dict:
        """Verify DNS authentication records"""
        results = {
            'spf': False,
            'dkim': False,
            'dmarc': False,
            'errors': []
        }

        try:
            # Check SPF record
            spf_answers = dns.resolver.resolve(self.domain, 'TXT')
            for rdata in spf_answers:
                if 'v=spf1' in str(rdata):
                    results['spf'] = True
                    break

            # Check DMARC record
            dmarc_domain = f'_dmarc.{self.domain}'
            dmarc_answers = dns.resolver.resolve(dmarc_domain, 'TXT')
            for rdata in dmarc_answers:
                if 'v=DMARC1' in str(rdata):
                    results['dmarc'] = True
                    break

            # Check DKIM (SendGrid example)
            dkim_selector = f's1._domainkey.{self.domain}'
            try:
                dkim_answers = dns.resolver.resolve(dkim_selector, 'CNAME')
                results['dkim'] = True
            except:
                results['errors'].append('DKIM record not found')

        except Exception as e:
            results['errors'].append(str(e))

        return results
```

### 3.2 Compliance Management
```python
# compliance/notification_compliance.py
from datetime import datetime, timedelta
import hashlib
import secrets

class NotificationCompliance:
    """Handle GDPR, CAN-SPAM, and other compliance requirements"""

    def __init__(self, db_session):
        self.db = db_session

    async def check_consent(self, user_id: int, notification_type: str) -> bool:
        """Check if user has consented to receive notifications"""
        prefs = await self.db.query(UserNotificationPreferences).filter(
            UserNotificationPreferences.user_id == user_id
        ).first()

        if not prefs:
            return False

        # Security notifications always allowed
        if notification_type == 'security':
            return True

        # Check marketing consent
        if notification_type == 'marketing':
            return prefs.marketing_consent and prefs.marketing_notifications

        # Check GDPR consent
        if notification_type in ['product_updates', 'onboarding']:
            return prefs.gdpr_consent

        return True

    def generate_unsubscribe_link(self, user_id: int, channel: str) -> str:
        """Generate one-click unsubscribe link"""
        token = secrets.token_urlsafe(32)

        # Store token in database
        # ... database update code ...

        return f"https://api.infrastructure-audit.com/unsubscribe/{channel}/{token}"

    def add_compliance_headers(self, message: Dict, user_id: int) -> Dict:
        """Add required compliance headers to email"""
        # List-Unsubscribe header (RFC 2369)
        unsubscribe_url = self.generate_unsubscribe_link(user_id, 'email')

        headers = {
            'List-Unsubscribe': f'<{unsubscribe_url}>',
            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
            'X-Auto-Response-Suppress': 'DR, RN, NRN, OOF, AutoReply',
            'Precedence': 'bulk'
        }

        message['headers'] = {**message.get('headers', {}), **headers}

        # Add unsubscribe link to email footer
        footer_html = f"""
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666;">
            <p>Infrastructure Audit Platform | 123 Tech Street, San Francisco, CA 94102</p>
            <p>
                <a href="{unsubscribe_url}">Unsubscribe</a> |
                <a href="https://infrastructure-audit.com/preferences">Update Preferences</a> |
                <a href="https://infrastructure-audit.com/privacy">Privacy Policy</a>
            </p>
            <p>This email was sent to {{{{email}}}} because you signed up for Infrastructure Audit Platform.</p>
        </div>
        """

        message['body_html'] = message.get('body_html', '') + footer_html

        return message

    async def handle_complaint(self, user_id: int, channel: str, reason: str):
        """Handle spam complaints"""
        # Mark user as complained
        await self.db.execute(
            """
            UPDATE user_notification_preferences
            SET {channel}_enabled = FALSE
            WHERE user_id = :user_id
            """,
            {"channel": channel, "user_id": user_id}
        )

        # Log complaint
        await self.log_compliance_event(
            user_id=user_id,
            event_type='complaint',
            channel=channel,
            metadata={'reason': reason}
        )

        # If complaint rate > 0.1%, alert admin
        complaint_rate = await self.calculate_complaint_rate()
        if complaint_rate > 0.001:
            await self.alert_admin(f"High complaint rate: {complaint_rate*100}%")
```

**Tasks:**
- [ ] Configure SPF records for domain
- [ ] Set up DKIM authentication
- [ ] Implement DMARC with p=quarantine
- [ ] Add BIMI record for brand indicators
- [ ] Implement GDPR consent management
- [ ] Add CAN-SPAM compliance headers
- [ ] Create one-click unsubscribe
- [ ] Set up complaint feedback loops

---

## 4. Orchestration Layer (Important - Week 2)

### 4.1 Notification Orchestrator with Knock
```python
# orchestration/knock_orchestrator.py
import httpx
from typing import Dict, List, Optional
import json

class KnockOrchestrator:
    """Knock.app notification orchestration"""

    def __init__(self, api_key: str, environment: str = "production"):
        self.api_key = api_key
        self.base_url = "https://api.knock.app/v1"
        self.environment = environment
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def identify_user(self, user: Dict) -> Dict:
        """Identify/update user in Knock"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/users/{user['id']}",
                headers=self.headers,
                json={
                    "email": user.get('email'),
                    "phone_number": user.get('phone'),
                    "name": user.get('full_name'),
                    "properties": {
                        "persona": user.get('persona'),
                        "organization_id": user.get('organization_id'),
                        "signup_date": user.get('created_at')
                    }
                }
            )
            return response.json()

    async def trigger_workflow(
        self,
        workflow: str,
        recipients: List[str],
        data: Dict,
        tenant: Optional[str] = None,
        cancellation_key: Optional[str] = None
    ) -> Dict:
        """Trigger notification workflow"""

        payload = {
            "workflow": workflow,
            "recipients": recipients,
            "data": data,
            "environment": self.environment
        }

        if tenant:
            payload["tenant"] = tenant

        if cancellation_key:
            payload["cancellation_key"] = cancellation_key

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/workflows/trigger",
                headers=self.headers,
                json=payload
            )
            return response.json()

    async def get_user_preferences(self, user_id: str) -> Dict:
        """Get user notification preferences"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{user_id}/preferences",
                headers=self.headers
            )
            return response.json()

    async def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Update user notification preferences"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/users/{user_id}/preferences",
                headers=self.headers,
                json=preferences
            )
            return response.json()

    async def cancel_workflow(self, cancellation_key: str) -> Dict:
        """Cancel a scheduled workflow"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/workflows/cancel/{cancellation_key}",
                headers=self.headers
            )
            return response.json()
```

### 4.2 Workflow Definitions
```python
# orchestration/signup_workflows.py
from enum import Enum
from typing import Dict, List

class SignupWorkflows(Enum):
    """Signup notification workflows"""

    # Immediate notifications
    WELCOME_EMAIL = "welcome_email"
    VERIFY_EMAIL = "verify_email"
    VERIFY_PHONE = "verify_phone"

    # Onboarding sequence
    ONBOARDING_DAY_1 = "onboarding_day_1"
    ONBOARDING_DAY_3 = "onboarding_day_3"
    ONBOARDING_DAY_7 = "onboarding_day_7"
    ONBOARDING_DAY_14 = "onboarding_day_14"

    # Progressive profiling
    COMPLETE_PROFILE = "complete_profile"
    SETUP_INFRASTRUCTURE = "setup_infrastructure"
    CONNECT_AI = "connect_ai"
    INVITE_TEAM = "invite_team"

    # Re-engagement
    INACTIVE_3_DAYS = "inactive_3_days"
    INACTIVE_7_DAYS = "inactive_7_days"
    ABANDONED_SIGNUP = "abandoned_signup"

class SignupNotificationService:
    """Manage signup notification workflows"""

    def __init__(self, orchestrator: KnockOrchestrator):
        self.orchestrator = orchestrator

    async def trigger_signup_sequence(self, user: Dict):
        """Trigger complete signup notification sequence"""

        # 1. Immediate welcome email
        await self.orchestrator.trigger_workflow(
            workflow=SignupWorkflows.WELCOME_EMAIL.value,
            recipients=[user['id']],
            data={
                "user_name": user.get('full_name', user['email'].split('@')[0]),
                "email": user['email'],
                "signup_date": user['created_at']
            }
        )

        # 2. Email verification (if not OAuth)
        if user.get('auth_method') == 'password':
            verification_token = generate_verification_token(user['id'])
            await self.orchestrator.trigger_workflow(
                workflow=SignupWorkflows.VERIFY_EMAIL.value,
                recipients=[user['id']],
                data={
                    "verification_link": f"https://app.infrastructure-audit.com/verify/{verification_token}",
                    "expires_in": "24 hours"
                }
            )

        # 3. Schedule onboarding emails
        await self.schedule_onboarding_sequence(user)

    async def schedule_onboarding_sequence(self, user: Dict):
        """Schedule delayed onboarding notifications"""

        onboarding_schedule = [
            (1, SignupWorkflows.ONBOARDING_DAY_1),
            (3, SignupWorkflows.ONBOARDING_DAY_3),
            (7, SignupWorkflows.ONBOARDING_DAY_7),
            (14, SignupWorkflows.ONBOARDING_DAY_14),
        ]

        for days, workflow in onboarding_schedule:
            send_at = datetime.now() + timedelta(days=days)

            # Each can be cancelled if user completes onboarding
            cancellation_key = f"onboarding_{user['id']}_{days}"

            await self.orchestrator.trigger_workflow(
                workflow=workflow.value,
                recipients=[user['id']],
                data={
                    "days_since_signup": days,
                    "profile_completion": await self.calculate_profile_completion(user['id']),
                    "next_steps": await self.get_next_onboarding_steps(user['id'])
                },
                cancellation_key=cancellation_key
            )

    async def send_sms_verification(self, user: Dict, phone: str):
        """Send SMS verification code"""
        verification_code = generate_otp()

        await self.orchestrator.trigger_workflow(
            workflow=SignupWorkflows.VERIFY_PHONE.value,
            recipients=[user['id']],
            data={
                "verification_code": verification_code,
                "phone_number": phone,
                "expires_in_minutes": 10
            }
        )

        # Store code in cache
        await cache.set(f"sms_verify:{user['id']}", verification_code, ttl=600)
```

**Tasks:**
- [ ] Set up Knock.app account and API
- [ ] Define notification workflows
- [ ] Create signup sequence workflows
- [ ] Implement onboarding campaigns
- [ ] Set up re-engagement workflows
- [ ] Configure channel fallbacks
- [ ] Add batching and throttling rules
- [ ] Create A/B testing workflows

---

## 5. MCP Integration Layer (Important - Week 2)

### 5.1 MCP Server for Notifications
```python
# mcp/notification_mcp_server.py
import json
from typing import Dict, List, Optional
from mcp.server import MCPServer
from mcp.server.models import Tool, Resource

class NotificationMCPServer(MCPServer):
    """MCP server for AI-powered notification management"""

    def __init__(self, notification_service):
        super().__init__()
        self.notification_service = notification_service
        self.register_tools()

    def register_tools(self):
        """Register notification tools for AI agents"""

        # Send notification tool
        self.add_tool(Tool(
            name="send_notification",
            description="Send a notification to a user via email or SMS",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "User ID"},
                    "channel": {"type": "string", "enum": ["email", "sms", "both"]},
                    "template": {"type": "string", "description": "Template name"},
                    "variables": {"type": "object", "description": "Template variables"}
                },
                "required": ["user_id", "channel", "template"]
            },
            handler=self.send_notification
        ))

        # Check user preferences tool
        self.add_tool(Tool(
            name="check_notification_preferences",
            description="Check if user wants to receive specific notification types",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "notification_type": {"type": "string"}
                },
                "required": ["user_id", "notification_type"]
            },
            handler=self.check_preferences
        ))

        # Generate personalized content tool
        self.add_tool(Tool(
            name="generate_notification_content",
            description="Generate personalized notification content using AI",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "template_type": {"type": "string"},
                    "context": {"type": "object"}
                },
                "required": ["user_id", "template_type"]
            },
            handler=self.generate_content
        ))

        # Schedule notification tool
        self.add_tool(Tool(
            name="schedule_notification",
            description="Schedule a notification for future delivery",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "workflow": {"type": "string"},
                    "send_at": {"type": "string", "format": "date-time"},
                    "data": {"type": "object"}
                },
                "required": ["user_id", "workflow", "send_at"]
            },
            handler=self.schedule_notification
        ))

    async def send_notification(self, params: Dict) -> Dict:
        """Send notification via MCP"""
        user_id = params['user_id']
        channel = params['channel']
        template = params['template']
        variables = params.get('variables', {})

        # Check user preferences
        if not await self.check_consent(user_id, template):
            return {
                "success": False,
                "reason": "User has not consented to this notification type"
            }

        # Send notification
        result = await self.notification_service.send(
            user_id=user_id,
            channel=channel,
            template=template,
            variables=variables
        )

        return result

    async def generate_content(self, params: Dict) -> Dict:
        """Generate AI-powered personalized content"""
        user_id = params['user_id']
        template_type = params['template_type']
        context = params.get('context', {})

        # Get user data
        user = await self.get_user(user_id)

        # Generate personalized content based on user persona
        if template_type == 'onboarding':
            content = await self.generate_onboarding_content(user, context)
        elif template_type == 'infrastructure_tips':
            content = await self.generate_infrastructure_tips(user, context)
        elif template_type == 're_engagement':
            content = await self.generate_reengagement_content(user, context)
        else:
            content = await self.generate_generic_content(user, template_type, context)

        return {
            "subject": content['subject'],
            "body_html": content['body_html'],
            "body_text": content['body_text'],
            "personalization_score": content.get('score', 0.8)
        }

    async def generate_onboarding_content(self, user: Dict, context: Dict) -> Dict:
        """Generate personalized onboarding content"""
        persona = user.get('persona', 'developer')

        # Persona-specific content
        persona_content = {
            'devops_engineer': {
                'subject': 'Set Up Your CI/CD Pipeline Monitoring',
                'focus': 'automation and deployment pipelines'
            },
            'platform_engineer': {
                'subject': 'Configure Your Platform Infrastructure',
                'focus': 'platform services and orchestration'
            },
            'sre': {
                'subject': 'Enable SLO Tracking and Alerting',
                'focus': 'reliability metrics and incident management'
            },
            'security_engineer': {
                'subject': 'Security Compliance Dashboard Setup',
                'focus': 'security scanning and compliance reporting'
            }
        }

        content = persona_content.get(persona, {
            'subject': 'Complete Your Infrastructure Setup',
            'focus': 'infrastructure monitoring'
        })

        body_html = f"""
        <h2>Welcome, {user.get('full_name', 'there')}!</h2>
        <p>Based on your role as a {persona.replace('_', ' ').title()},
        we've customized your onboarding to focus on {content['focus']}.</p>

        <h3>Your Next Steps:</h3>
        <ol>
            <li>Connect your first infrastructure component</li>
            <li>Configure AI-powered analysis with {user.get('preferred_llm', 'Gemini')}</li>
            <li>Set up monitoring for your {context.get('infrastructure_size', 'infrastructure')}</li>
        </ol>

        <a href="https://app.infrastructure-audit.com/onboarding"
           style="display: inline-block; padding: 12px 24px; background: #4F46E5;
                  color: white; text-decoration: none; border-radius: 6px;">
            Continue Setup
        </a>
        """

        return {
            'subject': content['subject'],
            'body_html': body_html,
            'body_text': strip_html(body_html),
            'score': 0.9
        }
```

### 5.2 MCP Client Integration
```python
# mcp/notification_mcp_client.py
from mcp.client import MCPClient
import asyncio

class NotificationMCPClient:
    """Client for interacting with notification MCP server"""

    def __init__(self, server_url: str = "http://localhost:8080"):
        self.client = MCPClient(server_url)
        self.connected = False

    async def connect(self):
        """Connect to MCP server"""
        await self.client.connect()
        self.connected = True

    async def send_ai_notification(
        self,
        user_id: int,
        notification_type: str,
        context: Dict
    ) -> Dict:
        """Send AI-generated notification"""

        if not self.connected:
            await self.connect()

        # Generate content using AI
        content = await self.client.call_tool(
            "generate_notification_content",
            {
                "user_id": user_id,
                "template_type": notification_type,
                "context": context
            }
        )

        # Send the notification
        result = await self.client.call_tool(
            "send_notification",
            {
                "user_id": user_id,
                "channel": "email",
                "template": notification_type,
                "variables": content
            }
        )

        return result

    async def check_and_notify(
        self,
        user_id: int,
        event: str,
        data: Dict
    ) -> Dict:
        """Check preferences and send notification if allowed"""

        # Check if user wants this notification
        preferences = await self.client.call_tool(
            "check_notification_preferences",
            {
                "user_id": user_id,
                "notification_type": event
            }
        )

        if preferences.get('allowed'):
            return await self.send_ai_notification(user_id, event, data)

        return {"skipped": True, "reason": "User preferences"}
```

**Tasks:**
- [ ] Set up MCP server for notifications
- [ ] Create notification tools for AI
- [ ] Implement AI content generation
- [ ] Add personalization engine
- [ ] Create preference checking tools
- [ ] Set up scheduling tools
- [ ] Implement analytics tools
- [ ] Add A/B testing capabilities

---

## 6. Notification Service Layer (Week 2)

### 6.1 Unified Notification Service
```python
# services/notification_service.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

class NotificationService:
    """Unified notification service orchestrating all channels"""

    def __init__(
        self,
        email_provider,
        sms_provider,
        orchestrator,
        mcp_server,
        db_session
    ):
        self.email = email_provider
        self.sms = sms_provider
        self.orchestrator = orchestrator
        self.mcp = mcp_server
        self.db = db_session

    async def notify_signup(self, user: Dict):
        """Handle all signup notifications"""

        # 1. Send immediate welcome email
        await self.send_welcome_email(user)

        # 2. Send verification email/SMS
        await self.send_verification(user)

        # 3. Schedule onboarding sequence
        await self.schedule_onboarding(user)

        # 4. Notify admin of new signup (if enterprise)
        if user.get('organization_type') == 'enterprise':
            await self.notify_admin_new_enterprise_user(user)

        # 5. Add to newsletter (if consented)
        if user.get('marketing_consent'):
            await self.add_to_newsletter(user)

    async def send_welcome_email(self, user: Dict):
        """Send personalized welcome email"""

        # Generate AI-powered content
        content = await self.mcp.generate_content({
            "user_id": user['id'],
            "template_type": "welcome",
            "context": {
                "persona": user.get('persona'),
                "organization": user.get('organization'),
                "signup_source": user.get('signup_source')
            }
        })

        # Add compliance headers
        message = self.compliance.add_compliance_headers({
            "to_email": user['email'],
            "subject": content['subject'],
            "body_html": content['body_html'],
            "body_text": content['body_text'],
            "categories": ["welcome", "transactional"]
        }, user['id'])

        # Send via primary provider
        result = await self.email.send_email(**message)

        # Log event
        await self.log_notification_event(
            user_id=user['id'],
            channel='email',
            template='welcome',
            status='sent' if result['success'] else 'failed',
            provider='sendgrid',
            message_id=result.get('message_id')
        )

        return result

    async def send_verification(self, user: Dict):
        """Send verification for email/phone"""

        tasks = []

        # Email verification
        if user.get('email') and not user.get('email_verified'):
            tasks.append(self.send_email_verification(user))

        # SMS verification
        if user.get('phone') and not user.get('phone_verified'):
            tasks.append(self.send_sms_verification(user))

        # Send both in parallel
        if tasks:
            await asyncio.gather(*tasks)

    async def send_sms_verification(self, user: Dict):
        """Send SMS verification code"""

        code = generate_otp()

        message = f"Your Infrastructure Audit verification code is {code}. Valid for 10 minutes."

        result = await self.sms.send_sms(
            to_phone=user['phone'],
            message=message
        )

        # Store code in cache
        await cache.set(
            f"sms_verify:{user['id']}",
            code,
            ttl=600  # 10 minutes
        )

        # Log event
        await self.log_notification_event(
            user_id=user['id'],
            channel='sms',
            template='verification',
            status='sent' if result['success'] else 'failed',
            provider='plivo',
            message_id=result.get('message_id')
        )

        return result

    async def schedule_onboarding(self, user: Dict):
        """Schedule onboarding notification sequence"""

        # Define onboarding timeline
        timeline = [
            # Day 1: Getting started guide
            {
                'delay_hours': 24,
                'template': 'onboarding_day_1',
                'channel': 'email'
            },
            # Day 2: SMS reminder to complete profile
            {
                'delay_hours': 48,
                'template': 'profile_reminder',
                'channel': 'sms',
                'condition': lambda u: u.get('profile_completion', 0) < 50
            },
            # Day 3: Infrastructure setup guide
            {
                'delay_hours': 72,
                'template': 'infrastructure_setup',
                'channel': 'email'
            },
            # Day 5: AI configuration reminder
            {
                'delay_hours': 120,
                'template': 'ai_setup_reminder',
                'channel': 'email',
                'condition': lambda u: not u.get('ai_configured')
            },
            # Day 7: First week recap
            {
                'delay_hours': 168,
                'template': 'week_1_recap',
                'channel': 'email'
            },
            # Day 14: Two week check-in
            {
                'delay_hours': 336,
                'template': 'two_week_checkin',
                'channel': 'email'
            },
            # Day 30: Monthly summary
            {
                'delay_hours': 720,
                'template': 'first_month_summary',
                'channel': 'email'
            }
        ]

        for step in timeline:
            scheduled_for = datetime.utcnow() + timedelta(hours=step['delay_hours'])

            # Check condition if exists
            if 'condition' in step:
                # Schedule a job to check condition at runtime
                await self.schedule_conditional_notification(
                    user_id=user['id'],
                    template=step['template'],
                    channel=step['channel'],
                    scheduled_for=scheduled_for,
                    condition=step['condition']
                )
            else:
                # Schedule unconditionally
                await self.queue_notification(
                    user_id=user['id'],
                    template_name=step['template'],
                    channel=step['channel'],
                    scheduled_for=scheduled_for,
                    priority=5
                )
```

### 6.2 Delivery & Tracking
```python
# services/delivery_service.py
class DeliveryService:
    """Handle notification delivery and tracking"""

    def __init__(self, providers: Dict, db_session):
        self.providers = providers
        self.db = db_session

    async def process_queue(self):
        """Process notification queue"""

        while True:
            # Get pending notifications
            notifications = await self.get_pending_notifications(limit=100)

            if notifications:
                # Process in parallel
                tasks = [self.deliver(n) for n in notifications]
                await asyncio.gather(*tasks)

            # Wait before next batch
            await asyncio.sleep(1)

    async def deliver(self, notification: Dict) -> Dict:
        """Deliver single notification"""

        try:
            # Update status to processing
            await self.update_status(notification['id'], 'processing')

            # Select provider
            provider = self.select_provider(notification['channel'])

            # Send notification
            if notification['channel'] == 'email':
                result = await provider.send_email(
                    to_email=notification['recipient'],
                    subject=notification['subject'],
                    body_html=notification['body_html'],
                    body_text=notification['body_text']
                )
            elif notification['channel'] == 'sms':
                result = await provider.send_sms(
                    to_phone=notification['recipient'],
                    message=notification['body_text']
                )

            # Update status based on result
            if result['success']:
                await self.update_status(
                    notification['id'],
                    'sent',
                    provider_message_id=result.get('message_id')
                )
            else:
                await self.handle_failure(notification, result)

            return result

        except Exception as e:
            await self.handle_error(notification, e)
            return {"success": False, "error": str(e)}

    async def handle_failure(self, notification: Dict, result: Dict):
        """Handle delivery failure with retry logic"""

        notification['attempts'] += 1

        if notification['attempts'] < notification['max_attempts']:
            # Exponential backoff
            retry_after = 2 ** notification['attempts'] * 60  # seconds

            await self.update_status(
                notification['id'],
                'pending',
                error_message=result.get('error'),
                scheduled_for=datetime.utcnow() + timedelta(seconds=retry_after)
            )
        else:
            # Max retries reached
            await self.update_status(
                notification['id'],
                'failed',
                error_message=f"Max retries reached: {result.get('error')}"
            )

            # Alert admin for critical notifications
            if notification.get('priority', 5) <= 3:
                await self.alert_admin(f"Critical notification failed: {notification['id']}")

    async def track_engagement(self, event: Dict):
        """Track email/SMS engagement events"""

        event_type = event['event']
        message_id = event['message_id']

        # Find notification by provider message ID
        notification = await self.find_by_message_id(message_id)

        if notification:
            # Update notification status
            if event_type == 'delivered':
                await self.update_status(notification['id'], 'delivered')
            elif event_type == 'opened':
                await self.mark_opened(notification['id'])
            elif event_type == 'clicked':
                await self.mark_clicked(notification['id'], event.get('url'))
            elif event_type == 'bounced':
                await self.mark_bounced(notification['id'], event.get('reason'))
            elif event_type == 'complained':
                await self.handle_complaint(notification['id'], notification['user_id'])

            # Log event
            await self.log_event(
                notification_id=notification['id'],
                user_id=notification['user_id'],
                event_type=event_type,
                metadata=event
            )
```

**Tasks:**
- [ ] Create unified notification service
- [ ] Implement queue processing
- [ ] Add delivery tracking
- [ ] Create retry logic with backoff
- [ ] Implement engagement tracking
- [ ] Add webhook handlers
- [ ] Create delivery reports
- [ ] Set up monitoring alerts

---

## 7. FastAPI Integration Layer (Week 3)

### 7.1 Notification API Endpoints
```python
# api/notification_routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Optional

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

@router.post("/send")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Send notification to user"""

    # Validate permissions
    if request.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Queue notification
    background_tasks.add_task(
        notification_service.send,
        user_id=request.user_id,
        template=request.template,
        channel=request.channel,
        variables=request.variables
    )

    return {"status": "queued", "message": "Notification queued for delivery"}

@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notification preferences"""

    prefs = await db.query(UserNotificationPreferences).filter(
        UserNotificationPreferences.user_id == current_user.id
    ).first()

    if not prefs:
        # Return defaults
        prefs = UserNotificationPreferences(user_id=current_user.id)

    return prefs

@router.put("/preferences")
async def update_preferences(
    preferences: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""

    prefs = await db.query(UserNotificationPreferences).filter(
        UserNotificationPreferences.user_id == current_user.id
    ).first()

    if not prefs:
        prefs = UserNotificationPreferences(
            user_id=current_user.id,
            **preferences.dict()
        )
        db.add(prefs)
    else:
        for key, value in preferences.dict(exclude_unset=True).items():
            setattr(prefs, key, value)

    await db.commit()

    return {"status": "updated", "preferences": prefs}

@router.post("/webhooks/sendgrid")
async def sendgrid_webhook(
    events: List[Dict],
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """Handle SendGrid webhook events"""

    for event in events:
        background_tasks.add_task(
            delivery_service.track_engagement,
            event
        )

    return {"received": len(events)}

@router.post("/webhooks/plivo")
async def plivo_webhook(
    event: Dict,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """Handle Plivo webhook events"""

    background_tasks.add_task(
        delivery_service.track_engagement,
        event
    )

    return {"status": "received"}

@router.get("/unsubscribe/{channel}/{token}")
async def unsubscribe(
    channel: str,
    token: str,
    db: Session = Depends(get_db)
):
    """One-click unsubscribe"""

    # Find user by token
    prefs = await db.query(UserNotificationPreferences).filter(
        UserNotificationPreferences.email_unsubscribe_token == token
        if channel == 'email'
        else UserNotificationPreferences.sms_unsubscribe_token == token
    ).first()

    if not prefs:
        raise HTTPException(status_code=404, detail="Invalid unsubscribe link")

    # Update preferences
    if channel == 'email':
        prefs.email_enabled = False
        prefs.marketing_notifications = False
    elif channel == 'sms':
        prefs.sms_enabled = False

    await db.commit()

    return {"message": f"Successfully unsubscribed from {channel} notifications"}

@router.get("/history")
async def notification_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notification history"""

    notifications = await db.query(NotificationQueue).filter(
        NotificationQueue.user_id == current_user.id
    ).order_by(
        NotificationQueue.created_at.desc()
    ).limit(limit).offset(offset).all()

    return {
        "notifications": notifications,
        "total": await db.query(NotificationQueue).filter(
            NotificationQueue.user_id == current_user.id
        ).count()
    }
```

**Tasks:**
- [ ] Create notification API endpoints
- [ ] Implement preference management
- [ ] Add webhook handlers
- [ ] Create unsubscribe endpoints
- [ ] Implement notification history
- [ ] Add admin endpoints
- [ ] Create analytics endpoints
- [ ] Set up rate limiting

---

## 8. Monitoring & Analytics Layer (Week 3)

### 8.1 Notification Analytics
```python
# analytics/notification_analytics.py
from datetime import datetime, timedelta
from typing import Dict, List

class NotificationAnalytics:
    """Track and analyze notification performance"""

    def __init__(self, db_session):
        self.db = db_session

    async def get_delivery_stats(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get delivery statistics"""

        stats = await self.db.execute("""
            SELECT
                channel,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
                SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) as clicked,
                SUM(CASE WHEN bounced_at IS NOT NULL THEN 1 ELSE 0 END) as bounced,
                SUM(CASE WHEN complained_at IS NOT NULL THEN 1 ELSE 0 END) as complained
            FROM notification_queue
            WHERE created_at BETWEEN :start_date AND :end_date
            GROUP BY channel
        """, {
            "start_date": start_date,
            "end_date": end_date
        })

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "channels": stats.fetchall(),
            "metrics": await self.calculate_metrics(stats)
        }

    async def calculate_metrics(self, stats: List) -> Dict:
        """Calculate key metrics"""

        total_sent = sum(s['sent'] for s in stats)
        total_delivered = sum(s['delivered'] for s in stats)
        total_opened = sum(s['opened'] for s in stats)
        total_clicked = sum(s['clicked'] for s in stats)
        total_bounced = sum(s['bounced'] for s in stats)
        total_complained = sum(s['complained'] for s in stats)

        return {
            "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0,
            "open_rate": (total_opened / total_delivered * 100) if total_delivered > 0 else 0,
            "click_rate": (total_clicked / total_opened * 100) if total_opened > 0 else 0,
            "bounce_rate": (total_bounced / total_sent * 100) if total_sent > 0 else 0,
            "complaint_rate": (total_complained / total_delivered * 100) if total_delivered > 0 else 0
        }

    async def get_engagement_funnel(self, template: str, days: int = 30) -> Dict:
        """Get engagement funnel for specific template"""

        start_date = datetime.utcnow() - timedelta(days=days)

        funnel = await self.db.execute("""
            SELECT
                COUNT(*) as sent,
                SUM(CASE WHEN delivered_at IS NOT NULL THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
                SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) as clicked
            FROM notification_queue
            WHERE template_id = (
                SELECT id FROM notification_templates WHERE name = :template
            )
            AND created_at >= :start_date
        """, {
            "template": template,
            "start_date": start_date
        })

        result = funnel.fetchone()

        return {
            "template": template,
            "period_days": days,
            "funnel": {
                "sent": result['sent'],
                "delivered": result['delivered'],
                "opened": result['opened'],
                "clicked": result['clicked']
            },
            "conversion": {
                "delivery": (result['delivered'] / result['sent'] * 100) if result['sent'] > 0 else 0,
                "open": (result['opened'] / result['delivered'] * 100) if result['delivered'] > 0 else 0,
                "click": (result['clicked'] / result['opened'] * 100) if result['opened'] > 0 else 0
            }
        }

    async def get_provider_performance(self) -> Dict:
        """Compare provider performance"""

        providers = await self.db.execute("""
            SELECT
                provider,
                channel,
                COUNT(*) as total,
                AVG(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as success_rate,
                AVG(JULIANDAY(sent_at) - JULIANDAY(created_at)) * 86400 as avg_send_time,
                SUM(CASE WHEN bounced_at IS NOT NULL THEN 1 ELSE 0 END) as bounces,
                COUNT(DISTINCT user_id) as unique_users
            FROM notification_queue
            WHERE provider IS NOT NULL
            GROUP BY provider, channel
        """)

        return {
            "providers": providers.fetchall(),
            "recommendations": await self.generate_provider_recommendations(providers)
        }
```

### 8.2 Monitoring & Alerts
```python
# monitoring/notification_monitor.py
class NotificationMonitor:
    """Monitor notification system health"""

    def __init__(self, alerting_service, analytics_service):
        self.alerting = alerting_service
        self.analytics = analytics_service

    async def check_delivery_rate(self):
        """Monitor delivery rate"""

        stats = await self.analytics.get_delivery_stats(
            start_date=datetime.utcnow() - timedelta(hours=1),
            end_date=datetime.utcnow()
        )

        delivery_rate = stats['metrics']['delivery_rate']

        if delivery_rate < 95:
            await self.alerting.send_alert(
                level='warning',
                message=f"Low delivery rate: {delivery_rate}%",
                details=stats
            )

        if delivery_rate < 90:
            await self.alerting.send_alert(
                level='critical',
                message=f"Critical delivery rate: {delivery_rate}%",
                details=stats
            )

    async def check_complaint_rate(self):
        """Monitor spam complaint rate"""

        stats = await self.analytics.get_delivery_stats(
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow()
        )

        complaint_rate = stats['metrics']['complaint_rate']

        # Industry standard is < 0.1%
        if complaint_rate > 0.1:
            await self.alerting.send_alert(
                level='critical',
                message=f"High complaint rate: {complaint_rate}%",
                action_required="Review sending practices immediately"
            )

    async def check_queue_health(self):
        """Monitor notification queue"""

        # Check for stuck notifications
        stuck = await self.db.execute("""
            SELECT COUNT(*) as count
            FROM notification_queue
            WHERE status = 'processing'
            AND updated_at < datetime('now', '-5 minutes')
        """)

        if stuck['count'] > 0:
            await self.alerting.send_alert(
                level='warning',
                message=f"{stuck['count']} notifications stuck in processing"
            )

        # Check queue size
        queue_size = await self.db.execute("""
            SELECT COUNT(*) as count
            FROM notification_queue
            WHERE status = 'pending'
        """)

        if queue_size['count'] > 1000:
            await self.alerting.send_alert(
                level='warning',
                message=f"Large queue size: {queue_size['count']} pending notifications"
            )
```

**Tasks:**
- [ ] Create analytics dashboard
- [ ] Implement delivery tracking
- [ ] Add engagement metrics
- [ ] Create funnel analysis
- [ ] Monitor provider performance
- [ ] Set up alerting thresholds
- [ ] Create compliance reports
- [ ] Add cost tracking

---

## Implementation Roadmap

### Week 1: Foundation
**Days 1-2: Infrastructure**
- Set up database schema
- Configure provider accounts (SendGrid, Plivo)
- Implement basic provider integrations
- Set up authentication (SPF, DKIM, DMARC)

**Days 3-4: Core Services**
- Build notification service
- Implement delivery service
- Create queue processor
- Add retry logic

**Days 5-7: Compliance & Security**
- Implement GDPR compliance
- Add CAN-SPAM headers
- Create unsubscribe system
- Set up rate limiting

### Week 2: Advanced Features
**Days 8-10: Orchestration**
- Set up Knock.app
- Define workflows
- Create onboarding sequences
- Implement scheduling

**Days 11-12: MCP Integration**
- Create MCP server
- Build notification tools
- Add AI personalization
- Implement content generation

**Days 13-14: API & Integration**
- Build FastAPI endpoints
- Create webhook handlers
- Add preference management
- Implement admin tools

### Week 3: Polish & Launch
**Days 15-17: Monitoring**
- Set up analytics
- Create dashboards
- Implement alerting
- Add performance monitoring

**Days 18-21: Testing & Launch**
- End-to-end testing
- Load testing
- Documentation
- Production deployment

---

## Provider Recommendations

### Primary Providers
1. **Email: SendGrid** - Best balance of features, reliability, and developer experience
2. **SMS: Plivo** - Most cost-effective with good global coverage
3. **Orchestration: Knock** - Enterprise-grade workflow management

### Backup Providers
1. **Email: AWS SES** - For high-volume cost optimization
2. **SMS: Twilio** - Premium reliability when needed
3. **Orchestration: Courier** - Alternative with good Segment integration

### MCP Integration
- Use **Knock MCP Server** for multi-channel orchestration
- Implement custom MCP server for AI personalization
- Connect to **Twilio MCP** for SMS capabilities

---

## Cost Optimization

### Email Costs (Monthly)
- **SendGrid**: $89.95 for 100k emails
- **AWS SES**: $10 for 100k emails (requires more setup)
- **Resend**: $80 for 100k emails

### SMS Costs (Per Message)
- **Plivo**: $0.0055 (US)
- **Twilio**: $0.0075 (US)
- **Vonage**: $0.0065 (US)

### Recommendations
- Start with SendGrid + Plivo
- Switch to AWS SES at >500k emails/month
- Use Knock for orchestration ($150/month)
- Budget: ~$300/month for 100k users

---

## Security Checklist

- [ ] All API keys encrypted at rest
- [ ] Webhook signatures validated
- [ ] Rate limiting on all endpoints
- [ ] PII data encrypted in database
- [ ] Audit logs for all operations
- [ ] HTTPS only for webhooks
- [ ] IP whitelisting for admin APIs
- [ ] Regular security audits

---

## Compliance Checklist

- [ ] GDPR consent management
- [ ] CAN-SPAM compliance headers
- [ ] One-click unsubscribe
- [ ] Physical address in emails
- [ ] Complaint rate < 0.1%
- [ ] Bounce rate < 2%
- [ ] Data retention policies
- [ ] Right to erasure implementation

---

## Success Metrics

1. **Delivery Rate**: >98%
2. **Open Rate**: >25% (signup emails)
3. **Click Rate**: >10% (onboarding emails)
4. **Complaint Rate**: <0.1%
5. **Bounce Rate**: <2%
6. **Response Time**: <500ms API
7. **Queue Processing**: <30s delay
8. **Cost per User**: <$0.03/month

---

## Conclusion

This comprehensive notification system provides a robust, scalable solution for user engagement throughout the signup and onboarding journey. By combining best-in-class providers (SendGrid, Plivo) with modern orchestration (Knock) and AI capabilities (MCP), we ensure maximum deliverability, engagement, and compliance while maintaining cost efficiency.

The system is designed to scale from startup to enterprise, with built-in failover, monitoring, and compliance features that meet 2025 standards including mandatory DMARC authentication and GDPR requirements.