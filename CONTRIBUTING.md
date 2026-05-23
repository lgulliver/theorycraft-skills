# Contributing to theorycraft

Thanks for wanting to contribute. This document covers how the skills are structured, what makes a good contribution, and how to get changes merged.

---

## Where to start

The most useful contributions right now are **reference files for partial skills**. Several skills have a solid `SKILL.md` but thin or missing reference files — this means the skill works but gives shallower answers than it could.

Skills that would benefit most from reference file contributions:

| Skill | Missing references |
|---|---|
| `theorycraft-iaas` | `vm-sizing.md`, `iaas-networking.md`, `migration-patterns.md`, `iaas-finops.md` |
| `theorycraft-paas` | `app-platforms.md`, `managed-databases.md`, `managed-messaging.md`, `paas-finops.md` |
| `theorycraft-containers` | `topology-patterns.md`, `diagram-templates.md` |
| `theorycraft-serverless` | `workflow-patterns.md`, `serverless-observability.md`, `serverless-finops.md` |
| `theorycraft-aws` | `aws-networking.md`, `aws-security.md`, `aws-finops.md` |
| `theorycraft-gcp` | `gcp-networking.md`, `gcp-security.md`, `gcp-finops.md` |
| `theorycraft-azure` | `azure-networking.md`, `azure-security.md`, `azure-finops.md` |

The `SKILL.md` for each skill lists the expected reference files and what they should cover — use that as your spec.

---

## How skills are structured

```
skills/
└── theorycraft-<name>/
    ├── SKILL.md           ← required; orchestration layer and output structure
    └── references/        ← optional; domain-specific reference material
        └── <topic>.md
```

### SKILL.md

The `SKILL.md` has two parts:

**YAML frontmatter:**
```yaml
---
name: theorycraft-<name>
description: <trigger description — max 1024 characters>
---
```

The `description` is what Claude reads to decide whether to use the skill. It must be under 1024 characters. This is a hard limit — skills with longer descriptions will fail to install.

**Body:** markdown instructions telling Claude how to behave when the skill triggers. This includes phase structure, output sections, tone guidance, and pointers to reference files.

### Reference files

Reference files contain deeper domain knowledge that would make `SKILL.md` too long if included inline. The skill body tells Claude which reference files to read and when. Reference files should be self-contained — don't assume Claude has read another reference file unless the skill body explicitly chains them.

---

## What makes a good contribution

### For reference files

- **Specific, not generic.** "Use a managed database" is not useful. "Azure Database for PostgreSQL Flexible Server — Burstable B2ms for dev, General Purpose D4s_v3 for prod — because Flexible Server supports VNet injection and point-in-time restore to 35 days" is.
- **Decision guides, not just lists.** For every tool or service comparison, include a "when to choose X over Y" decision guide. The goal is to help Claude make a recommendation, not just enumerate options.
- **Honest about trade-offs.** Call out the downsides of each option. Skills that only list pros aren't useful.
- **Concrete examples.** Manifest snippets, CLI commands, cost figures, architecture patterns. The more concrete, the better.
- **Grounded in current practice.** Avoid deprecated approaches. Flag when something is changing (e.g. "Kubenet is being deprecated — use Azure CNI Overlay for new clusters").

### For SKILL.md changes

- **Don't add tool prescriptions without context.** The kubernetes skill learned this the hard way — prescribing Kyverno before knowing if the user already has Gatekeeper isn't helpful. Tools should be presented with selection criteria.
- **Keep descriptions under 1024 characters.** Check with `python3 -c "print(len('your description here'))"` before submitting.
- **Don't change the phase structure without discussion.** The Q&A → synthesis → output pattern is intentional. Open an issue first.

### For new skills

Open an issue before building. Include:
- What problem the skill solves
- Why an existing skill doesn't cover it
- Rough outline of what it would contain
- Whether it extends an existing skill or stands alone

New skills need to meet the same quality bar as existing ones — a `SKILL.md` with clear phase structure, well-defined output sections, and at least the core reference files stubbed out.

---

## Content guidelines

### Accuracy

Skills give architectural advice that people act on. Getting it wrong has real consequences. If you're not confident about something, either don't include it or flag the uncertainty explicitly ("verify current pricing before committing" is fine).

### Pricing and benchmarks

Cost figures date quickly. When including pricing:
- Always specify the date the figures were checked
- Include the region and pricing model (on-demand, reserved, etc.)
- Tell the reader to verify with the provider's pricing calculator
- Use ranges rather than point figures where possible

### Vendor neutrality

Skills should be tool-aware, not tool-partisan. Where genuine choices exist (Kyverno vs Gatekeeper, Argo CD vs Flux, etc.), present them with honest trade-offs and decision criteria — not a winner. Provider-specific skills (theorycraft-azure, theorycraft-aws, theorycraft-gcp) are explicitly provider-focused, but even they should acknowledge when a competing provider has a genuinely better approach to something.

### No proprietary or company-specific content

Reference files should be useful to anyone. Don't include content that only applies to a specific organisation's stack, naming conventions, or internal tooling. If you want to build company-specific extensions, fork the repo and add them in your own private overlay.

---

## Pull request process

1. **Fork** the repo and create a branch: `git checkout -b add-iaas-vm-sizing-reference`
2. **Make your changes** following the guidelines above
3. **Test your skill** — install the modified `.skill` file in Claude and run at least 3 representative prompts. Include the prompts and a summary of outputs in your PR description.
4. **Open a PR** with a clear description of what changed and why

> The `.skill` files and suite bundle are built automatically by CI when changes are merged to `main` or a release is published. You don't need to build them locally — just change the source files.

### PR description template

```markdown
## What changed
<!-- Which skill, which files, what content was added/changed -->

## Why
<!-- What gap does this fill, or what was wrong with the previous content -->

## Test prompts
<!-- At least 3 prompts you used to test the skill, with a brief note on whether the output improved -->

## Checklist
- [ ] Description is under 1024 characters (if SKILL.md was changed)
- [ ] Reference files follow the structure of existing ones
- [ ] Pricing figures include date checked and region
```

---

## Issue templates

### Bug report

Use this when a skill gives incorrect, outdated, or misleading advice. Include:
- Which skill
- The prompt you used
- What the skill said
- What it should have said (and why)

### Skill request

Use this to propose a new skill. Include the outline described in the "For new skills" section above.

---

## Local development

### Prerequisites
- Python 3.8+
- A Claude account with Skills enabled

### Building a skill file locally (optional)

CI handles this automatically, but you can also build locally:

```bash
python3 scripts/package.py skills/theorycraft-<name>
# Output: ./theorycraft-<name>.skill
```

Build all skills and the suite bundle:

```bash
python3 scripts/package.py --all --output dist/
# Output: dist/*.skill + dist/theorycraft-suite.zip
```

### Testing a skill

1. Run `python3 scripts/package.py skills/theorycraft-<name>`
2. In Claude, go to Settings → Skills → upload the `.skill` file
3. Start a new conversation and test with representative prompts
4. Check that the skill triggers correctly (not triggering when it shouldn't, triggering when it should)
5. Check that the output follows the structure defined in `SKILL.md`

---

## Questions

Open an issue with the `question` label. We'll answer there so the discussion is public and searchable.
