# dash-spec-updater Skill - Deployment Summary

## Overview
Ensures SPEC.md (user-facing dashboard documentation) stays synchronized with Plotly Dash dashboard implementation changes.

## Multi-Layer Enforcement Architecture

This skill uses a **3-layer approach** to ensure compliance:

### Layer 1: Project-Level Requirement (CLAUDE.md)
```markdown
### SPEC.md 必須ルール（MANDATORY）
- 全ダッシュボードページには `SPEC.md` を配置すること
- 更新タイミング: フィルタ、チャート、KPI、テーブルを追加・修正した際は必ずSPEC.mdも更新
- 詳細: `dash-spec-updater` スキルを参照
```

**Why:** Makes SPEC.md a project-wide mandatory requirement

### Layer 2: Skill Auto-Trigger (Enhanced Description)
```yaml
description: Use when user requests dashboard changes or starting implementation of filters, charts, KPIs, tables in src/pages/ - mandatory SPEC.md update checklist must be included in plan before implementation
```

**Why:** Triggers at planning phase ("starting implementation"), not post-completion

### Layer 3: Implementation Guide (SKILL.md)
- Workflow flowchart with SPEC.md as mandatory step
- Template and format requirements (日本語, user-facing, no technical details)
- Counter-rationalizations table
- Detection logic for modified dashboards

**Why:** Provides HOW to update SPEC.md correctly

## Test Results

| Pressure Type | Baseline (No Protection) | With Multi-Layer | Improvement |
|---------------|-------------------------|------------------|-------------|
| Time (5 min deadline) | 0% SPEC.md update | 100% proactive update | ✅ Fixed |
| Sunk Cost (30 min invested) | 50% random | 100% proactive update | ✅ Fixed |
| New Feature | N/A | 100% proactive update | ✅ Fixed |

## Usage

### As a User
Invoke explicitly when needed:
```bash
/dash-spec-updater
```

### As an Agent
The skill auto-triggers when:
- User requests dashboard changes ("add filter", "new KPI", etc.)
- Starting implementation in `src/pages/*/`
- CLAUDE.md mandate applies

## Files

- `SKILL.md` - Main skill documentation (703 words)
- `README.md` - This deployment summary

## Integration Status

- ✅ Deployed as Project Skill to `.claude/skills/dash-spec-updater/`
- ✅ CLAUDE.md updated with mandatory requirement
- ✅ Tested and verified working
- ✅ Scoped to this project only (not global user skill)

## Maintenance

When updating the skill:
1. Follow TDD: Create failing test first
2. Update SKILL.md
3. Re-test with pressure scenarios
4. Update this README if architecture changes

## Related Skills

- `dash-bi-workflow` - Main dashboard development workflow
- `etl-workflow` - Data pipeline development

## Created

2026-02-07 by TDD methodology (RED-GREEN-REFACTOR)
