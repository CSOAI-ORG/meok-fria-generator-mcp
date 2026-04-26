"""meok-fria-generator-mcp — EU AI Act Article 27 Fundamental Rights Impact Assessment generator

Generates structured FRIA artifacts per EU AI Act Reg (EU) 2024/1689 Article 27,
mapped against the EDPB harmonised DPIA template (14 April 2026), with HMAC-signed
compliance attestations verifiable via meok-attestation-api.

The official EU AI Office FRIA template is not yet published as of April 2026.
This MCP is first-mover infrastructure for public-sector deployers and SaaS
vendors selling to them.

By MEOK AI Labs (https://meok.ai). MIT licensed.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meok-fria-generator")

ATTESTATION_API = os.environ.get("MEOK_ATTESTATION_API", "https://meok-attestation-api.vercel.app")

# EU AI Act Article 27 — FRIA mandatory fields (per Article 27(1)(a)-(g))
ARTICLE_27_FIELDS = {
    "a_deployer_processes": {
        "label": "Deployer's processes in which the system will be used",
        "guidance": "Describe each business process where the high-risk AI system will be deployed. "
        "Include process owner, throughput volume, decision-making authority of the AI vs human.",
    },
    "b_period_frequency_use": {
        "label": "Period and frequency of intended use",
        "guidance": "Time horizon (pilot 6mo / production 3yr / etc.) and frequency "
        "(real-time per request / batch nightly / etc.). Note any seasonality.",
    },
    "c_categories_persons_affected": {
        "label": "Categories of natural persons and groups likely affected",
        "guidance": "Affected populations (employees, customers, candidates, claimants, citizens, etc.). "
        "Include vulnerable groups protected under EU Charter (children, disabled, refugees, minorities).",
    },
    "d_specific_risks_harm": {
        "label": "Specific risks of harm likely to impact the categories of persons",
        "guidance": "Risks across: discrimination, dignity, privacy, freedom of expression, "
        "access to services, due process, mental health, economic outcomes. "
        "Use EU Charter of Fundamental Rights as the reference framework.",
    },
    "e_human_oversight_measures": {
        "label": "Measures of human oversight per Art. 14",
        "guidance": "How the natural persons assigned human oversight are enabled to: (a) understand "
        "system capacity, (b) interpret outputs, (c) decide not to use the output, (d) intervene/halt, "
        "(e) reverse outcomes. Specific roles, training, escalation paths.",
    },
    "f_internal_governance_complaint_mechanisms": {
        "label": "Internal governance + complaint mechanisms",
        "guidance": "Internal governance structure (AI ethics board, escalation paths). "
        "Complaint mechanisms for affected persons, including timelines and accessibility.",
    },
    "g_review_modify_obligations": {
        "label": "Periodic review of FRIA + obligations to update",
        "guidance": "Frequency of FRIA review (annual / per-deployment / per-significant-change). "
        "Triggers for re-review (regulatory change, incident, complaint volume).",
    },
}

# EDPB harmonised DPIA sections (14 April 2026 template) — overlap mapping
EDPB_DPIA_SECTIONS = [
    "1. Context of processing (legal basis, purpose, scope)",
    "2. Necessity & proportionality (data minimisation, retention)",
    "3. Risks to data subjects' rights and freedoms",
    "4. Measures + safeguards (technical + organisational)",
    "5. Sign-off (DPO + processing controller + risk owner)",
    "6. Consultation (DPA, data subjects, third parties)",
    "7. Review schedule + version control",
    "8. Annex — flowcharts, ROPA cross-references, technical specs",
    "9. Annex — DPO recommendation summary",
]

# Crosswalk: which Art. 27 FRIA fields map to which EDPB DPIA sections
FRIA_DPIA_CROSSWALK = {
    "a_deployer_processes": ["1. Context of processing"],
    "b_period_frequency_use": ["2. Necessity & proportionality"],
    "c_categories_persons_affected": ["1. Context of processing", "3. Risks to data subjects"],
    "d_specific_risks_harm": ["3. Risks to data subjects' rights and freedoms"],
    "e_human_oversight_measures": ["4. Measures + safeguards"],
    "f_internal_governance_complaint_mechanisms": ["4. Measures + safeguards", "6. Consultation"],
    "g_review_modify_obligations": ["7. Review schedule + version control"],
}

# When FRIA is mandatory (per Article 27(1))
FRIA_MANDATORY_TRIGGERS = [
    "Body governed by public law (Member State or EU institution)",
    "Private operator providing public services (e.g., recruitment for public-sector roles, education, healthcare)",
    "Deploying a high-risk AI system listed in Annex III",
    "Specifically: credit scoring (Annex III §5(b))",
    "Specifically: life/health insurance pricing (Annex III §5(c))",
]

# EU Charter of Fundamental Rights — articles most relevant to AI deployer FRIA
CHARTER_REFERENCE = {
    "Art. 1": "Human dignity",
    "Art. 7": "Respect for private and family life",
    "Art. 8": "Protection of personal data",
    "Art. 11": "Freedom of expression and information",
    "Art. 14": "Right to education",
    "Art. 15": "Freedom to choose an occupation and right to engage in work",
    "Art. 21": "Non-discrimination",
    "Art. 23": "Equality between women and men",
    "Art. 24": "Rights of the child",
    "Art. 25": "Rights of the elderly",
    "Art. 26": "Integration of persons with disabilities",
    "Art. 31": "Fair and just working conditions",
    "Art. 34": "Social security and social assistance",
    "Art. 35": "Health care",
    "Art. 41": "Right to good administration",
    "Art. 47": "Right to an effective remedy and to a fair trial",
}


@mcp.tool()
def is_fria_required(
    organisation_type: str,
    is_public_law_body: bool = False,
    provides_public_service: bool = False,
    annex_iii_categories: list[str] | None = None,
) -> dict[str, Any]:
    """Determine if a FRIA is mandatory under EU AI Act Article 27 for this deployment.

    Args:
        organisation_type: One of public-authority / private-operator / SaaS-vendor / individual.
        is_public_law_body: True if the organisation is a body governed by Member State or EU public law.
        provides_public_service: True if the organisation provides services in a public-service context
            (recruitment for public sector, education, healthcare, social services, etc.).
        annex_iii_categories: List of Annex III high-risk categories the system falls under.
            E.g., ["employment-and-workforce", "education-and-vocational-training", "credit-scoring"].

    Returns:
        Decision + rationale + Article 27 reference.
    """
    annex_iii_categories = annex_iii_categories or []

    # Specifically mandatory categories per Article 27(1)
    always_mandatory = {"credit-scoring", "life-insurance-pricing", "health-insurance-pricing"}
    has_always_mandatory = bool(set(annex_iii_categories) & always_mandatory)

    is_mandatory = False
    rationale = []

    if is_public_law_body:
        is_mandatory = True
        rationale.append("Public-law body — Article 27(1) mandates FRIA for all bodies governed by public law")
    if provides_public_service:
        is_mandatory = True
        rationale.append(
            "Provides public service — Article 27(1) extends FRIA obligation to private operators "
            "providing public services"
        )
    if has_always_mandatory:
        is_mandatory = True
        cats = sorted(set(annex_iii_categories) & always_mandatory)
        rationale.append(
            f"Always-mandatory category triggered: {cats} — Article 27(1) requires FRIA "
            f"regardless of organisation type for credit/insurance pricing"
        )

    if not is_mandatory and annex_iii_categories:
        rationale.append(
            "Not strictly mandatory under Art. 27, but Annex III high-risk system — STRONGLY "
            "RECOMMENDED to conduct a FRIA-equivalent assessment as best practice"
        )

    return {
        "fria_mandatory": is_mandatory,
        "rationale": rationale,
        "annex_iii_categories": annex_iii_categories,
        "regulatory_basis": "EU AI Act Reg (EU) 2024/1689 Article 27",
        "deadline": "FRIA must be completed BEFORE first deployment of the high-risk AI system",
        "review_obligation": "Article 27(2) — update FRIA when deployer's processes, risks, or "
        "circumstances change materially",
    }


@mcp.tool()
def generate_fria_template(
    deployer_name: str,
    ai_system_name: str,
    annex_iii_category: str,
    expected_users: int = 1000,
    geographic_scope: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a FRIA template structure with all 7 mandatory Article 27 fields populated as guidance.

    Args:
        deployer_name: Legal name of the deployer (e.g., "Acme Hiring Ltd").
        ai_system_name: Name of the AI system being deployed.
        annex_iii_category: Annex III category (e.g., "employment-and-workforce").
        expected_users: Estimated count of natural persons whose data will be processed.
        geographic_scope: List of country codes (e.g., ["DE", "FR", "IE"]).

    Returns:
        Structured FRIA template ready for completion by the deployer's compliance team.
    """
    geographic_scope = geographic_scope or ["EU-27"]
    today = datetime.now(timezone.utc).date().isoformat()

    sections = {}
    for field_id, field in ARTICLE_27_FIELDS.items():
        sections[field_id] = {
            "label": field["label"],
            "guidance": field["guidance"],
            "deployer_response": "[TO BE COMPLETED BY DEPLOYER]",
            "edpb_dpia_overlap": FRIA_DPIA_CROSSWALK.get(field_id, []),
        }

    return {
        "fria_template_metadata": {
            "deployer": deployer_name,
            "ai_system": ai_system_name,
            "annex_iii_category": annex_iii_category,
            "expected_user_count": expected_users,
            "geographic_scope": geographic_scope,
            "drafted_on": today,
            "drafted_by_tool": "meok-fria-generator-mcp",
            "tool_version": "1.0.0",
            "regulatory_basis": "EU AI Act Reg (EU) 2024/1689 Article 27",
        },
        "sections": sections,
        "charter_reference": CHARTER_REFERENCE,
        "review_schedule": {
            "default_review_period": "12 months",
            "trigger_based_review": [
                "Material change to deployer processes",
                "Substantive complaint received via complaint mechanism (Art. 27(1)(f))",
                "Regulatory guidance from EU AI Office or national supervisory authority",
                "Significant model update (>5% performance shift on validation set)",
                "Geographic expansion to new Member State",
            ],
        },
        "delivery_format": {
            "primary": "PDF + machine-readable JSON-LD",
            "regulator_request_format": "Per supervisory authority (typically PDF + structured annex)",
            "retention": "Minimum 10 years per Article 18 (post-deployment)",
        },
    }


