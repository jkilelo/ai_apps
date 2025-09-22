# Authentication & Onboarding System Audit Checklist
## Comprehensive Infrastructure Audit Platform Authentication Implementation
### *Integrating Modern 2025 Authentication Standards with AI-First Infrastructure Management*

---

## Executive Summary

This audit document provides a comprehensive bottom-up implementation strategy for integrating modern authentication and onboarding into our infrastructure audit system. Drawing from 2025 best practices, we implement a three-tier authentication approach: traditional signup, OAuth2 (Google/GitHub), and passwordless (passkeys/WebAuthn), all integrated with our existing Pydantic v2 models, FastAPI backend, and React v19 frontend.

**Core Innovation**: Multi-modal authentication with progressive profiling, tenant-aware RBAC, and AI-assisted onboarding that adapts to user personas (DevOps Engineer, Platform Lead, SRE, etc.) defined in our existing user hierarchy.

---

## 1. Database Schema Extension Layer (Foundation - Critical)

### 1.1 Authentication Tables
```sql
-- REQUIREMENT: Extend existing schema.sql with authentication tables
-- Authentication Methods Table
CREATE TABLE auth_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT CHECK(type IN ('password', 'oauth2', 'passkey', 'magic_link')),
    enabled BOOLEAN DEFAULT TRUE,
    config JSON,  -- Provider-specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Authentication Table (extends existing users)
CREATE TABLE user_auth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    auth_method_id INTEGER NOT NULL,

    -- Password auth fields
    password_hash TEXT,
    password_salt TEXT,
    password_algorithm TEXT DEFAULT 'bcrypt',

    -- OAuth2 fields
    oauth_provider TEXT,  -- 'google', 'github'
    oauth_id TEXT,
    oauth_email TEXT,
    oauth_refresh_token TEXT,  -- Encrypted
    oauth_access_token TEXT,   -- Encrypted
    oauth_token_expiry TIMESTAMP,

    -- Passkey/WebAuthn fields
    credential_id TEXT UNIQUE,
    public_key TEXT,
    credential_public_key BLOB,
    counter INTEGER DEFAULT 0,
    credential_device_type TEXT,
    credential_backed_up BOOLEAN,
    transports JSON,  -- ['usb', 'nfc', 'ble', 'internal']

    -- Magic link fields
    magic_link_token TEXT,
    magic_link_expiry TIMESTAMP,

    -- Security fields
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret TEXT,  -- Encrypted TOTP secret
    backup_codes JSON,  -- Encrypted array

    -- Audit fields
    last_login TIMESTAMP,
    last_password_change TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (auth_method_id) REFERENCES auth_methods(id),
    UNIQUE(user_id, auth_method_id, oauth_provider)
);

-- Sessions Table
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    auth_method_id INTEGER NOT NULL,

    -- Session data
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    id_token TEXT,  -- For OIDC

    -- Device tracking
    user_agent TEXT,
    ip_address TEXT,
    device_fingerprint TEXT,

    -- Session management
    expires_at TIMESTAMP NOT NULL,
    refresh_expires_at TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    revoke_reason TEXT,

    -- Multi-tenancy
    tenant_id INTEGER,
    organization_id INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (auth_method_id) REFERENCES auth_methods(id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Progressive Profiling Table
CREATE TABLE user_onboarding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,

    -- Onboarding stages
    stage TEXT DEFAULT 'registration',  -- registration, profile, preferences, workspace, complete
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 5,

    -- Profile completion
    profile_completion_percent INTEGER DEFAULT 0,
    required_fields_complete BOOLEAN DEFAULT FALSE,
    optional_fields_complete BOOLEAN DEFAULT FALSE,

    -- Onboarding metadata
    onboarding_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    onboarding_completed_at TIMESTAMP,
    skipped_steps JSON,  -- Array of skipped step IDs

    -- User preferences collected
    preferred_language TEXT DEFAULT 'en',
    preferred_theme TEXT DEFAULT 'system',
    notification_preferences JSON,

    -- Infrastructure preferences (from our audit system)
    preferred_profile_type TEXT,  -- 'poc', 'local', 'opensource', 'enterprise', 'hybrid'
    infrastructure_focus JSON,  -- ['compute', 'storage', 'network', 'security']
    team_size TEXT,  -- 'solo', 'small', 'medium', 'large', 'enterprise'

    -- AI preferences
    ai_assistance_enabled BOOLEAN DEFAULT TRUE,
    preferred_llm_provider TEXT DEFAULT 'gemini',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Audit Log for Authentication Events
CREATE TABLE auth_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_type TEXT NOT NULL,  -- login, logout, password_change, mfa_enable, etc.
    auth_method TEXT,
    success BOOLEAN,
    failure_reason TEXT,
    ip_address TEXT,
    user_agent TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_user_auth_user_id ON user_auth(user_id);
CREATE INDEX idx_user_auth_oauth ON user_auth(oauth_provider, oauth_id);
CREATE INDEX idx_user_auth_credential ON user_auth(credential_id);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(access_token);
CREATE INDEX idx_auth_audit_user_id ON auth_audit_log(user_id, created_at DESC);
```

**Tasks:**
- [ ] Create authentication schema extensions
- [ ] Add foreign key relationships to existing users table
- [ ] Implement JSON field support for flexible data
- [ ] Add indexes for query performance
- [ ] Create triggers for updated_at timestamps
- [ ] Implement soft delete for audit trail
- [ ] Add encryption markers for sensitive fields
- [ ] Create views for common auth queries

---

## 2. Pydantic v2 Authentication Models Layer (Critical)

