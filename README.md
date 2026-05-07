[![meok-fria-generator-mcp MCP server](https://glama.ai/mcp/servers/CSOAI-ORG/meok-fria-generator-mcp/badges/card.svg)](https://glama.ai/mcp/servers/CSOAI-ORG/meok-fria-generator-mcp)

# meok-fria-generator-mcp

[![PyPI](https://img.shields.io/pypi/v/meok-fria-generator-mcp.svg)](https://pypi.org/project/meok-fria-generator-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-server-purple)](https://modelcontextprotocol.io)

> EU AI Act Article 27 Fundamental Rights Impact Assessment (FRIA) generator. EDPB DPIA crosswalk, EU Charter of Fundamental Rights mapping, HMAC-signed compliance attestations.

**By [MEOK AI Labs](https://meok.ai)** · MIT licensed · runs as an [MCP server](https://modelcontextprotocol.io) inside Claude Code, Cursor, Cline, Windsurf, etc.

---

## Why this exists

EU AI Act Reg (EU) 2024/1689 Article 27 mandates that **public-law bodies and private operators providing public services** complete a Fundamental Rights Impact Assessment **before** deploying a high-risk AI system.

The official EU AI Office FRIA template is **not yet published** (April 2026). Existing free tools (ALIGNER, AIActStack, kla.digital) are template generators — none are MCP-callable, none ship signed attestations.

This MCP gives compliance teams a structured, callable, signed-FRIA workflow today, mapped against the EDPB harmonised DPIA template (14 April 2026) so the same evidence pack satisfies both AI Act and GDPR auditors.

## Tools

| Tool | Use |
|---|---|
| `is_fria_required` | Decide if FRIA is mandatory under Article 27(1) for a given deployment |
| `generate_fria_template` | Produce a structured FRIA template with all 7 mandatory Article 27 fields |
| `map_to_edpb_dpia` | Crosswalk FRIA fields ↔ EDPB DPIA sections to share evidence |
| `signed_fria_attestation` | HMAC-sign your completed FRIA via meok-attestation-api |
| `list_charter_articles` | EU Charter of Fundamental Rights articles relevant to AI deployer FRIA |
| `list_mandatory_triggers` | Conditions that trigger Article 27(1) FRIA obligation |
| `pricing` | Pricing tiers (free / £79 Pro / £1,499 Enterprise / from £5K bespoke) |

## Install

```bash
pip install meok-fria-generator-mcp
```

Then in your Claude Code / Cursor MCP config:

```json
{
  "mcpServers": {
    "meok-fria-generator": {
      "command": "python",
      "args": ["-m", "meok_fria_generator"]
    }
  }
}
```

## Example use

> "Is a FRIA mandatory if we're a UK public-sector recruitment provider deploying a CV-screening AI in EU markets? Annex III categories: employment-and-workforce."

Claude calls `is_fria_required(...)` and returns a structured decision: YES, mandatory because (a) provides-public-service AND (b) Annex III high-risk category. Returns the rationale, the regulatory basis, and the deadline (before first deployment).

> "Generate a FRIA template for Acme Public Services Ltd's CV-screening AI. Expected 50,000 candidates/year, deployed in DE, FR, IE."

Claude returns a structured template with all 7 Article 27 fields, EU Charter article references, EDPB DPIA crosswalk, and review-trigger schedule.

## Article 27 mandatory triggers

FRIA is mandatory when:

1. The deployer is a **body governed by public law** (Member State or EU institution)
2. The deployer is a **private operator providing public services** (recruitment for public sector, education, healthcare, etc.)
3. The deployment is a **high-risk Annex III system**
4. **Always-mandatory categories** (regardless of organisation type):
   - Credit scoring (Annex III §5(b))
   - Life/health insurance pricing (Annex III §5(c))

## Compliance posture

- **EU AI Act Reg (EU) 2024/1689** Article 27 (FRIA — mandatory for public-sector + Annex III deployers)
- **EU Charter of Fundamental Rights** (cross-referenced for risk identification)
- **EDPB Harmonised DPIA Template** (14 April 2026 — for GDPR Article 35 overlap)
- **Article 14** (human oversight requirements feeding into FRIA section (e))

## Pricing

- **Free** — full toolset, public attestation API
- **£79/mo Pro** — your own HMAC signing key + custom verify domain + FRIA versioning
- **£1,499/mo Enterprise** — multi-deployment FRIA management + SLA + reseller white-label
- **from £5,000 bespoke** — self-hosted attestation + GRC integrations + on-site workshop

Buy: https://meok.ai/pricing · Contact: nicholas@csoai.org

## License

MIT. © 2026 Nicholas Templeman / CSOAI LTD (UK Companies House 16939677).

## See also

- [meok-eu-ai-act-compliance-mcp](https://github.com/CSOAI-ORG/eu-ai-act-compliance-mcp) — broader EU AI Act compliance toolkit
- [meok-dpia-edpb-template-mcp](https://github.com/CSOAI-ORG/meok-dpia-edpb-template-mcp) — EDPB harmonised DPIA template
- [meok-attestation-api](https://meok-attestation-api.vercel.app/health) — public verifiable attestation infrastructure