@mcp.tool()
def map_to_edpb_dpia(annex_iii_category: str) -> dict[str, Any]:
    """Map FRIA fields to EDPB harmonised DPIA template (14 April 2026) sections to avoid double work.

    Args:
        annex_iii_category: Annex III category for context.

    Returns:
        Crosswalk showing which FRIA fields satisfy which DPIA sections.
    """
    return {
        "annex_iii_category": annex_iii_category,
        "crosswalk": FRIA_DPIA_CROSSWALK,
        "fria_only_fields": [
            "Article 27(1)(e) human oversight per Art. 14 — narrower than DPIA Art. 35",
            "Article 27(1)(f) complaint mechanisms — explicit FRIA requirement, not in DPIA",
            "Article 27(1)(g) periodic review obligation — different cadence rules than DPIA",
        ],
        "dpia_only_fields": [
            "Section 6 — DPA consultation (DPIA-specific, not in FRIA)",
            "Section 8 — ROPA cross-references (DPIA-specific data-protection focus)",
            "Section 9 — DPO recommendation (DPIA-specific accountability)",
        ],
        "shared_evidence_strategy": (
            "Author one combined assessment with FRIA fields explicitly tagged. "
            "Submit FRIA fields to AI Act supervisor; submit DPIA sections to DPA. "
            "Single evidence pack avoids duplicate effort."
        ),
        "edpb_template_reference": "EDPB harmonised DPIA template (adopted 14 April 2026)",
    }