### 2.1 Core Authentication Models
```python
# auth_models.py - Pydantic v2 models for authentication
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, model_validator, SecretStr
from pydantic import constr, EmailStr, HttpUrl
from enum import Enum
import secrets

class AuthMethod(str, Enum):
    """Supported authentication methods"""
    PASSWORD = "password"
    GOOGLE_OAUTH = "google_oauth"
    GITHUB_OAUTH = "github_oauth"
    PASSKEY = "passkey"
    MAGIC_LINK = "magic_link"

class AuthProvider(str, Enum):
    """OAuth2 providers"""
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"  # Future
    GITLAB = "gitlab"  # Future

class MFAType(str, Enum):
    """Multi-factor authentication types"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"
    PASSKEY = "passkey"

# Request/Response Models
class UserSignup(BaseModel):
    """Traditional signup with password"""
    email: EmailStr = Field(..., description="User email address")
    password: SecretStr = Field(..., min_length=8, description="Password (min 8 chars)")
    confirm_password: SecretStr = Field(..., description="Password confirmation")

    # Optional profile data
    full_name: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)

    # From our user personas
    persona: Optional[str] = Field(None, description="User persona from UserPersona enum")
    infrastructure_focus: Optional[List[str]] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_passwords(self):
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match")
        return self

class OAuth2Callback(BaseModel):
    """OAuth2 callback data"""
    provider: AuthProvider
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State parameter for CSRF protection")
    redirect_uri: HttpUrl = Field(..., description="Callback URL")

class PasskeyRegistration(BaseModel):
    """WebAuthn/Passkey registration"""
    credential_id: str = Field(..., description="Base64 encoded credential ID")
    public_key: str = Field(..., description="Base64 encoded public key")
    attestation_object: str = Field(..., description="Base64 encoded attestation")
    client_data_json: str = Field(..., description="Base64 encoded client data")
    transports: Optional[List[str]] = Field(default_factory=list)

class PasskeyAuthentication(BaseModel):
    """WebAuthn/Passkey authentication"""
    credential_id: str
    authenticator_data: str
    client_data_json: str
    signature: str
    user_handle: Optional[str] = None

class MagicLinkRequest(BaseModel):
    """Magic link authentication request"""
    email: EmailStr
    redirect_url: Optional[HttpUrl] = None

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None  # For OIDC
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="Seconds until expiration")
    scope: Optional[str] = None

    # User info for initial load
    user: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None
    tenant_id: Optional[int] = None

class SessionInfo(BaseModel):
    """Active session information"""
    session_id: str
    user_id: int
    auth_method: AuthMethod
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    device_name: Optional[str] = None

    # Multi-tenancy context
    tenant_id: Optional[int] = None
    organization_id: Optional[int] = None
    active_project_id: Optional[int] = None

# Progressive Profiling Models
class OnboardingStage(str, Enum):
    """Onboarding progression stages"""
    REGISTRATION = "registration"
    EMAIL_VERIFICATION = "email_verification"
    PROFILE_SETUP = "profile_setup"
    PREFERENCES = "preferences"
    INFRASTRUCTURE = "infrastructure"
    TEAM_SETUP = "team_setup"
    AI_CONFIGURATION = "ai_configuration"
    WORKSPACE = "workspace"
    COMPLETE = "complete"

class OnboardingProgress(BaseModel):
    """Track user onboarding progress"""
    user_id: int
    current_stage: OnboardingStage
    current_step: int
    total_steps: int
    completion_percent: int = Field(..., ge=0, le=100)

    # Collected data flags
    has_verified_email: bool = False
    has_profile_picture: bool = False
    has_configured_infrastructure: bool = False
    has_connected_llm: bool = False
    has_joined_organization: bool = False

    # Next actions
    next_action: Optional[str] = None
    can_skip: bool = True
    estimated_time_remaining: Optional[int] = None  # seconds

class ProfileUpdate(BaseModel):
    """Progressive profile collection"""
    # Basic info (collected at different stages)
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None

    # Infrastructure preferences (stage 2)
    preferred_cloud_provider: Optional[str] = None
    infrastructure_size: Optional[Literal["small", "medium", "large", "enterprise"]] = None
    compliance_requirements: Optional[List[str]] = None

    # Team info (stage 3)
    team_size: Optional[int] = None
    team_roles: Optional[List[str]] = None

    # AI preferences (stage 4)
    ai_enabled: Optional[bool] = None
    preferred_llm: Optional[str] = None
    ai_usage_consent: Optional[bool] = None
```

**Tasks:**
- [ ] Create comprehensive auth Pydantic models
- [ ] Implement password validation rules
- [ ] Add OAuth2 state management models
- [ ] Create passkey/WebAuthn models
- [ ] Implement session management models
- [ ] Add progressive profiling models
- [ ] Create audit trail models
- [ ] Implement MFA configuration models

---

## 3. FastAPI Authentication Backend Layer (Critical)

