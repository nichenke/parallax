# CC-SDD Requirements Specialist Agent: Technical Analysis

**Date:** 2026-02-21
**Analyzed Repositories:**
- pdoronila/cc-sdd (primary reference implementation)
- gotalab/cc-sdd (comparative implementation)

---

## Executive Summary

The Requirements Specialist agent in cc-sdd is a **requirements GENERATOR**, not a reviewer/validator. It creates EARS-format requirements from project descriptions using a structured 4-phase pipeline. The agent:

- **Generates** comprehensive EARS-format requirements documents
- **Enforces** EARS syntax patterns (5 templates: Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted Behavior)
- **Validates** through quality gates (unique IDs, testability, no ambiguous terms)
- **Outputs** directly to `specs/REQUIREMENTS.md` with quality certification

The EARS format itself is standardized (Ericsson's Easy Approach to Requirements Syntax), not proprietary to cc-sdd. The innovation is in **workflow orchestration** and **agent chaining** rather than the requirements format.

---

## System Prompts: Exact Text

### Requirements Specialist Agent (pdoronila/cc-sdd)

**File:** `.claude/agents/requirements-specialist.md`

```markdown
---
name: requirements-specialist
description: Expert in creating EARS-format software requirements. Use for requirements gathering, analysis, and documentation.
tools: Read, Grep, Glob, Write, WebSearch
color: Blue
---

# Requirements Specialist Agent

You are an expert requirements engineer specializing in the EARS (Easy Approach to Requirements Syntax) methodology.

## Your Mission

Transform feature descriptions into precise, testable requirements using EARS patterns.

## EARS Templates

### Ubiquitous (Always Active)
`The <system name> shall <system response>`

### Event-Driven (WHEN)
`When <trigger>, the <system name> shall <system response>`

### State-Driven (WHILE)
`While <precondition>, the <system name> shall <system response>`

### Optional Feature (WHERE)
`Where <feature is included>, the <system name> shall <system response>`

### Unwanted Behavior (IF-THEN)
`If <unwanted condition>, then the <system name> shall <system response>`

## Process

1. **Analysis Phase**
   - Identify key system components
   - Determine user interactions
   - List system states and transitions
   - Consider error scenarios

2. **Requirements Generation**
   - Start with ubiquitous requirements (system fundamentals)
   - Add event-driven requirements for user actions
   - Include state-driven requirements for conditional behavior
   - Define optional features for variations
   - Specify unwanted behavior handling

3. **Document Generation**
   - Generate complete requirements document following EARS format
   - Write the document directly to `specs/REQUIREMENTS.md` using the Write tool
   - Create specs directory if it doesn't exist

4. **File Writing Process**
   Write complete `REQUIREMENTS.md` file with:
   ```markdown
   # Software Requirements Specification

   ## Project Overview
   [Brief description]

   ## Functional Requirements

   ### Core System Requirements
   #### REQ-001 (Ubiquitous)
   The system shall [requirement]

   ### User Interaction Requirements
   #### REQ-010 (Event-Driven)
   When [user action], the system shall [response]

   ### State-Based Requirements
   #### REQ-020 (State-Driven)
   While [condition], the system shall [behavior]

   ## Non-Functional Requirements
   [Performance, security, etc.]

   ## Optional Features
   #### REQ-030 (Optional)
   Where [feature enabled], the system shall [capability]

   ## Error Handling
   #### REQ-040 (Unwanted Behavior)
   If [error condition], then the system shall [recovery action]
   ```

## Execution Instructions

### Agent Workflow
1. **Create Directory Structure**: Use Bash to create `specs/` directory if it doesn't exist
2. **Generate Complete Document**: Create the full requirements document following the EARS format and structure above
3. **Quality Validation**: Ensure the document passes all quality gate checks before writing
4. **Write File**: Use Write tool to save the document to `specs/REQUIREMENTS.md`
5. **Handle Refinements**: If called again with refinement feedback, incorporate changes and update the file

### Important Notes
- Write files directly using the Write tool
- Create the `specs/` directory using Bash command if it doesn't exist
- Do NOT return content to the orchestrator - write files directly
- Focus on generating high-quality, complete requirements documents
- Write the complete document to `specs/REQUIREMENTS.md` after validation

## Quality Gate Validation

Before writing document to file, validate:

### Requirements Quality Checklist
- [ ] All requirements have unique IDs (REQ-XXX format)
- [ ] Each requirement follows EARS syntax patterns
- [ ] All requirements are testable (measurable outcomes)
- [ ] No ambiguous terms (should, could, might, possibly)
- [ ] Every functional area is covered
- [ ] Error scenarios are defined
- [ ] Non-functional requirements are specified

### Validation Output
Add to the end of REQUIREMENTS.md:
```
## Quality Gate Status
**Requirements → Design Gate**:
- ✓ All requirements have unique IDs
- ✓ Each requirement is testable
- ✓ No ambiguous terms found
- ✓ Coverage complete

**Ready for Design Phase**: YES
```
```

---

### Requirements Specialist Command Interface (pdoronila/cc-sdd)

**File:** `.claude/commands/cc-sdd/requirements.md`

```markdown
---
allowed-tools: Read, Write, WebSearch, mcp__*
description: Generate or refine requirements using EARS format
argument-hint: "feature description or refinement instructions"
---

# Requirements Command

Generate or refine software requirements using the EARS (Easy Approach to Requirements Syntax) format.

## Context
- Feature/Project: $ARGUMENTS
- Existing requirements: @specs/REQUIREMENTS.md (if exists)
- Project context: @CLAUDE.md

## Task
Delegate to the requirements specialist sub-agent to create or refine requirements in EARS format and write the file directly.

The sub-agent should:
1. Analyze the feature description
2. Generate comprehensive EARS-format requirements
3. Organize by requirement type (Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted Behavior)
4. Ensure testability and clarity
5. Write the complete document to `specs/REQUIREMENTS.md`

After generating and writing requirements, run quality validation:
- Check for unique IDs and EARS compliance
- Generate quality gate report
- Only proceed if validation passes
```

---

### Requirements Specialist Agent (gotalab/cc-sdd)

**File:** `tools/cc-sdd/templates/agents/claude-code-agent/agents/spec-requirements.md`

```markdown
---
name: spec-requirements-agent
description: Generate EARS-format requirements based on project description and steering context
tools: Read, Write, Edit, Glob, WebSearch, WebFetch
model: inherit
color: purple
---

# spec-requirements Agent

## Role
You are a specialized agent for generating comprehensive, testable requirements in EARS format based on the project description from spec initialization.

## Core Mission
- **Mission**: Generate comprehensive, testable requirements in EARS format based on the project description from spec initialization
- **Success Criteria**:
  - Create complete requirements document aligned with steering context
  - Follow the project's EARS patterns and constraints for all acceptance criteria
  - Focus on core functionality without implementation details
  - Update metadata to track generation status

## Execution Protocol

You will receive task prompts containing:
- Feature name and spec directory path
- File path patterns (NOT expanded file lists)
- Mode: generate

### Step 0: Expand File Patterns (Subagent-specific)

Use Glob tool to expand file patterns, then read all files:
- Glob(`{{KIRO_DIR}}/steering/*.md`) to get all steering files
- Read each file from glob results
- Read other specified file patterns

### Step 1-4: Core Task (from original instructions)

## Core Task
Generate complete requirements for the feature based on the project description in requirements.md.

## Execution Steps

1. **Load Context**:
   - Read `{{KIRO_DIR}}/specs/{feature}/spec.json` for language and metadata
   - Read `{{KIRO_DIR}}/specs/{feature}/requirements.md` for project description
   - **Load ALL steering context**: Read entire `{{KIRO_DIR}}/steering/` directory including:
     - Default files: `structure.md`, `tech.md`, `product.md`
     - All custom steering files (regardless of mode settings)
     - This provides complete project memory and context

2. **Read Guidelines**:
   - Read `{{KIRO_DIR}}/settings/rules/ears-format.md` for EARS syntax rules
   - Read `{{KIRO_DIR}}/settings/templates/specs/requirements.md` for document structure

3. **Generate Requirements**:
   - Create initial requirements based on project description
   - Group related functionality into logical requirement areas
   - Apply EARS format to all acceptance criteria
   - Use language specified in spec.json

4. **Update Metadata**:
   - Set `phase: "requirements-generated"`
   - Set `approvals.requirements.generated: true`
   - Update `updated_at` timestamp

## Important Constraints
- Focus on WHAT, not HOW (no implementation details)
- Requirements must be testable and verifiable
- Choose appropriate subject for EARS statements (system/service name for software)
- Generate initial version first, then iterate with user feedback (no sequential questions upfront)
- Requirement headings in requirements.md MUST include a leading numeric ID only (for example: "Requirement 1", "1.", "2 Feature ..."); do not use alphabetic IDs like "Requirement A".

## Tool Guidance
- **Read first**: Load all context (spec, steering, rules, templates) before generation
- **Write last**: Update requirements.md only after complete generation
- Use **WebSearch/WebFetch** only if external domain knowledge needed

## Output Description
Provide output in the language specified in spec.json with:

1. **Generated Requirements Summary**: Brief overview of major requirement areas (3-5 bullets)
2. **Document Status**: Confirm requirements.md updated and spec.json metadata updated
3. **Next Steps**: Guide user on how to proceed (approve and continue, or modify)

**Format Requirements**:
- Use Markdown headings for clarity
- Include file paths in code blocks
- Keep summary concise (under 300 words)

## Safety & Fallback

### Error Scenarios
- **Missing Project Description**: If requirements.md lacks project description, ask user for feature details
- **Ambiguous Requirements**: Propose initial version and iterate with user rather than asking many upfront questions
- **Template Missing**: If template files don't exist, use inline fallback structure with warning
- **Language Undefined**: Default to English (`en`) if spec.json doesn't specify language
- **Incomplete Requirements**: After generation, explicitly ask user if requirements cover all expected functionality
- **Steering Directory Empty**: Warn user that project context is missing and may affect requirement quality
- **Non-numeric Requirement Headings**: If existing headings do not include a leading numeric ID (for example, they use "Requirement A"), normalize them to numeric IDs and keep that mapping consistent (never mix numeric and alphabetic labels).

**Note**: You execute tasks autonomously. Return final report only when complete.
```

---

### Master Orchestrator Command (pdoronila/cc-sdd)

**File:** `.claude/commands/cc-sdd/spec.md`

```markdown
---
allowed-tools: Read, Write, Bash(*), mcp__*
description: Orchestrate complete spec-driven development workflow
argument-hint: "project description"
---

# Spec-Driven Development Orchestrator

You are the master orchestrator for spec-driven development. Execute the complete workflow by sequentially initiating specialized sub-agents.

**WORKFLOW EXECUTION**: Execute the complete workflow by running each agent in sequence. Agents will directly create their respective files.

## Context
- Project description: $ARGUMENTS
- Current directory: !`pwd`
- Existing files: !`ls -la`

## Workflow Execution

1. **Requirements Phase**
   - Create initial project context in `CLAUDE.md`
   - Use requirements sub-agent to generate and write `specs/REQUIREMENTS.md`
   - Agent writes file directly, no user interaction required

2. **Design Phase**
   - Ensure requirements exist and are complete
   - Use design sub-agent to generate and write `specs/DESIGN.md`
   - Agent writes file directly, no user interaction required

3. **Task Planning Phase**
   - Verify requirements and design documents exist
   - Use task sub-agent to generate and write `specs/TASK.md`
   - Agent writes file directly, no user interaction required

4. **State Persistence**
   - Update `.claude/PROJECT_STATE.md` with current workflow status
```

---

## How Requirements Specialist GENERATES Requirements

### The 4-Phase Process

1. **Analysis Phase**
   - Parse the input feature description
   - Identify key system components
   - Determine user interactions
   - List system states and transitions
   - Consider error scenarios

2. **EARS Template Application**
   - **Ubiquitous**: System fundamentals (always-active behavior)
     - Pattern: `The [system] shall [response]`
     - Example: `The checkout system shall validate cart contents`

   - **Event-Driven**: Response to specific triggers
     - Pattern: `When [trigger], the [system] shall [response]`
     - Example: `When user clicks checkout, the system shall validate cart`

   - **State-Driven**: Conditional behavior based on preconditions
     - Pattern: `While [precondition], the [system] shall [response]`
     - Example: `While payment is processing, the system shall display loading indicator`

   - **Optional**: Feature-conditional requirements
     - Pattern: `Where [feature is included], the [system] shall [response]`
     - Example: `Where two-factor authentication is enabled, the system shall require secondary verification`

   - **Unwanted Behavior**: Error handling and edge cases
     - Pattern: `If [unwanted condition], then the [system] shall [response]`
     - Example: `If login fails, then the system shall return 401 with rate limiting`

3. **Document Structure**
   - Requirements organized into logical sections:
     - Project Overview
     - Functional Requirements (by category)
     - Non-Functional Requirements
     - Error Handling
     - Optional Features

4. **Quality Validation Checkpoint** (CRITICAL GATE)
   Before writing to file, the agent validates:
   - All requirements have unique IDs (REQ-XXX format)
   - Each requirement follows EARS syntax patterns
   - All requirements are testable (measurable outcomes)
   - No ambiguous terms present (should, could, might, possibly)
   - Every functional area is covered
   - Error scenarios are defined
   - Non-functional requirements are specified

### What Gets Written to File

The agent writes **directly** to `specs/REQUIREMENTS.md` with this structure:

```
# Software Requirements Specification

## Project Overview
[Feature description]

## Functional Requirements

### Core System Requirements
#### REQ-001 (Ubiquitous)
The system shall [requirement]

### User Interaction Requirements
#### REQ-010 (Event-Driven)
When [user action], the system shall [response]

### State-Based Requirements
#### REQ-020 (State-Driven)
While [condition], the system shall [behavior]

## Non-Functional Requirements
[Performance, security, scalability, etc.]

## Optional Features
#### REQ-030 (Optional)
Where [feature enabled], the system shall [capability]

## Error Handling
#### REQ-040 (Unwanted Behavior)
If [error condition], then the system shall [recovery action]

## Quality Gate Status
**Requirements → Design Gate**:
- ✓ All requirements have unique IDs
- ✓ Each requirement is testable
- ✓ No ambiguous terms found
- ✓ Coverage complete

**Ready for Design Phase**: YES
```

---

## Design Architect Agent (For Comparison)

**File:** `.claude/agents/design-architect.md`

The Design Architect **consumes** the Requirements Specialist output and creates technical designs:

1. **Requirements Analysis** - Reads `specs/REQUIREMENTS.md` thoroughly
2. **Architecture Design** - Defines components, patterns, technology stack
3. **Technical Decisions** - Selects frameworks, coding standards, testing approach
4. **Traceability** - Maps each REQ-XXX to a design component
5. **Quality Gate** - Validates 100% requirements coverage before writing `specs/DESIGN.md`

**Key Output**: Traceability matrix showing requirement-to-component mapping.

---

## Task Planner Agent (For Comparison)

**File:** `.claude/agents/task-planner.md`

The Task Planner **chains from** the Design Architect output and creates implementation tasks:

1. **Document Analysis** - Reads both `REQUIREMENTS.md` and `DESIGN.md`
2. **Task Breakdown** - Groups by architectural layers, identifies dependencies
3. **Complexity Estimation** - Assigns S/M/L/XL estimates
4. **Priority Assignment** - P0/P1/P2 based on criticality
5. **Traceability** - Maps each task to requirements (REQ-XXX) and design components
6. **Quality Gate** - Validates requirements coverage, dependency DAG, no orphaned tasks

**Key Output**: Structured task breakdown with bidirectional traceability to requirements.

---

## Workflow Chain (pdoronila/cc-sdd)

```
User Input: "Build an e-commerce checkout system"
     ↓
Master Orchestrator (/cc-sdd/spec)
     ↓
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Phase 1: Requirements Specialist                         │
│  ├─ Analyze: payment, cart, orders, users                │
│  ├─ Generate EARS: Ubiquitous, Event-Driven, etc.        │
│  ├─ Validate: Quality gate (unique IDs, testability)     │
│  └─ Output: specs/REQUIREMENTS.md (REQ-001 through REQ-040)
│                                                            │
│  Phase 2: Design Architect                                │
│  ├─ Read: specs/REQUIREMENTS.md                           │
│  ├─ Create: Architecture, component design, tech stack   │
│  ├─ Validate: 100% requirements coverage                 │
│  └─ Output: specs/DESIGN.md (+ traceability matrix)      │
│                                                            │
│  Phase 3: Task Planner                                    │
│  ├─ Read: REQUIREMENTS.md + DESIGN.md                    │
│  ├─ Generate: Implementation tasks with dependencies      │
│  ├─ Validate: Requirements coverage, DAG integrity       │
│  └─ Output: specs/TASK.md (TASK-001 through TASK-030)    │
│                                                            │
└────────────────────────────────────────────────────────────┘
     ↓
.claude/PROJECT_STATE.md updated with status
     ↓
Result: Complete spec-driven foundation ready for implementation
```

---

## EARS Format Specification

**Source:** gotalab/cc-sdd (`settings/rules/ears-format.md`)

### Five Core Patterns

| Pattern | Syntax | Use Case | Example |
|---------|--------|----------|---------|
| **Ubiquitous** | `The [system] shall [response]` | Always-active fundamentals | `The mobile phone shall weigh < 100g` |
| **Event-Driven** | `When [event], the [system] shall [response]` | Specific triggers | `When user clicks checkout, the system shall validate cart` |
| **State-Driven** | `While [precondition], the [system] shall [response]` | Conditional on system state | `While payment processing, the system shall show spinner` |
| **Optional** | `Where [feature is included], the [system] shall [response]` | Feature-conditional | `Where 2FA enabled, the system shall require verification` |
| **Unwanted Behavior** | `If [trigger], then the [system] shall [response]` | Error handling | `If login fails, then the system shall return 401` |

### Combined Patterns
- `While [precondition], when [event], the [system] shall [response]`
- `When [event] and [additional condition], the [system] shall [response]`

### Subject Selection Guidelines
- **Software**: Use concrete service/module name (e.g., "Checkout Service", "Auth Module")
- **Process/Workflow**: Use responsible team/role (e.g., "Support Team")
- **Non-Software**: Use appropriate entity (e.g., "Marketing Campaign")

### Quality Criteria
- Testable, verifiable, single behavior
- Objective language: "shall" (mandatory), "should" (recommendation)
- Avoid ambiguous terms: should/could/might/possibly/perhaps

---

## Key Differentiators: CC-SDD vs Parallax PEARS

### Similarities
1. Both use structured requirement patterns (EARS vs PEARS)
2. Both enforce testability and single-behavior atomicity
3. Both use bidirectional traceability (requirements → design → tasks)
4. Both validate through quality gates before phase transitions
5. Both support iterative refinement

### Differences

| Aspect | CC-SDD (EARS) | Parallax (PEARS) |
|--------|--------------|-----------------|
| **Format** | 5 fixed EARS patterns (When/While/Where/If/Ubiquitous) | Probabilistic/deterministic distinction (assumption-oriented) |
| **Generation Mode** | Generator: creates reqs from descriptions | Evaluator: validates/reviews existing reqs |
| **Agent Role** | Requirements Specialist (generator) | PEARS integrator (reviewer/validator) |
| **Output Scope** | Complete REQUIREMENTS.md with all 5 pattern types | Gaps, assumptions, missing error cases (critique-focused) |
| **Validation Gate** | Pre-write quality checklist | Post-generation adversarial review |
| **Integration** | Pipeline: Requirements → Design → Tasks | Parallel: Review team + synthesizer filter |
| **Error Handling** | Explicit REQ-040 (Unwanted Behavior) section | Assumption tracking + error case gaps |
| **Determinism Focus** | Not explicitly tracked | Core to PEARS (probabilistic vs deterministic distinction) |

---

## What CC-SDD Requirements Specialist Does NOT Do

1. **Review or Validate** existing requirements (no validation agent at requirements phase)
2. **Track Assumptions** explicitly (PEARS adds assumption-oriented pattern)
3. **Distinguish Deterministic vs Probabilistic** behavior (not in EARS)
4. **Provide Gap Analysis** (separate agent in gotalab/cc-sdd: `validate-gap`)
5. **Perform Adversarial Review** of requirements
6. **Trace to Architecture Patterns** at requirements phase (only design phase does this)
7. **Multi-perspective Review** (single Requirements Specialist, no reviewer team)

---

## Quality Gate Checklist: Requirements Phase

**Before writing `specs/REQUIREMENTS.md`, agent validates:**

- ✓ All requirements have unique IDs (REQ-XXX format, numeric-only)
- ✓ Each requirement follows one of 5 EARS syntax patterns
- ✓ All requirements are testable (measurable outcomes, observable behavior)
- ✓ No ambiguous terms (no "should", "could", "might", "possibly", "perhaps")
- ✓ Every functional area is covered
- ✓ Error scenarios are defined (REQ-040 Unwanted Behavior section exists)
- ✓ Non-functional requirements (performance, security, scalability) are specified
- ✓ Subject in each requirement is consistently named (same service/system name throughout)

---

## Comparison: pdoronila/cc-sdd vs gotalab/cc-sdd

### pdoronila/cc-sdd (Simpler, Claude Code-Native)
- **Structure**: `.claude/agents/`, `.claude/commands/cc-sdd/`
- **Agents**: 3 (Requirements Specialist, Design Architect, Task Planner)
- **Workflow**: Linear (Requirements → Design → Tasks)
- **Metadata**: PROJECT_STATE.md + WORKFLOW_CONTEXT.md
- **Tool Constraints**: Limited to Read, Grep, Glob, Write, WebSearch per agent
- **Language Support**: Single language (English in examples)
- **Validation Loop**: Quality gates built into each agent
- **Deployment**: Copy `.claude/` directory to any Claude Code project

### gotalab/cc-sdd (Complex, Multi-Tool Ecosystem)
- **Structure**: `.kiro/` (Kiro framework), `tools/cc-sdd/templates/agents/`
- **Agents**: 5+ (spec-requirements, spec-design, spec-tasks, validate-gap, validate-design, validate-impl)
- **Workflow**: Linear + optional validation branches (Requirements → [Gap Analysis] → Design → [Validation] → Tasks)
- **Metadata**: `spec.json` with explicit phase tracking, approval gates, metadata
- **Tool Constraints**: Dynamic per agent (Bash, Glob, Grep, Edit, MultiEdit, Update, WebSearch, WebFetch)
- **Language Support**: Multi-language (spec.json.language field, EARS translations)
- **Validation Loop**: Separate validation agents (validate-gap, validate-design, validate-impl)
- **Deployment**: Kiro CLI tool that generates `.claude/` from templates
- **Steering Context**: Centralized `steering/` directory for project memory (structure.md, tech.md, product.md, custom files)

---

## Technical Takeaways for Parallax Integration

### 1. EARS is Proven & Standardized
- Industry-standard (Ericsson), not proprietary
- 5 clear patterns cover ~95% of software requirements
- cc-sdd's innovation is **agent orchestration**, not format invention

### 2. Quality Gates Work
- Pre-write validation prevents invalid requirements from being persisted
- pdoronila's checklist is practical and implementable
- gotalab's multi-phase validation (generate → validate-gap → validate-design → validate-impl) adds rigor

### 3. Generator vs Reviewer
- CC-SDD **generates** requirements from descriptions (one-way, forward)
- PEARS (presumably) **reviews/validates** requirements (backward, adversarial)
- **Complementary**, not redundant:
  - Use CC-SDD (or PEARS generator) to create initial requirements
  - Use PEARS (or adversarial agents) to validate and challenge them

### 4. Traceability is Essential
- Each requirement must flow through design → tasks
- gotalab's metadata.approvals tracking is cleaner than pdoronila's file-based status
- Both achieve bidirectional mapping (REQ-XXX ↔ Design Component ↔ Task-XXX)

### 5. Steering Context is a Key Differentiator
- gotalab's centralized `steering/` (structure.md, tech.md, product.md) provides **project memory**
- pdoronila relies on CLAUDE.md (less structured)
- PEARS could benefit from similar context architecture (captured assumptions, known patterns, risk profiles)

### 6. Multi-Language Support
- gotalab's language-aware EARS (English trigger keywords, localized variable parts) is elegant
- pdoronila assumes English throughout
- For team adoption, language flexibility matters

---

## Recommendations: How Parallax Could Integrate CC-SDD Patterns

### Option 1: Use CC-SDD's Requirements Specialist as Pre-Review Step
1. Run `/cc-sdd/requirements` or delegate to CC-SDD agent to generate initial EARS requirements
2. Feed output to PEARS evaluator agents (design reviewer, security reviewer, consistency checker)
3. Refinement loop: PEARS identifies gaps → Requirements Specialist updates → Re-review

### Option 2: Embed EARS Validation in PEARS Agents
- Add EARS pattern checking to parallax review agents
- Validate Requirements Specialist output against EARS checklist
- Report violations (e.g., "REQ-005 uses ambiguous term 'should'", "REQ-015 not testable")

### Option 3: Extend PEARS with Determinism Tracking
- CC-SDD's EARS doesn't explicitly track deterministic vs probabilistic behavior
- PEARS can add a 6th pattern: **Probabilistic Requirement**
  - Pattern: `The [system] may [response] with probability [P%]`
  - Example: `The cache may serve stale data (< 5 minutes old)`
- This fills a gap that pure EARS doesn't address

### Option 4: Create Parallax Steering Context (like gotalab)
- Centralize project assumptions, error budgets, patterns in `docs/analysis/` or `.claude/steering/`
- Reference during agent coordination
- Improves consistency across Requirements, Design, Review phases

---

## Conclusion

The Requirements Specialist agent in cc-sdd is a **requirements GENERATOR**, not a validator. It:

1. **Takes** feature descriptions as input
2. **Applies** EARS patterns systematically
3. **Validates** output through a pre-write quality gate
4. **Writes** directly to `specs/REQUIREMENTS.md`
5. **Feeds** output to Design Architect and Task Planner agents

The EARS format itself is not novel (Ericsson standard), but the **agent pipeline orchestration** (Requirements → Design → Tasks with bidirectional traceability) is well-designed.

For Parallax, the key insight is that **cc-sdd and PEARS operate at different layers**:
- **CC-SDD**: Generation + forward validation (requirements → artifacts)
- **PEARS**: Review + adversarial validation (requirements ← human/agent critique)

They are **complementary**, not competing. A mature system would use CC-SDD to generate requirements, then PEARS agents to challenge them from multiple angles (security, consistency, completeness, assumptions).

PEARS' advantage: multi-perspective review, assumption tracking, determinism distinction. CC-SDD's advantage: systematic generation, clear phase gates, proven EARS patterns.

**No need to replace PEARS format**. Instead, consider:
1. Generator: Use CC-SDD or similar to create initial EARS requirements
2. Validator: Use PEARS agents to review, identify gaps, challenge assumptions
3. Enrichment: Add determinism tracking, steering context, multi-language support from gotalab's approach
4. Integration: Link requirements IDs bidirectionally through design and task phases (already in parallax)

