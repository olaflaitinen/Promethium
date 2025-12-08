# Security Policy

## Supported Versions

The following table indicates which versions of Promethium currently receive security updates:

| Version | Supported          |
|---------|--------------------|
| 1.x.x   | Yes                |
| < 1.0   | No                 |

Security patches are applied to the latest minor version within each supported major version line.

## Security Scope

### In Scope

The following components are within the security scope of this policy:

- **Backend API**: FastAPI application, authentication, authorization
- **Frontend**: Angular web application, client-side security
- **Database**: PostgreSQL schema, queries, stored procedures
- **Worker Processes**: Celery tasks, job execution
- **Container Images**: Official Docker images published by the project
- **Dependencies**: Third-party libraries directly included in the project

### Out of Scope

The following are outside the security scope:

- Third-party hosting environments (user-managed infrastructure)
- Modifications or forks of the official codebase
- Issues in dependencies that have not been integrated into Promethium
- Social engineering attacks targeting project maintainers
- Denial of service attacks against project infrastructure

## Reporting a Vulnerability

We take security vulnerabilities seriously and appreciate responsible disclosure.

### How to Report

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report vulnerabilities through one of the following methods:

1. **Email**: Send a detailed report to the security contact provided in the project's communication channels.
2. **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature if available.

### What to Include

When reporting a vulnerability, please provide:

- **Description**: A clear, detailed description of the vulnerability.
- **Impact**: The potential impact and severity of the vulnerability.
- **Affected Components**: Which parts of the codebase are affected.
- **Reproduction Steps**: Detailed steps to reproduce the issue.
- **Proof of Concept**: If available, a minimal proof-of-concept demonstrating the vulnerability.
- **Suggested Fix**: If you have recommendations for remediation.
- **Your Contact Information**: So we can follow up with questions.

### Response Timeline

We are committed to the following response timeline:

| Action | Timeframe |
|--------|-----------|
| Initial acknowledgment | Within 48 hours |
| Preliminary assessment | Within 5 business days |
| Status update to reporter | Within 10 business days |
| Patch development | Varies by severity |
| Public disclosure | Coordinated with reporter |

### Severity Classification

We classify vulnerabilities using the following severity levels:

| Severity | Description | Response Priority |
|----------|-------------|-------------------|
| Critical | Remote code execution, authentication bypass, data breach | Immediate |
| High | Privilege escalation, significant data exposure | Within 7 days |
| Medium | Limited data exposure, denial of service | Within 30 days |
| Low | Minor issues, defense-in-depth improvements | Next release cycle |

## Disclosure Policy

### Coordinated Disclosure

We follow a coordinated disclosure process:

1. Reporter submits vulnerability report.
2. We acknowledge receipt and begin investigation.
3. We develop and test a fix.
4. We prepare a security advisory.
5. We notify the reporter of our planned disclosure date.
6. We release the patch and publish the advisory.
7. Reporter may publish their findings after the agreed-upon date.

### Disclosure Timeline

- **Standard vulnerabilities**: 90 days from report to public disclosure.
- **Critical vulnerabilities**: Expedited timeline based on severity.
- **Extended timeline**: Available if remediation requires complex changes.

We request that reporters:

- Allow reasonable time for investigation and remediation.
- Avoid accessing or modifying data belonging to others.
- Avoid exploiting the vulnerability beyond what is necessary to demonstrate it.
- Keep vulnerability details confidential until a patch is available.

## Security Best Practices for Users

### Deployment Security

When deploying Promethium, we recommend:

- **Use HTTPS**: Always deploy behind TLS/SSL termination.
- **Secure Secrets**: Use environment variables or secret management tools for sensitive configuration.
- **Limit Network Access**: Restrict database and Redis access to internal networks.
- **Regular Updates**: Keep Promethium and all dependencies up to date.
- **Access Control**: Implement proper authentication and authorization.

### Configuration Recommendations

```yaml
# Example secure configuration practices
security:
  # Use strong secret keys
  secret_key: "${PROMETHIUM_SECRET_KEY}"  # Set via environment variable
  
  # Configure secure JWT settings
  jwt_algorithm: "HS256"
  jwt_expiration_minutes: 60
  
  # Enable CORS only for trusted origins
  cors_origins:
    - "https://your-domain.com"
```

### Monitoring and Auditing

- Enable access logging for the API.
- Monitor for unusual access patterns.
- Regularly review authentication logs.
- Set up alerts for failed authentication attempts.

## Security Updates

Security updates are announced through:

- GitHub Security Advisories
- Release notes in [CHANGELOG.md](CHANGELOG.md)
- Project communication channels

We recommend subscribing to repository notifications to receive security update announcements.

## Acknowledgments

We gratefully acknowledge security researchers who responsibly disclose vulnerabilities. With the reporter's permission, we acknowledge their contribution in our security advisories.

---

Thank you for helping keep Promethium and its users safe.