### 3.1 Core Authentication Service
```python
# auth_service.py - Core authentication service layer
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from datetime import datetime, timedelta
import secrets
import redis
from typing import Optional

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:email read:user'}
)

# Token schemes
oauth2_password = OAuth2PasswordBearer(tokenUrl="token")
http_bearer = HTTPBearer()

class AuthService:
    def __init__(self, db_session, redis_client: redis.Redis):
        self.db = db_session
        self.redis = redis_client
        self.pwd_context = pwd_context

    # Password Authentication
    async def signup_with_password(self, signup: UserSignup) -> User:
        """Create new user with password authentication"""
        # Check existing user
        existing = await self.get_user_by_email(signup.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user with our existing User model
        user = User(
            email=signup.email,
            full_name=signup.full_name,
            persona=signup.persona,
            # Map to our existing user model fields
        )

        # Create auth record
        password_hash = self.pwd_context.hash(signup.password.get_secret_value())
        user_auth = UserAuth(
            user_id=user.id,
            auth_method_id=AuthMethod.PASSWORD,
            password_hash=password_hash,
            password_algorithm="bcrypt"
        )

        # Initialize onboarding
        onboarding = UserOnboarding(
            user_id=user.id,
            stage=OnboardingStage.EMAIL_VERIFICATION,
            infrastructure_focus=signup.infrastructure_focus
        )

        await self.db.commit()

        # Send verification email
        await self.send_verification_email(user)

        return user

    # OAuth2 Authentication
    async def oauth_login(self, provider: AuthProvider):
        """Initiate OAuth2 flow"""
        redirect_uri = f"{BASE_URL}/auth/callback/{provider}"

        if provider == AuthProvider.GOOGLE:
            return await oauth.google.authorize_redirect(redirect_uri)
        elif provider == AuthProvider.GITHUB:
            return await oauth.github.authorize_redirect(redirect_uri)

    async def oauth_callback(self, provider: AuthProvider, code: str) -> TokenResponse:
        """Handle OAuth2 callback"""
        if provider == AuthProvider.GOOGLE:
            token = await oauth.google.authorize_access_token(code=code)
            user_info = token.get('userinfo')
        elif provider == AuthProvider.GITHUB:
            token = await oauth.github.authorize_access_token(code=code)
            # Fetch user info from GitHub API
            user_info = await self.fetch_github_user(token['access_token'])

        # Create or update user
        user = await self.get_or_create_oauth_user(
            provider=provider,
            oauth_id=user_info['id'],
            email=user_info['email'],
            name=user_info.get('name')
        )

        # Create session
        return await self.create_session(user, auth_method=f"{provider}_oauth")

    # Passkey/WebAuthn
    async def register_passkey(self, user_id: int, registration: PasskeyRegistration):
        """Register a new passkey for user"""
        # Verify attestation (use py_webauthn library)
        verification = verify_registration_response(
            credential=registration.dict(),
            expected_challenge=self.get_challenge(user_id),
            expected_origin=FRONTEND_URL,
            expected_rp_id=RP_ID
        )

        if verification.verified:
            # Store credential
            user_auth = UserAuth(
                user_id=user_id,
                auth_method_id=AuthMethod.PASSKEY,
                credential_id=registration.credential_id,
                public_key=registration.public_key,
                transports=registration.transports
            )
            await self.db.commit()
            return {"status": "registered"}

        raise HTTPException(status_code=400, detail="Invalid registration")

    # Session Management
    async def create_session(
        self,
        user: User,
        auth_method: str,
        tenant_id: Optional[int] = None
    ) -> TokenResponse:
        """Create JWT tokens and session"""
        # Token payload
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "persona": user.persona,
            "auth_method": auth_method,
            "tenant_id": tenant_id,
            "permissions": await self.get_user_permissions(user.id, tenant_id),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Refresh token
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Store session in Redis
        session_id = secrets.token_urlsafe(32)
        await self.redis.setex(
            f"session:{session_id}",
            ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            json.dumps({
                "user_id": user.id,
                "auth_method": auth_method,
                "tenant_id": tenant_id
            })
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user.dict(),
            permissions=payload["permissions"],
            tenant_id=tenant_id
        )

    # Tenant-Aware RBAC
    async def get_user_permissions(
        self,
        user_id: int,
        tenant_id: Optional[int] = None
    ) -> List[str]:
        """Get user permissions for specific tenant"""
        if tenant_id:
            # Get tenant-specific role
            tenant_member = await self.db.query(TenantMember).filter(
                TenantMember.user_id == user_id,
                TenantMember.tenant_id == tenant_id
            ).first()

            if tenant_member:
                return self.get_role_permissions(tenant_member.role)

        # Get global permissions
        user = await self.get_user(user_id)
        return self.get_persona_permissions(user.persona)

    def get_role_permissions(self, role: str) -> List[str]:
        """Map role to permissions"""
        role_permissions = {
            "owner": ["*"],  # All permissions
            "admin": ["read", "write", "delete", "invite", "configure"],
            "developer": ["read", "write", "deploy"],
            "viewer": ["read"],
        }
        return role_permissions.get(role, [])
```

**Tasks:**
- [ ] Implement password hashing with bcrypt
- [ ] Create JWT token generation and validation
- [ ] Set up OAuth2 with Google provider
- [ ] Set up OAuth2 with GitHub provider
- [ ] Implement passkey registration flow
- [ ] Create session management with Redis
- [ ] Add tenant-aware permission system
- [ ] Implement refresh token rotation

### 3.2 FastAPI Routes
```python
# auth_routes.py - Authentication endpoints
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup(
    signup_data: UserSignup,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Traditional email/password signup"""
    user = await auth_service.signup_with_password(signup_data)
    return await auth_service.create_session(user, AuthMethod.PASSWORD)

@router.get("/oauth/{provider}/login")
async def oauth_login(
    provider: AuthProvider,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Initiate OAuth2 flow"""
    return await auth_service.oauth_login(provider)

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: AuthProvider,
    code: str,
    state: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle OAuth2 callback"""
    return await auth_service.oauth_callback(provider, code)

@router.post("/passkey/register/begin")
async def passkey_register_begin(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Begin passkey registration"""
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name="Infrastructure Audit Platform",
        user_id=str(current_user.id),
        user_name=current_user.email,
        user_display_name=current_user.full_name or current_user.email
    )

    # Store challenge in session
    await auth_service.store_challenge(current_user.id, options.challenge)

    return options

@router.post("/passkey/register/complete")
async def passkey_register_complete(
    registration: PasskeyRegistration,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Complete passkey registration"""
    return await auth_service.register_passkey(current_user.id, registration)

@router.post("/magic-link/send")
async def send_magic_link(
    request: MagicLinkRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Send magic link for passwordless login"""
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=15)

    # Store token
    await auth_service.store_magic_token(request.email, token, expiry)

    # Send email
    await send_email(
        to=request.email,
        subject="Your login link",
        body=f"Click here to login: {FRONTEND_URL}/auth/magic/{token}"
    )

    return {"message": "Magic link sent"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    return await auth_service.refresh_access_token(refresh_token)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout and revoke tokens"""
    await auth_service.revoke_session(current_user.id)
    return {"message": "Logged out successfully"}

# Progressive Profiling Endpoints
@router.get("/onboarding/progress", response_model=OnboardingProgress)
async def get_onboarding_progress(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current onboarding progress"""
    return await auth_service.get_onboarding_progress(current_user.id)

@router.post("/onboarding/update")
async def update_onboarding(
    stage: OnboardingStage,
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update onboarding progress with collected data"""
    return await auth_service.update_onboarding(current_user.id, stage, data)
```

