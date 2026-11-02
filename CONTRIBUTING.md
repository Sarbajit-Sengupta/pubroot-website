# Contributing to Pubroot

Thank you for your interest in contributing to Pubroot! This guide explains how to submit papers, propose changes to the review pipeline, and run the project locally.

## Table of Contents

- [How to Submit a Paper](#how-to-submit-a-paper)
- [How to Submit a Priorroot Disclosure](#how-to-submit-a-priorroot-disclosure)
- [How to Propose Rubric or Review Pipeline Changes](#how-to-propose-rubric-or-review-pipeline-changes)
- [Local Development Setup](#local-development-setup)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Code of Conduct](#code-of-conduct)

---

## How to Submit a Paper

Pubroot accepts articles through a structured GitHub Issue form. The submission is automatically reviewed by a 6-stage AI pipeline.

### Submission Process

1. **Open the submission form**: [Submit Article](https://github.com/buildngrowsv/pubroot-website/issues/new?template=submission.yml)

2. **Fill out all required fields**:
   - **Article Title** — Clear and descriptive
   - **Category** — Select from the dropdown (format: `journal/topic`, e.g., `ai/llm-benchmarks`)
   - **Submission Type** — Choose from: `original-research`, `case-study`, `benchmark`, `review-survey`, `tutorial`, or `dataset`
   - **Abstract** — 50-300 words, self-contained summary
   - **Article Body** — 200+ words in Markdown (use `##` for sections, never `###` which is reserved for form fields)
   - **Supporting Repository URL** — Optional but strongly recommended (earns 🟢 **Verified Open** badge)
   - **Commit SHA** — Pin to a specific commit in your repo
   - **Repository Visibility** — `public`, `private`, or `no-repo`

3. **Submit** — The review pipeline starts automatically

### The 6-Stage Review Pipeline

Every submission passes through these stages sequentially:

| Stage | File | What It Does |
|-------|------|-------------|
| **1. Parse & Filter** | `_review_agent/stage_1_parse_and_filter.py` | Extract fields, validate format, check word counts, validate category against `journals.json` |
| **2. Novelty Check** | `_review_agent/stage_2_novelty_check.py` | Search arXiv and Semantic Scholar for related work, check internal index for supersession |
| **3. Repo Analysis** | `_review_agent/stage_3_read_linked_repo.py` | If a repo is linked, read file tree and key source files |
| **4. Build Prompt** | `_review_agent/stage_4_build_review_prompt.py` | Assemble complete review prompt with calibration examples, novelty context, and type-specific criteria |
| **5. AI Review** | `_review_agent/stage_5_gemini_grounded_review.py` | Send to Gemini via OpenRouter with web search grounding. Model scores and verifies claims |
| **6. Post & Decide** | `_review_agent/stage_6_post_review_and_decide.py` | Post review as GitHub comment. If accepted (≥6.0/10): create PR, auto-merge, update index. If rejected: close issue with feedback |

### Scoring Rubric

Articles are scored 0.0–10.0 across six dimensions (each 0.0–1.0):

- **Methodology** — Rigor of approach, experimental design
- **Factual Accuracy** — Claims verified via Google Search grounding
- **Novelty** — Contribution beyond existing work
- **Code Quality** — Repository structure, docs, tests, claim alignment
- **Writing Quality** — Clarity, structure, grammar
- **Reproducibility** — Steps documented, dependencies pinned, data available

**Acceptance threshold: 6.0/10.0**

### Review Time by Reputation

- **New Contributor**: ~24 hours
- **Established** (2+ accepted): ~6 hours
- **Trusted** (5+ accepted, avg > 7.0): ~1 hour
- **Authority** (10+ accepted, avg > 8.0): Minutes

### Handling Revisions

**If rejected**, open a **new submission issue** with your updated article:

1. Read the review comment on your closed issue
2. Revise your Markdown article and supporting repo
3. Open a [new submission](https://github.com/buildngrowsv/pubroot-website/issues/new?template=submission.yml)
4. Fill in all fields with your full updated content
5. The entire 6-stage review runs again

**Do not** reply to the old issue expecting a re-review — the automation only processes new issues.

**If already published**:
- **Small fixes** (typos, broken links): Open a PR editing `papers/{journal}/{topic}/{slug}/index.md`
- **Substantive changes** (new claims, results): Submit as a new article (may use `supersedes` field in review metadata)

### Figures and Images

The pipeline stores **Markdown text only** — it does not upload binary files from the issue.

- Embed images: `![description](https://...)` using **stable HTTPS URLs you control**
- **Recommended**: Commit images to your supporting repository and link via `raw.githubusercontent.com` or `?raw=1` URLs
- Also valid: self-hosted HTTPS, CDN, or object storage

See [Editorial Guidelines — Figures](https://pubroot.com/editorial-guidelines/#figures-hosting) for details.

---

## How to Submit a Priorroot Disclosure

**Priorroot** is Pubroot's defensive disclosure system for prior art. It publishes structured, enabling disclosures that create citable prior art under 35 U.S.C. § 102, anticipating method-of-use patents before they are filed.

### What is Priorroot?

Priorroot prevents known compounds, devices, and software methods from being fenced off by method-of-use patents. Every disclosure is:
- AI-reviewed for completeness and enabling detail
- Date-stamped when published
- Placed in the public domain under CC0
- Indexed separately in `priorroot-index.json`

### How to Submit

Priorroot uses the **same submission template** as regular Pubroot papers. The key difference is the **category** you select:

1. Go to [Submit Article](https://github.com/buildngrowsv/pubroot-website/issues/new?template=submission.yml)

2. In the **Category** dropdown, select a **Defensive Disclosures & Prior Art** topic:
   - `prior-art/therapeutic-use` — Known compounds for specific medical uses
   - `prior-art/device-method` — Device operation methods and configurations
   - `prior-art/software-method` — Software algorithms, architectures, and protocols
   - `prior-art/materials-process` — Materials synthesis and processing methods
   - `prior-art/general-disclosure` — Other enabling disclosures

3. Fill out the form as you would for any Pubroot submission:
   - **Submission Type**: Usually `original-research` or `case-study`
   - **Abstract**: What is being disclosed and why it's already known
   - **Article Body**: Enabling technical detail (enough for someone skilled in the art to reproduce)
   - **Supporting Repo**: Code, data, or documentation proving prior knowledge

4. Submit — The same 6-stage review runs, but:
   - Published disclosures go to `papers/prior-art/{topic}/{slug}/`
   - Indexed in `priorroot-index.json` (separate from general Pubroot index)
   - Featured on [pubroot.com/priorroot](https://pubroot.com/priorroot/)

### Review Criteria for Disclosures

Priorroot disclosures are judged on:
- **Enabling detail** (critical) — Can someone skilled in the art reproduce this?
- **Prior knowledge evidence** — Citations, dates, or documentation showing it was already known
- **Completeness** — All relevant parameters, conditions, and context documented

The acceptance threshold is the same (6.0/10), but the rubric weights differ from research papers.

### Future Development

As of November 2026, Priorroot submissions follow the standard pipeline. Planned enhancements include:
- Dedicated Priorroot submission form with prior-art-specific fields
- Automated prior art database cross-checks (USPTO, EPO, patent literature)
- Chemical structure and device diagram validation

For questions about Priorroot, open an issue in this repository or email the maintainers.

---

## How to Propose Rubric or Review Pipeline Changes

The review pipeline is modular and open to community improvements. Changes to scoring criteria, stage logic, or calibration examples are welcome.

### Where Things Live

- **Scoring rubric**: Defined in `_review_agent/stage_4_build_review_prompt.py` (type-specific criteria) and documented in [Editorial Guidelines](https://pubroot.com/editorial-guidelines/)
- **Review prompts**: `_review_agent/stage_4_build_review_prompt.py` and `_review_agent/stage_5_gemini_grounded_review.py`
- **Calibration examples**: `_calibration/gold-01-excellent.json`, `gold-02-average.json`, `gold-03-poor.json`
- **Category definitions**: `journals.json` (journal/topic taxonomy)
- **Workflows**: `.github/workflows/review.yml` and `publish.yml`

### Proposal Process

1. **Open a Discussion or Issue First**
   - Describe the problem: What's broken, unclear, or missing?
   - Propose your solution: What would you change and why?
   - Tag with `enhancement` or `review-pipeline`
   - Get feedback from maintainers before implementing

2. **If Approved, Open a Pull Request**
   - Create a branch: `git checkout -b your-feature-name`
   - Make your changes
   - **Write or update tests** (see [Running Tests](#running-tests) below)
   - Run the test suite: `python3 -m pytest _review_agent/` (from repo root)
   - Open a PR with a clear description linking to the original issue

3. **Code Review**
   - Maintainers will review your PR
   - Tests must pass (GitHub Actions runs them automatically)
   - Small, focused PRs are preferred over large rewrites

### Running Tests

Tests live in `_review_agent/test_*.py`. Run them locally before submitting a PR:

```bash
# From repository root
python3 -m pytest _review_agent/

# Run a specific test file
python3 -m pytest _review_agent/test_stage_1_parse_and_filter.py

# From _review_agent directory
cd _review_agent
python3 -m pytest
```

**Install test dependencies** (if pytest is not installed):

```bash
pip install pytest
pip install -r _review_agent/requirements.txt
```

Tests include:
- Stage-by-stage unit tests (`test_stage_*.py`)
- Integration tests (`test_end_to_end_integration.py`)
- Bug regression tests (`test_bug_b20_fixes.py`, `test_bug_b23_fixes.py`)
- Index consistency tests (`test_pubroot_site_paths.py`)

### What to Test

When making changes:
- **Changing stage logic**: Update corresponding `test_stage_N_*.py`
- **Changing index building**: Run `scripts/test_index_golden.py` and `scripts/validate_index_integrity.py`
- **Changing calibration**: Add test cases to `test_stage_5_gemini_grounded_review.py`
- **Adding a new journal/topic**: Update `journals.json` and test with stage 1 validation

---

## Local Development Setup

### Prerequisites

- **Python 3.12** (minimum 3.10)
- **Git**
- **Hugo Extended** (for site builds, optional)
- **API Keys** (for running the review pipeline):
  - `OPENROUTER_API_KEY` — Required for AI review (get from [openrouter.ai](https://openrouter.ai))
  - `GITHUB_TOKEN` — Required for GitHub API (create a [personal access token](https://github.com/settings/tokens))
  - `S2_API_KEY` — Optional, for Semantic Scholar higher rate limits

### Clone the Repository

```bash
git clone https://github.com/buildngrowsv/pubroot-website.git
cd pubroot-website
```

### Install Python Dependencies

```bash
pip install -r _review_agent/requirements.txt
```

This installs:
- `openai` (for OpenRouter API)
- `arxiv` (for arXiv search)
- `requests` (for GitHub and Semantic Scholar APIs)
- `PyYAML` (for config parsing)

### Running the Review Pipeline Locally

**Set environment variables**:

```bash
export OPENROUTER_API_KEY="your-key-here"
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPOSITORY="buildngrowsv/pubroot-website"
export S2_API_KEY="your-semantic-scholar-key"  # Optional
```

**Run the pipeline on an issue**:

```bash
cd _review_agent
python3 review_pipeline_main.py <issue_number>
```

Example:

```bash
python3 review_pipeline_main.py 42
```

This runs all 6 stages on issue #42 and posts the result.

**Run without API keys** (for testing parse/validate stages only):

You can test stages 1-4 without API keys:

```bash
# Stage 1: Parse an issue (no API calls)
python3 -c "from stage_1_parse_and_filter import parse_and_filter_submission; \
  print(parse_and_filter_submission(42))"
```

### Running Tests

```bash
# All tests from repository root
python3 -m pytest _review_agent/

# Specific test file
python3 -m pytest _review_agent/test_stage_1_parse_and_filter.py -v

# With coverage
python3 -m pytest _review_agent/ --cov=_review_agent --cov-report=html
```

**Install pytest** if needed:

```bash
pip install pytest pytest-cov
```

### Building the Hugo Site Locally

The static site is built with Hugo and deployed to GitHub Pages.

1. **Install Hugo Extended**:
   - macOS: `brew install hugo`
   - Linux: Download from [gohugo.io](https://gohugo.io/installation/)
   - Verify: `hugo version` (must be Extended edition)

2. **Build the site**:

   ```bash
   cd _site_theme
   hugo --minify --destination public
   ```

3. **Serve locally**:

   ```bash
   hugo server --buildDrafts
   ```

   Visit `http://localhost:1313`

### Running Pagefind (Client-Side Search)

Pagefind generates the client-side search index:

```bash
cd _site_theme
hugo --minify --destination public
npx pagefind --site public --output-subdir _pagefind
```

Then serve with a local HTTP server:

```bash
python3 -m http.server -d public 8000
```

### Linting and Code Style

**No automated linters are configured in CI** as of November 2026, but clean Python code is expected:

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to functions
- Keep functions focused and small
- Use type hints where helpful

To lint manually:

```bash
# Install linters
pip install flake8 black

# Check formatting
black --check _review_agent/

# Lint
flake8 _review_agent/ --max-line-length=120
```

---

## Pull Request Guidelines

### Before Opening a PR

1. **Create a branch** from `main`:
   ```bash
   git checkout -b your-feature-name
   ```

2. **Make focused changes**:
   - Small, single-purpose PRs are easier to review
   - Don't mix feature work with unrelated refactors

3. **Write or update tests**:
   - New features need test coverage
   - Bug fixes should include a regression test
   - Run `pytest _review_agent/` before committing

4. **Update documentation**:
   - If you change behavior, update relevant docs (README.md, this file, Editorial Guidelines)
   - Add comments explaining non-obvious code

5. **Test locally**:
   - Run the full test suite: `python3 -m pytest _review_agent/`
   - If you changed the site, build it with Hugo
   - Check that your changes don't break existing papers

### Opening the PR

1. **Push your branch**:
   ```bash
   git add .
   git commit -m "Clear description of what changed and why"
   git push -u origin your-feature-name
   ```

2. **Open a PR on GitHub**:
   - Use a clear title (e.g., "Fix stage 2 novelty check rate limiting")
   - Reference related issues (e.g., "Fixes #123")
   - Describe what you changed and why
   - Explain any non-obvious implementation choices
   - Note any breaking changes

3. **Wait for CI**:
   - GitHub Actions runs tests automatically
   - Fix any failures before requesting review

### PR Review Process

- Maintainers will review your code
- Address feedback by pushing new commits
- Once approved, a maintainer will merge
- Small fixes (typos, docs) may be merged quickly
- Larger changes may need discussion or testing

### After Merge

- Maintainers handle deployment (GitHub Pages auto-deploys on merge to `main`)
- Your contribution will appear in the site build within minutes
- Thank you for contributing!

---

## Code of Conduct

Pubroot does not currently have a formal Code of Conduct, but we expect all contributors to:

- Be respectful and constructive in discussions
- Focus on the work, not personal attacks
- Welcome newcomers and help them learn the codebase
- Assume good intent in others' contributions
- Follow GitHub's [Community Guidelines](https://docs.github.com/en/site-policy/github-terms/github-community-guidelines)

Violations can be reported to the repository maintainers.

---

## Questions?

- **For general questions**: Open a [Discussion](https://github.com/buildngrowsv/pubroot-website/discussions)
- **For bugs or feature requests**: Open an [Issue](https://github.com/buildngrowsv/pubroot-website/issues)
- **For sensitive matters**: Email the maintainers (listed in the repository)

Thank you for contributing to Pubroot! 🚀
