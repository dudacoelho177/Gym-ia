"""Agente Gerador de Resumo (specs/phase-04/007): consolida DiscoveryState em ExecutiveUnderstanding."""
from __future__ import annotations

from app.domain.entities import DiscoveryState, ExecutiveUnderstanding
from app.domain.ports.llm_provider import LLMProvider


async def generate_executive_understanding(llm: LLMProvider, *, state: DiscoveryState, conversation_id: str, tenant_id: str) -> ExecutiveUnderstanding:
    result = await llm.generate_structured(
        system_prompt=(
            "Consolide o DiscoveryState em um entendimento executivo acionável, em português.\n"
            "Responda APENAS com um objeto JSON válido, sem markdown, sem texto antes ou depois, "
            "exatamente neste formato:\n"
            '{"summary": "string", "diagnosis": "string", "missing_information": ["string"], '
            '"risks": ["string"], "assumptions": ["string"], "next_steps": ["string"], '
            '"complexity": "baixa"|"media"|"alta"}'
        ),
        user_payload={
            "coverage_by_category": state.coverage_by_category,
            "overall_coverage": state.overall_coverage(),
        },
        response_schema_name="executive_summary",
    )
    content = result.content
    return ExecutiveUnderstanding(
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        summary=content.get("summary", ""),
        diagnosis=content.get("diagnosis", ""),
        missing_information=content.get("missing_information", []),
        risks=content.get("risks", []),
        assumptions=content.get("assumptions", []),
        next_steps=content.get("next_steps", []),
        complexity=content.get("complexity", "media"),
    )