**Tasks:**
- [ ] Create signup endpoint with validation
- [ ] Implement OAuth2 login/callback endpoints
- [ ] Add passkey registration endpoints
- [ ] Create magic link endpoints
- [ ] Implement token refresh endpoint
- [ ] Add logout with session revocation
- [ ] Create onboarding progress endpoints
- [ ] Add MFA setup endpoints

---

## 4. Security & Compliance Layer (Critical)

### 4.1 Security Middleware
```python
# security_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import hmac

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""

    async def dispatch(self, request: Request, call_next):
        # CSRF Protection
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_token = request.headers.get("X-CSRF-Token")
            session_token = request.session.get("csrf_token")

            if not csrf_token or csrf_token != session_token:
                raise HTTPException(status_code=403, detail="CSRF validation failed")

        # Rate Limiting
        client_ip = request.client.host
        endpoint = f"{request.method}:{request.url.path}"

        if await self.is_rate_limited(client_ip, endpoint):
            raise HTTPException(status_code=429, detail="Too many requests")

        # Security Headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

    async def is_rate_limited(self, client_ip: str, endpoint: str) -> bool:
        """Check rate limits using Redis"""
        key = f"rate_limit:{client_ip}:{endpoint}"

        # Different limits for different endpoints
        limits = {
            "POST:/api/v1/auth/signup": (5, 3600),  # 5 per hour
            "POST:/api/v1/auth/login": (10, 300),   # 10 per 5 minutes
            "POST:/api/v1/auth/magic-link/send": (3, 3600),  # 3 per hour
        }

        limit, window = limits.get(endpoint, (100, 60))  # Default: 100 per minute

        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)

        return current > limit

class ComplianceMiddleware(BaseHTTPMiddleware):
    """GDPR, SOC2, and compliance middleware"""

    async def dispatch(self, request: Request, call_next):
        # Audit logging
        audit_entry = {
            "timestamp": datetime.utcnow(),
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host,
            "user_agent": request.headers.get("User-Agent"),
            "user_id": None  # Will be populated if authenticated
        }

        # Check for authenticated user
        if hasattr(request.state, "user"):
            audit_entry["user_id"] = request.state.user.id

        response = await call_next(request)

        # Log sensitive operations
        sensitive_operations = [
            "/api/v1/auth/",
            "/api/v1/users/",
            "/api/v1/infrastructure/components"
        ]

        if any(request.url.path.startswith(op) for op in sensitive_operations):
            audit_entry["status_code"] = response.status_code
            await self.log_audit_event(audit_entry)

        # GDPR: Add privacy headers
        if "/api/v1/users/" in request.url.path:
            response.headers["X-Privacy-Protected"] = "true"

        return response
```

**Tasks:**
- [ ] Implement CSRF protection
- [ ] Add rate limiting with Redis
- [ ] Set security headers (HSTS, CSP, etc.)
- [ ] Create audit logging middleware
- [ ] Implement GDPR compliance checks
- [ ] Add SOC2 audit trail
- [ ] Create IP-based blocking
- [ ] Implement request signing validation

### 4.2 FIDO2/WebAuthn Implementation
```python
# webauthn_service.py - Passwordless authentication
from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response

class WebAuthnService:
    """FIDO2/WebAuthn passwordless authentication"""

    def __init__(self, rp_id: str, rp_name: str):
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.origin = f"https://{rp_id}"

    async def generate_registration_options(self, user: User) -> dict:
        """Generate registration challenge"""
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=str(user.id).encode(),
            user_name=user.email,
            user_display_name=user.full_name or user.email,
            attestation="direct",
            authenticator_selection={
                "authenticator_attachment": "platform",
                "require_resident_key": True,
                "user_verification": "required"
            },
            supported_pub_key_algs=[-7, -257],  # ES256, RS256
            timeout=60000
        )

        # Store challenge
        await self.store_challenge(user.id, options["challenge"])

        return options

    async def verify_registration(
        self,
        user_id: int,
        credential: dict
    ) -> bool:
        """Verify registration response"""
        expected_challenge = await self.get_challenge(user_id)

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_origin=self.origin,
            expected_rp_id=self.rp_id,
            require_user_verification=True
        )

        if verification.verified:
            # Store credential
            await self.store_credential(
                user_id=user_id,
                credential_id=verification.credential_id,
                public_key=verification.credential_public_key,
                sign_count=verification.sign_count,
                credential_device_type=verification.credential_device_type,
                credential_backed_up=verification.credential_backed_up,
                transports=credential.get("transports", [])
            )

        return verification.verified
```

**Tasks:**
- [ ] Implement FIDO2 registration flow
- [ ] Create FIDO2 authentication flow
- [ ] Add resident key support
- [ ] Implement attestation verification
- [ ] Create backup authentication methods
- [ ] Add cross-platform authenticator support
- [ ] Implement user verification requirements
- [ ] Create passkey management UI

---

## 5. Multi-Tenancy Integration Layer

