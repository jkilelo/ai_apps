# /secure - Security Audit Command

## Strategy: Constitutional AI with Security Principles

### Security Constitution
1. **No Exposed Secrets**: API keys, passwords, tokens must be environment variables
2. **Input Validation**: All user inputs must be sanitized and validated
3. **Least Privilege**: Code should request minimum necessary permissions
4. **Defense in Depth**: Multiple layers of security checks
5. **Secure by Default**: Default configurations must be secure
6. **Audit Trail**: Security-relevant actions must be logged
7. **Error Handling**: Never expose sensitive information in errors

## Security Scan Areas

### 1. Secret Detection
- Scan for hardcoded credentials
- Check for exposed API keys
- Identify sensitive data in logs

### 2. Vulnerability Analysis
- SQL injection risks
- XSS vulnerabilities
- Path traversal issues
- Command injection risks
- SSRF vulnerabilities

### 3. Dependency Audit
- Check for known CVEs
- Identify outdated packages
- Review dependency licenses

### 4. Permission Review
- File system permissions
- Network access patterns
- API endpoint security

## Implementation
Generate security fixes that:
- Follow OWASP guidelines
- Include security tests
- Document security measures
- Provide migration path for breaking changes