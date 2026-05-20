# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | Yes       |
| < 1.0   | No        |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in the Startup Valuation library, MCP server, or documentation site, please report it responsibly.

### How to Report

1. **Do NOT open a public issue** — security reports should be private
2. Go to [GitHub Security Advisories](https://github.com/simonplmak-cloud/startup-valuation/security/advisories/new) and submit a draft advisory
3. Alternatively, contact the maintainer directly via the repository

### What to Include

- Description of the vulnerability
- Steps to reproduce (with code examples if applicable)
- Potential impact assessment
- Suggested fix (if you have one)

### Response Timeline

- **72 hours**: Acknowledgment of your report
- **7 days**: Initial assessment and severity classification
- **30 days**: Fix release or mitigation plan (for confirmed vulnerabilities)

### Scope

This policy covers:
- Python library (`src/startup_valuation/`)
- MCP Server (`mcp_server/`)
- Documentation site (GitHub Pages)
- Build and CI/CD workflows

Out of scope:
- Third-party dependencies (report upstream)
- GitHub platform vulnerabilities (report to GitHub)

## Disclosure Policy

- Coordinated disclosure: we will work with you before any public disclosure
- Credit: reporters will be credited in the release notes (unless anonymity is requested)
- CVE: we will request a CVE ID for confirmed vulnerabilities