### 5.1 Tenant-Aware Authentication
```python
# tenant_auth.py - Multi-tenant authentication
class TenantAuthService:
    """Handle authentication in multi-tenant context"""

    async def authenticate_with_tenant(
        self,
        credentials: dict,
        tenant_identifier: str  # subdomain, slug, or ID
    ) -> TokenResponse:
        """Authenticate user within tenant context"""
        # Resolve tenant
        tenant = await self.resolve_tenant(tenant_identifier)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Authenticate user
        user = await self.authenticate_user(credentials)

        # Check tenant membership
        membership = await self.get_tenant_membership(user.id, tenant.id)
        if not membership:
            raise HTTPException(
                status_code=403,
                detail="User is not a member of this tenant"
            )

        # Create tenant-scoped session
        return await self.create_session(
            user=user,
            tenant_id=tenant.id,
            role=membership.role,
            permissions=self.get_tenant_permissions(membership.role)
        )

    async def resolve_tenant(self, identifier: str) -> Optional[Tenant]:
        """Resolve tenant from subdomain, slug, or ID"""
        # Try subdomain first (for *.example.com)
        if "." in identifier:
            subdomain = identifier.split(".")[0]
            tenant = await self.db.query(Tenant).filter(
                Tenant.subdomain == subdomain
            ).first()
            if tenant:
                return tenant

        # Try slug
        tenant = await self.db.query(Tenant).filter(
            Tenant.slug == identifier
        ).first()
        if tenant:
            return tenant

        # Try ID
        if identifier.isdigit():
            return await self.db.query(Tenant).get(int(identifier))

        return None

    def get_tenant_permissions(self, role: str) -> List[str]:
        """Get permissions for tenant role"""
        # Tenant-specific permissions
        tenant_permissions = {
            "tenant_owner": [
                "tenant.manage",
                "tenant.billing",
                "tenant.users.manage",
                "infrastructure.*"
            ],
            "tenant_admin": [
                "tenant.users.manage",
                "infrastructure.*"
            ],
            "tenant_developer": [
                "infrastructure.read",
                "infrastructure.write",
                "infrastructure.deploy"
            ],
            "tenant_viewer": [
                "infrastructure.read"
            ]
        }
        return tenant_permissions.get(role, [])

class TenantMiddleware(BaseHTTPMiddleware):
    """Extract and validate tenant context from requests"""

    async def dispatch(self, request: Request, call_next):
        # Extract tenant from subdomain
        host = request.headers.get("host", "")

        if host and "." in host:
            subdomain = host.split(".")[0]

            # Skip for special subdomains
            if subdomain not in ["www", "api", "auth"]:
                tenant = await self.resolve_tenant(subdomain)
                if tenant:
                    request.state.tenant = tenant

        # Extract tenant from header (for API clients)
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header and not hasattr(request.state, "tenant"):
            tenant = await self.resolve_tenant(tenant_header)
            if tenant:
                request.state.tenant = tenant

        # Extract from JWT token
        if hasattr(request.state, "user") and not hasattr(request.state, "tenant"):
            token_tenant_id = request.state.token_payload.get("tenant_id")
            if token_tenant_id:
                tenant = await self.get_tenant(token_tenant_id)
                if tenant:
                    request.state.tenant = tenant

        response = await call_next(request)
        return response
```

**Tasks:**
- [ ] Implement tenant resolution (subdomain/slug/ID)
- [ ] Create tenant-scoped authentication
- [ ] Add tenant membership validation
- [ ] Implement tenant-specific roles
- [ ] Create tenant isolation in sessions
- [ ] Add cross-tenant switching
- [ ] Implement tenant invitation system
- [ ] Create tenant-specific MFA policies

---

## 6. React v19 Frontend Authentication Layer

### 6.1 Authentication Context & Hooks
```typescript
// src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '@/api/auth';
import { User, TokenResponse } from '@/types/auth';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  tenant: Tenant | null;
  permissions: string[];

  // Auth methods
  signup: (data: SignupData) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  loginWithGitHub: () => Promise<void>;
  loginWithPasskey: () => Promise<void>;
  logout: () => Promise<void>;

  // Session management
  refreshSession: () => Promise<void>;
  switchTenant: (tenantId: number) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from stored tokens
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
          setPermissions(userData.permissions || []);
          setTenant(userData.tenant || null);
        } catch (error) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Traditional signup
  const signup = async (data: SignupData) => {
    const response = await authAPI.signup(data);
    handleAuthResponse(response);
  };

  // OAuth2 login
  const loginWithGoogle = async () => {
    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE_URL}/auth/oauth/google/login`;
  };

  const loginWithGitHub = async () => {
    window.location.href = `${API_BASE_URL}/auth/oauth/github/login`;
  };

  // Passkey/WebAuthn login
  const loginWithPasskey = async () => {
    if (!navigator.credentials) {
      throw new Error('WebAuthn not supported');
    }

    // Get authentication options
    const options = await authAPI.getPasskeyAuthOptions();

    // Create credentials
    const credential = await navigator.credentials.get({
      publicKey: options
    });

    // Verify with backend
    const response = await authAPI.verifyPasskey(credential);
    handleAuthResponse(response);
  };

  // Handle auth response
  const handleAuthResponse = (response: TokenResponse) => {
    localStorage.setItem('access_token', response.access_token);
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }

    setUser(response.user);
    setPermissions(response.permissions || []);
    setTenant(response.tenant || null);

    // Set token refresh timer
    const expiresIn = response.expires_in * 1000;
    setTimeout(refreshSession, expiresIn - 60000); // Refresh 1 min before expiry
  };

  // Token refresh
  const refreshSession = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      logout();
      return;
    }

    try {
      const response = await authAPI.refreshToken(refreshToken);
      handleAuthResponse(response);
    } catch (error) {
      logout();
    }
  };

  // Logout
  const logout = async () => {
    await authAPI.logout();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setPermissions([]);
    setTenant(null);
  };

  // Multi-tenancy
  const switchTenant = async (tenantId: number) => {
    const response = await authAPI.switchTenant(tenantId);
    handleAuthResponse(response);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    tenant,
    permissions,
    signup,
    login,
    loginWithGoogle,
    loginWithGitHub,
    loginWithPasskey,
    logout,
    refreshSession,
    switchTenant,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Permission check hook
export const usePermission = (permission: string) => {
  const { permissions } = useAuth();
  return permissions.includes(permission) || permissions.includes('*');
};

// Role check hook
export const useRole = (role: string) => {
  const { user } = useAuth();
  return user?.role === role;
};
```

**Tasks:**
- [ ] Create authentication context provider
- [ ] Implement auth state management
- [ ] Add OAuth2 redirect handling
- [ ] Create passkey authentication flow
- [ ] Implement token refresh logic
- [ ] Add permission checking hooks
- [ ] Create tenant switching logic
- [ ] Implement auth persistence

### 6.2 Authentication Components
```typescript
// src/components/auth/SignupForm.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import { Button, Input, Alert } from '@/components/ui';

const signupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/,
    'Password must contain uppercase, lowercase, number, and special character'
  ),
  confirmPassword: z.string(),
  fullName: z.string().optional(),
  organization: z.string().optional(),
  persona: z.enum(['devops_engineer', 'platform_engineer', 'sre', 'developer']),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

