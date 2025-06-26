# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

The API Monitoring team and community take security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

To report a security issue, please use the GitHub Security Advisory ["Report a Vulnerability"](https://github.com/dkamenkov/api-monitoring/security/advisories/new) tab.

The API Monitoring team will send a response indicating the next steps in handling your report. After the initial reply to your report, the security team will keep you informed of the progress towards a fix and full announcement, and may ask for additional information or guidance.

### What to include in your report

Please include the following information in your security report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### Preferred Languages

We prefer all communications to be in English.

## Security Best Practices

When using API Monitoring, please follow these security best practices:

### Environment Variables and Secrets

- Never commit sensitive information like API keys, tokens, or passwords to version control
- Use environment variables or secure secret management systems
- Regularly rotate your API keys and tokens
- Use the principle of least privilege for AWS credentials

### Network Security

- Use HTTPS endpoints whenever possible
- Implement proper firewall rules
- Consider using VPN or private networks for sensitive deployments
- Monitor network traffic for unusual patterns

### Container Security

- Regularly update the base Docker image
- Scan container images for vulnerabilities
- Use non-root users in containers when possible
- Implement proper resource limits

### Monitoring and Logging

- Monitor application logs for security events
- Implement proper log retention policies
- Use structured logging for better analysis
- Set up alerts for suspicious activities

## Security Updates

Security updates will be released as soon as possible after a vulnerability is confirmed and a fix is developed. Updates will be announced through:

- GitHub Security Advisories
- Release notes
- CHANGELOG.md

## Acknowledgments

We would like to thank the following individuals for their responsible disclosure of security vulnerabilities:

<!-- This section will be updated as we receive security reports -->

## Contact

For any questions about this security policy, please contact the maintainers through GitHub issues or discussions.