@mcp.tool()
def signed_fria_attestation(
    deployer_name: str,
    ai_system_name: str,
    annex_iii_category: str,
    completed_sections: list[str],
    sign_off_role: str = "compliance-lead",
) -> dict[str, Any]:
    """Produce an HMAC-signed FRIA attestation via the public meok-attestation-api.

    Args:
        deployer_name: Legal name of the deployer.
        ai_system_name: Name of the AI system.
        annex_iii_category: Annex III category.
        completed_sections: List of FRIA section IDs that have been completed (e.g., ["a_deployer_processes", "b_period_frequency_use"]).
        sign_off_role: Role of the signer.

    Returns:
        Signed attestation with verification URL.
    """
    payload = {
        "kind": "fria-attestation",
        "deployer": deployer_name,
        "ai_system": ai_system_name,
        "annex_iii_category": annex_iii_category,
        "completed_sections": completed_sections,
        "missing_sections": [
            sid for sid in ARTICLE_27_FIELDS.keys() if sid not in completed_sections
        ],
        "sign_off_role": sign_off_role,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "regulatory_basis": "EU AI Act Reg (EU) 2024/1689 Article 27",
        "tool": "meok-fria-generator-mcp",
        "tool_version": "1.0.0",
    }

    try:
        req = urllib.request.Request(
            f"{ATTESTATION_API}/sign",
            data=json.dumps({"payload": payload, "type": "fria"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": True,
            "payload": payload,
            "signature": result.get("signature"),
            "verify_url": result.get("verify_url"),
            "attestation_id": result.get("attestation_id"),
        }
    except urllib.error.URLError as e:
        return {
            "ok": False,
            "error": f"attestation API unreachable: {e}",
            "payload": payload,
            "fallback": "Use payload above as self-attestation; sign locally with your own HMAC key.",
        }


@mcp.tool()
def list_charter_articles() -> dict[str, str]:
    """List EU Charter of Fundamental Rights articles relevant to AI deployer FRIA."""
    return CHARTER_REFERENCE


@mcp.tool()
def list_mandatory_triggers() -> dict[str, Any]:
    """List the conditions that make a FRIA mandatory under Article 27(1)."""
    return {
        "mandatory_triggers": FRIA_MANDATORY_TRIGGERS,
        "regulatory_basis": "EU AI Act Reg (EU) 2024/1689 Article 27(1)",
    }


@mcp.tool()
def pricing() -> dict[str, Any]:
    """Pricing for MEOK FRIA Generator."""
    return {
        "free_tier": {
            "price": "£0",
            "features": [
                "All FRIA generation tools",
                "Public attestation API (shared HMAC issuer)",
                "MIT-licensed source code",
                "EDPB DPIA crosswalk included",
            ],
        },
        "pro": {
            "price": "£79/mo",
            "features": [
                "Free tier + your own HMAC signing key",
                "Custom verify domain (your-firm.com/verify)",
                "Email support",
                "FRIA template versioning + diff tracking",
            ],
        },
        "enterprise": {
            "price": "£1,499/mo",
            "features": [
                "Pro tier + multi-deployment FRIA management for groups",
                "SLA on attestation API (99.9%)",
                "Direct slack/teams support channel",
                "Reseller white-label for compliance consultancies",
            ],
            "fit": "Public-sector deployers with multiple Annex III systems; consultancies "
            "running concurrent FRIA engagements",
        },
        "bespoke": {
            "price": "from £5,000",
            "features": [
                "Self-hosted attestation API on your infrastructure",
                "GRC stack integrations (Archer, ServiceNow, OneTrust)",
                "On-site FRIA workshop (1 day)",
            ],
        },
        "purchase": "https://meok.ai/pricing",
        "contact": "nicholas@csoai.org",
    }


if __name__ == "__main__":
    mcp.run()