export function SignupForm() {
  const { signup, loginWithGoogle, loginWithGitHub } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: z.infer<typeof signupSchema>) => {
    setIsLoading(true);
    setError(null);

    try {
      await signup(data);
      // Redirect handled by AuthContext
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Create Account</h2>
          <p className="mt-2 text-sm text-gray-600">
            Join the Infrastructure Audit Platform
          </p>
        </div>

        {error && <Alert variant="error">{error}</Alert>}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            {...register('email')}
            type="email"
            label="Email Address"
            error={errors.email?.message}
          />

          <Input
            {...register('password')}
            type="password"
            label="Password"
            error={errors.password?.message}
          />

          <Input
            {...register('confirmPassword')}
            type="password"
            label="Confirm Password"
            error={errors.confirmPassword?.message}
          />

          <Input
            {...register('fullName')}
            label="Full Name (Optional)"
            error={errors.fullName?.message}
          />

          <select
            {...register('persona')}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="">Select your role...</option>
            <option value="developer">Developer</option>
            <option value="devops_engineer">DevOps Engineer</option>
            <option value="platform_engineer">Platform Engineer</option>
            <option value="sre">Site Reliability Engineer</option>
          </select>

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
          >
            Create Account
          </Button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Button
            onClick={loginWithGoogle}
            variant="outline"
            className="flex items-center justify-center"
          >
            <GoogleIcon className="w-5 h-5 mr-2" />
            Google
          </Button>

          <Button
            onClick={loginWithGitHub}
            variant="outline"
            className="flex items-center justify-center"
          >
            <GitHubIcon className="w-5 h-5 mr-2" />
            GitHub
          </Button>
        </div>

        <div className="text-center">
          <Button
            onClick={() => {/* Navigate to passkey setup */}}
            variant="link"
            className="text-sm"
          >
            Set up passwordless login with passkey
          </Button>
        </div>
      </div>
    </div>
  );
}
```

**Tasks:**
- [ ] Create signup form component
- [ ] Implement login form component
- [ ] Add OAuth2 login buttons
- [ ] Create passkey registration UI
- [ ] Implement magic link request form
- [ ] Add password strength indicator
- [ ] Create form validation with Zod
- [ ] Implement loading states

---

## 7. Progressive Onboarding Layer

### 7.1 Onboarding Flow Components
```typescript
// src/components/onboarding/OnboardingWizard.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useOnboarding } from '@/hooks/useOnboarding';
import { motion, AnimatePresence } from 'framer-motion';

const ONBOARDING_STEPS = [
  {
    id: 'email_verification',
    title: 'Verify Your Email',
    component: EmailVerificationStep,
    required: true,
  },
  {
    id: 'profile_setup',
    title: 'Complete Your Profile',
    component: ProfileSetupStep,
    required: true,
  },
  {
    id: 'infrastructure_preferences',
    title: 'Infrastructure Preferences',
    component: InfrastructurePreferencesStep,
    required: false,
  },
  {
    id: 'ai_configuration',
    title: 'AI Assistant Setup',
    component: AIConfigurationStep,
    required: true, // Required for our AI-first platform
  },
  {
    id: 'team_setup',
    title: 'Invite Your Team',
    component: TeamSetupStep,
    required: false,
  },
];

export function OnboardingWizard() {
  const { user } = useAuth();
  const { progress, updateProgress, skipStep } = useOnboarding();
  const [currentStep, setCurrentStep] = useState(0);

  const CurrentStepComponent = ONBOARDING_STEPS[currentStep].component;

  const handleNext = async (data: any) => {
    await updateProgress(ONBOARDING_STEPS[currentStep].id, data);

    if (currentStep < ONBOARDING_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Complete onboarding
      await updateProgress('complete', {});
      // Redirect to dashboard
    }
  };

  const handleSkip = async () => {
    if (!ONBOARDING_STEPS[currentStep].required) {
      await skipStep(ONBOARDING_STEPS[currentStep].id);
      handleNext({});
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto pt-10">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold">Welcome, {user?.full_name || user?.email}</h2>
            <span className="text-sm text-gray-600">
              Step {currentStep + 1} of {ONBOARDING_STEPS.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / ONBOARDING_STEPS.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="bg-white rounded-xl shadow-lg p-8"
          >
            <CurrentStepComponent
              onNext={handleNext}
              onSkip={handleSkip}
              canSkip={!ONBOARDING_STEPS[currentStep].required}
            />
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <Button
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            variant="outline"
          >
            Previous
          </Button>

          <Button
            onClick={handleSkip}
            variant="ghost"
            disabled={ONBOARDING_STEPS[currentStep].required}
          >
            Skip
          </Button>
        </div>
      </div>
    </div>
  );
}

// Infrastructure Preferences Step (specific to our platform)
function InfrastructurePreferencesStep({ onNext }: StepProps) {
  const [preferences, setPreferences] = useState({
    profileType: '',
    cloudProviders: [],
    infrastructureSize: '',
    complianceRequirements: [],
    primaryFocus: [],
  });

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold">Configure Your Infrastructure</h3>

      <div>
        <label className="block text-sm font-medium mb-2">
          Select Infrastructure Profile
        </label>
        <div className="grid grid-cols-2 gap-3">
          {['poc', 'local', 'opensource', 'enterprise', 'hybrid'].map(type => (
            <button
              key={type}
              onClick={() => setPreferences({...preferences, profileType: type})}
              className={`p-3 border rounded-lg ${
                preferences.profileType === type ? 'border-blue-500 bg-blue-50' : ''
              }`}
            >
              <div className="font-medium capitalize">{type}</div>
              <div className="text-xs text-gray-600 mt-1">
                {getProfileDescription(type)}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">
          Primary Cloud Providers
        </label>
        <MultiSelect
          options={['AWS', 'GCP', 'Azure', 'On-Premise', 'Hybrid']}
          selected={preferences.cloudProviders}
          onChange={(selected) => setPreferences({...preferences, cloudProviders: selected})}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">
          Compliance Requirements
        </label>
        <MultiSelect
          options={['GDPR', 'HIPAA', 'SOC2', 'ISO 27001', 'PCI DSS']}
          selected={preferences.complianceRequirements}
          onChange={(selected) => setPreferences({...preferences, complianceRequirements: selected})}
        />
      </div>

      <Button onClick={() => onNext(preferences)} className="w-full">
        Continue
      </Button>
    </div>
  );
}

// AI Configuration Step (required for our AI-first platform)
function AIConfigurationStep({ onNext }: StepProps) {
  const [config, setConfig] = useState({
    enableAI: true,
    preferredProvider: 'gemini',
    apiKey: '',
    usageConsent: false,
  });

  const llmProviders = [
    { id: 'gemini', name: 'Google Gemini 2.5', recommended: true },
    { id: 'openai', name: 'OpenAI GPT-4' },
    { id: 'anthropic', name: 'Anthropic Claude' },
    { id: 'local', name: 'Local LLM (Ollama)' },
  ];

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold">Configure AI Assistant</h3>

      <Alert variant="info">
        Our platform requires at least one AI connection for infrastructure analysis and recommendations.
      </Alert>

      <div>
        <label className="block text-sm font-medium mb-2">
          Select AI Provider
        </label>
        <div className="space-y-2">
          {llmProviders.map(provider => (
            <label
              key={provider.id}
              className={`flex items-center p-3 border rounded-lg cursor-pointer ${
                config.preferredProvider === provider.id ? 'border-blue-500 bg-blue-50' : ''
              }`}
            >
              <input
                type="radio"
                value={provider.id}
                checked={config.preferredProvider === provider.id}
                onChange={(e) => setConfig({...config, preferredProvider: e.target.value})}
                className="mr-3"
              />
              <div>
                <div className="font-medium">
                  {provider.name}
                  {provider.recommended && (
                    <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Recommended
                    </span>
                  )}
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      <Input
        label="API Key"
        type="password"
        value={config.apiKey}
        onChange={(e) => setConfig({...config, apiKey: e.target.value})}
        placeholder="Enter your API key"
        helperText="Your API key is encrypted and never shared"
      />

      <label className="flex items-center">
        <input
          type="checkbox"
          checked={config.usageConsent}
          onChange={(e) => setConfig({...config, usageConsent: e.target.checked})}
          className="mr-2"
        />
        <span className="text-sm">
          I consent to AI-powered analysis of my infrastructure configuration
        </span>
      </label>

      <Button
        onClick={() => onNext(config)}
        disabled={!config.apiKey || !config.usageConsent}
        className="w-full"
      >
        Complete Setup
      </Button>
    </div>
  );
}
```

**Tasks:**
- [ ] Create onboarding wizard component
- [ ] Implement step navigation logic
- [ ] Add progress tracking
- [ ] Create email verification step
- [ ] Build profile completion step
- [ ] Add infrastructure preferences step
- [ ] Implement AI configuration step
- [ ] Create team invitation step

---

## 8. Testing & Monitoring Layer

### 8.1 Authentication Testing
```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    return TestClient(app)

class TestAuthentication:
    """Comprehensive authentication testing"""

    def test_password_signup(self, client):
        """Test traditional signup flow"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "persona": "devops_engineer"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_oauth_google_flow(self, client):
        """Test Google OAuth2 flow"""
        # Test redirect
        response = client.get("/api/v1/auth/oauth/google/login")
        assert response.status_code == 302
        assert "accounts.google.com" in response.headers["location"]

        # Test callback
        with patch("authlib.integrations.starlette_client.OAuth") as mock_oauth:
            mock_oauth.google.authorize_access_token.return_value = {
                "userinfo": {
                    "id": "google123",
                    "email": "user@gmail.com",
                    "name": "Test User"
                }
            }

            response = client.get("/api/v1/auth/oauth/google/callback?code=test")
            assert response.status_code == 200

    def test_passkey_registration(self, client, authenticated_user):
        """Test WebAuthn passkey registration"""
        # Get registration options
        response = client.post(
            "/api/v1/auth/passkey/register/begin",
            headers={"Authorization": f"Bearer {authenticated_user.token}"}
        )
        assert response.status_code == 200
        options = response.json()
        assert "challenge" in options

        # Complete registration
        registration_data = {
            "credential_id": "test_credential",
            "public_key": "test_public_key",
            "attestation_object": "test_attestation",
            "client_data_json": "test_client_data"
        }

        response = client.post(
            "/api/v1/auth/passkey/register/complete",
            json=registration_data,
            headers={"Authorization": f"Bearer {authenticated_user.token}"}
        )
        assert response.status_code == 200

    def test_rate_limiting(self, client):
        """Test rate limiting on auth endpoints"""
        # Attempt multiple signups
        for i in range(6):
            response = client.post("/api/v1/auth/signup", json={
                "email": f"test{i}@example.com",
                "password": "Pass123!"
            })

            if i < 5:
                assert response.status_code != 429
            else:
                assert response.status_code == 429
                assert "Too many requests" in response.json()["detail"]

    def test_tenant_authentication(self, client):
        """Test multi-tenant authentication"""
        # Create tenant
        tenant = create_test_tenant("acme", "acme.example.com")

        # Authenticate with tenant context
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@acme.com", "password": "Pass123!"},
            headers={"X-Tenant-ID": str(tenant.id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == tenant.id

    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/api/v1/auth/status")

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "Strict-Transport-Security" in response.headers
        assert "X-Frame-Options" in response.headers
```

**Tasks:**
- [ ] Create unit tests for auth service
- [ ] Test OAuth2 flows
- [ ] Test passkey registration/authentication
- [ ] Verify rate limiting
- [ ] Test tenant isolation
- [ ] Validate security headers
- [ ] Test token refresh flow
- [ ] Verify audit logging

### 8.2 Monitoring & Observability
```python
# monitoring.py - Authentication monitoring
from prometheus_client import Counter, Histogram, Gauge
import sentry_sdk

# Metrics
auth_attempts = Counter('auth_attempts_total', 'Total authentication attempts', ['method', 'status'])
auth_duration = Histogram('auth_duration_seconds', 'Authentication duration', ['method'])
active_sessions = Gauge('active_sessions', 'Number of active sessions', ['tenant'])
failed_logins = Counter('failed_logins_total', 'Failed login attempts', ['reason'])

class AuthMonitoring:
    """Monitor authentication events"""

    def track_auth_attempt(self, method: str, success: bool, duration: float):
        """Track authentication attempt"""
        auth_attempts.labels(method=method, status='success' if success else 'failure').inc()
        auth_duration.labels(method=method).observe(duration)

        if not success:
            failed_logins.labels(reason=method).inc()

    def track_session(self, action: str, tenant_id: Optional[int] = None):
        """Track session lifecycle"""
        tenant_label = str(tenant_id) if tenant_id else 'global'

        if action == 'create':
            active_sessions.labels(tenant=tenant_label).inc()
        elif action == 'destroy':
            active_sessions.labels(tenant=tenant_label).dec()

    def report_security_event(self, event_type: str, user_id: int, details: dict):
        """Report security events to monitoring"""
        sentry_sdk.capture_message(
            f"Security Event: {event_type}",
            level="warning",
            extra={
                "user_id": user_id,
                "event_type": event_type,
                "details": details
            }
        )

        # Also log to audit trail
        await self.log_audit_event(
            user_id=user_id,
            event_type=event_type,
            metadata=details
        )
```

**Tasks:**
- [ ] Set up Prometheus metrics
- [ ] Configure Sentry error tracking
- [ ] Create authentication dashboards
- [ ] Implement security alerting
- [ ] Add session analytics
- [ ] Monitor failed login patterns
- [ ] Track onboarding completion
- [ ] Create compliance reports

---

## Implementation Roadmap

### Phase 1: Foundation (Days 1-3)
1. Extend database schema with auth tables
2. Create Pydantic v2 authentication models
3. Implement basic password authentication
4. Set up JWT token generation

### Phase 2: OAuth2 Integration (Days 4-6)
1. Configure Google OAuth2
2. Configure GitHub OAuth2
3. Implement OAuth callback handling
4. Create frontend OAuth flows

### Phase 3: Advanced Security (Days 7-9)
1. Implement passkey/WebAuthn support
2. Add MFA capabilities
3. Create security middleware
4. Implement rate limiting

### Phase 4: Multi-Tenancy (Days 10-12)
1. Add tenant-aware authentication
2. Implement RBAC system
3. Create tenant switching
4. Add cross-tenant security

### Phase 5: Frontend Integration (Days 13-15)
1. Build React authentication components
2. Create onboarding wizard
3. Implement progressive profiling
4. Add permission-based UI

### Phase 6: Testing & Launch (Days 16-18)
1. Comprehensive testing
2. Security audit
3. Performance optimization
4. Documentation and deployment

---

## Security Checklist

- [ ] All passwords hashed with bcrypt (cost factor 12+)
- [ ] JWT tokens with short expiration (30 minutes)
- [ ] Refresh tokens with rotation
- [ ] HTTPS-only in production
- [ ] CSRF protection on all state-changing operations
- [ ] Rate limiting on authentication endpoints
- [ ] Account lockout after failed attempts
- [ ] Audit logging for all auth events
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] Session fixation prevention
- [ ] Secure cookie flags (HttpOnly, Secure, SameSite)
- [ ] Regular security dependency updates

---

## Compliance Requirements

- [ ] GDPR: Privacy by design, data minimization
- [ ] GDPR: Explicit consent for data processing
- [ ] GDPR: Right to erasure implementation
- [ ] SOC2: Access control documentation
- [ ] SOC2: Audit trail for all access
- [ ] SOC2: Regular security reviews
- [ ] FIDO2: Phishing-resistant authentication
- [ ] Zero Trust: Continuous verification
- [ ] Zero Trust: Least privilege access
- [ ] HIPAA: Encryption at rest and in transit (if applicable)

---

## Innovation Features

1. **AI-Powered Risk Assessment**: Use LLM to analyze login patterns and detect anomalies
2. **Smart Onboarding**: AI suggests infrastructure configuration based on user persona
3. **Adaptive Authentication**: Adjust security requirements based on risk score
4. **Passwordless First**: Prioritize passkey/WebAuthn over traditional passwords
5. **Infrastructure Profile Matching**: Auto-configure based on detected infrastructure
6. **Team Discovery**: Suggest team members based on organization domain
7. **Compliance Auto-Detection**: Detect required compliance based on infrastructure
8. **Progressive Security**: Gradually increase security as account value increases

---

## Success Metrics

1. **Authentication Performance**: <200ms average auth time
2. **Conversion Rate**: >60% signup completion
3. **Security Score**: 0 security breaches
4. **Onboarding Completion**: >80% complete onboarding
5. **Passkey Adoption**: >30% use passwordless
6. **Session Duration**: >30 minutes average
7. **Failed Login Rate**: <5% of attempts
8. **Support Tickets**: <2% auth-related

---

## Conclusion

This comprehensive authentication and onboarding system integrates seamlessly with our existing infrastructure audit platform, providing enterprise-grade security while maintaining excellent user experience. The three-tier authentication approach (traditional, OAuth2, passwordless) ensures maximum flexibility while the progressive onboarding captures essential information without overwhelming users.

The system is designed with 2025 best practices in mind, including FIDO2 passwordless authentication, zero-trust architecture, and full compliance with GDPR and SOC2 requirements. The tight integration with our existing Pydantic v2 models and AI-first infrastructure ensures a cohesive platform experience.