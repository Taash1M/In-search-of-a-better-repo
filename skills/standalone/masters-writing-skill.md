---
name: masters-deliverable
description: Produce submission-ready Master's-level case deliverables — write-up (.docx), presentation (.pptx), or both — scored to maximize rubric points. Use when given assignment instructions, a rubric, or case materials for any graded academic deliverable.
version: 2.1.0 (enhanced)
---

# Master's Deliverable Skill — Write-Up + Presentation

Produces submission-ready academic deliverables: a written analysis (.docx), a presentation (.pptx), or both — for any Master's-level case assignment. Designed to maximize rubric points by enforcing the patterns that move work from B+ to A/A+.

**This skill is portable.** It contains no user-specific paths, no embedded credentials, no hard-coded folders. Drop the SKILL.md anywhere and it works.

---

## When This Skill Activates

- User provides assignment instructions, a case, a rubric, or structural guide
- User says "write up", "case analysis", "presentation", "case write-up", "deck for", "slides for"
- User asks for help with a graded academic deliverable
- User shares case materials and asks for a formatted answer

---

## Step 0: Pick the Deliverable Mode

Before doing anything else, confirm which mode applies:

| Mode | Output | Use When |
|---|---|---|
| **A. Write-up only** | `.docx` | Assignment requires a written case analysis, memo, or paper |
| **B. Presentation only** | `.pptx` | Assignment requires slides only (case presentation, pitch) |
| **C. Both** | `.docx` + `.pptx` | Assignment requires both (common in MBA/MSIS — written brief + class presentation) |

If the user hasn't said, ask. If the assignment folder contains BOTH a "Write-Up Student Instructions" and a "Presentation Rubrics" document, default to **Mode C** and confirm.

---

## Workflow (8 Steps — Execute in Order)

### Step 1: Review Available Material

Read every artifact in the assignment folder. Extract and confirm:

| Artifact | What to Extract |
|---|---|
| **Instructions / Prompt** | Exact questions or dimensions to address. Role you are writing as. Audience you are writing to. Deliverable type (memo, analysis, essay, deck, pitch). |
| **Rubric** | Every scoring dimension, point weight, what "full marks" requires per dimension. **If both write-up and presentation rubrics exist, extract both** and treat them as separate evaluation tracks. |
| **Structural Guide** | Required sections, page limits (body vs. exhibits), slide count limits, formatting rules (font, size, spacing, margins), exhibit/visual expectations. |
| **Case Material** | PDF, docx, or reading — extract every key data point: financials, percentages, quotes, stakeholder names, dates, competitive data, market sizing. |
| **Course Frameworks** | Syllabus, slides, prior class readings — list every analytical framework the course has introduced (these are the "right" frameworks to apply). |

**Data Extraction Standard**: Build a fact sheet from the case with every quantitative data point. These numbers are the ammunition for the deliverable. No claim in the final document should lack a supporting data point from the case.

**External Research Standard** (when assignment permits): If the assignment says "you may use external data/research," conduct web research before planning. Gather: industry market sizing, competitor benchmarks, academic citations for named frameworks, technology adoption data, and company financial reports. Every external data point needs a full citation (Author, Year, Title, Source). External research strengthens the analysis but must complement, not replace, case evidence.

Present a summary of what was found to the user before proceeding.

### Step 2: Ask Clarifying Questions

Surface ambiguities before planning:

- Which mode (A/B/C) — write-up, presentation, or both?
- Specific frameworks from the course to apply? (Check if the assignment or rubric names one.)
- Format preference beyond the guide? (memo vs. essay vs. report; slides with speaker notes vs. without)
- Class discussions, slides, or readings that should inform the analysis?
- Specific position the user wants to take, or should the analysis determine it?
- Verbal guidance from the professor that overrides written instructions?
- For Mode B/C: target slide count, presentation duration, audience (class, executive, panel)?

**Do not skip this step.** Wait for the user to respond. If they say "no questions, proceed," continue.

### Step 3: Create a Plan

Present a plan that confirms understanding and shows how every rubric dimension earns full marks. The plan must include:

1. **Mode confirmation** (A / B / C) and what files will be produced.
2. **Assignment Requirements Summary** — restate what's asked. List every dimension/question.
3. **Rubric Alignment** — map each rubric dimension to specific sections of the deliverable. For Mode C, do this for both rubrics. Show how each dimension earns full marks.
4. **Analytical Framework** — name the framework(s) and why they fit. Use a course-named framework if the assignment specifies one.
5. **Alternatives** — 2-3 mutually exclusive alternatives with a one-line thesis each.
6. **Recommendation Preview** — the recommended alternative and core reasoning.
7. **Exhibit / Visual Plan** — list planned exhibits (write-up) and visuals (slides) with what analytical value each adds. Exhibits and visuals must synthesize, not just repeat case data.
8. **Page / Slide Budget** — how content is allocated, respecting strict limits.
9. **Data Points** — key quantitative facts that will anchor the analysis.

**Wait for user approval before drafting.**

### Step 4: Create First Draft (V1)

Generate the deliverable(s) as Python scripts and execute them.

#### 4.1 Mode A or C — Write-Up V1

Use `python-docx`. The 8 quality rules below lifted prior write-ups from B+ to A/A+. Apply every one.

**The 8 Rules**

| # | Rule | What It Means |
|---|---|---|
| 1 | **Lead with the answer** | State the recommendation in the first paragraph. Reader knows your position before reading the analysis. |
| 2 | **Anchor every claim in data** | Every assertion needs a number, percentage, dollar figure, or specific case fact. No unsupported generalizations. |
| 3 | **Rank framework dimensions** | Don't list — rank by impact or urgency. Show which matters most and why. |
| 4 | **Steel-man before you kill** | Present the strongest version of each alternative before explaining why it falls short. |
| 5 | **Quantify everything** | Recommendations need specific KPI targets ("increase from 4% to 8%"), not vague "improve". |
| 6 | **Who does what** | Every recommendation needs an owner, a timeline, and a resource/cost estimate. |
| 7 | **Pin-cite exhibits** | Reference specific exhibits ("see Exhibit 2, Panel B"). Every exhibit referenced at least once. |
| 8 | **Create urgency** | Show what happens if the company doesn't act — competitive erosion, cost escalation, share loss. |

**Default Formatting (academic preset — override per assignment instructions)**

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.line_spacing = 2.0
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.space_before = Pt(0)

for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Headings: same font as body, bold, black, no color
# Body paragraphs: 0.5 inch first-line indent
# Exhibits: Table Grid style, 9pt, bold headers, 8pt italic source notes
```

**Default Document Structure** (override per the assignment's structural guide)

1. **Header** — Memo (TO/FROM/RE) if assignment uses "memo" or names an audience; otherwise student name + course + assignment title.
2. **Executive Summary & Problem Definition** (~0.5 pages) — Root cause (not symptoms), recommendation preview.
3. **Analysis & Evaluation of Alternatives** (~1–1.5 pages) — Framework application, 2-3 alternatives with quantified pros/cons.
4. **Recommendation & Action Plan** (~1–1.5 pages) — Clear recommendation, phased implementation, risk mitigation, governance.
5. **Exhibits** (separate pages) — Tables and frameworks with analytical value, labeled with source notes.

**Page Budget Enforcement**: ~250 words/page (double-spaced 12pt TNR). Verify body fits the page limit. If over, tighten prose and move data-heavy content to exhibits. If under, expand any rubric dimension that's underserved.

#### 4.2 Mode B or C — Presentation V1

Use `python-pptx`. Slides must do their own job — they are not a printout of the write-up.

**The 6 Presentation Rules**

| # | Rule | What It Means |
|---|---|---|
| 1 | **One idea per slide** | A slide carries a single argument or data point. The headline IS the argument, not the topic. |
| 2 | **Headline-as-takeaway** | Slide titles state the conclusion ("Three alternatives, but only Option B clears the cost gate"), not the topic ("Alternatives"). |
| 3 | **Visual primacy** | Every slide has a chart, framework diagram, table, or image — not a wall of bullets. If you can't visualize it, the slide isn't earned. |
| 4 | **Speaker notes carry the proof** | Body of the slide shows the takeaway. Speaker notes carry the data citations and supporting argument. The reader of the deck and the listener get the same content from different angles. |
| 5 | **Closer is the strongest** | Last content slide = the recommendation with KPI targets, owners, timeline. Then a single Q&A / thank-you slide. |
| 6 | **Consistent visual system** | Same font family across all slides. Limited palette (2-3 brand colors + neutrals). Consistent title position. Page numbers on content slides. |

**Default Slide Order** (10–14 slides typical for case presentations)

1. **Title** — case name, your name, course, date
2. **Recommendation up front** — 1 sentence: "We recommend X because Y, with KPI Z" (yes, the recommendation goes second, not last)
3. **Problem & stakes** — what's at risk if no action
4. **Case context** — 1 slide of essential background (don't recap the case)
5. **Framework** — the analytical lens, with a diagram
6. **Alternatives** — 1 slide each (2-3 slides), each with steel-manned pros + decisive cons
7. **Evaluation matrix** — alternatives × criteria, scored
8. **Recommendation, expanded** — same recommendation as slide 2, now with detail
9. **Action plan** — phased timeline, owners, KPIs
10. **Risks & mitigations** — top 3 risks, what we'll do
11. **Financial / impact summary** — quantified outcome
12. **Q&A** — single slide, "Questions?" + your name

**Default Formatting**

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9 widescreen
prs.slide_height = Inches(7.5)

# Default fonts:
TITLE_FONT = 'Calibri'   # or 'Calibri Light'
TITLE_SIZE = Pt(28)
BODY_FONT = 'Calibri'
BODY_SIZE = Pt(18)        # min — never go below 16pt for body content
NOTE_SIZE = Pt(10)        # exhibit/source notes only

# Palette: choose 2-3 colors + 1 neutral. Stay consistent.
PRIMARY   = RGBColor(0x0B, 0x3D, 0x91)   # deep blue
ACCENT    = RGBColor(0xE8, 0x6E, 0x1A)   # warm orange
NEUTRAL   = RGBColor(0x44, 0x44, 0x44)   # near-black for body text
LIGHT_BG  = RGBColor(0xF5, 0xF5, 0xF5)
```

**Speaker Notes Discipline**: every content slide has speaker notes. Notes are 60-120 words. They state: (a) the data anchor for the slide's claim, (b) the transition into the next slide. Without speaker notes, the rubric's "depth of analysis" dimension gets the floor score.

**Visual Variety**: across the deck, vary the visual element type — bar chart, framework diagram, evaluation matrix table, timeline, quadrant, photo. A deck of 10 bar-chart slides scores worse than a deck of 10 varied visuals.

**Team Presentation Allocation**: For team presentations with N members, allocate slides so each member presents 2 content slides. Slide 1 (title) and the final slide (Q&A) are shared. Assign slides by logical ownership — e.g., Member 1: Problem & Stakes + Case Context, Member 2: Framework + JTBD Analysis, etc. Include a slide allocation table in the speaker notes of the title slide so the team knows who presents what.

#### 4.3 Mode C — Both

Generate the write-up V1 first, then build the presentation V1 from it. The presentation is **not** a copy-paste from the write-up — it is a re-expression of the same argument for a listening audience. Specifically:

- Deck headlines = takeaways from each section of the write-up
- Deck visuals = the write-up's exhibits, redrawn as slides
- Deck speaker notes = the body prose of the write-up, condensed
- Deck recommendation slide = the write-up's recommendation, with the same KPI targets

The argument must be **identical** across both formats. If a reviewer reads the write-up and watches the presentation, they should hear the same recommendation, the same framework, the same alternatives, the same numbers.

### Step 5: PhD Reviewer Pass

Assume the persona of a PhD-level grader. Score V1 against every rubric dimension using this template (one block per dimension):

```
### [Dimension Name] — X/Y points
What's there: [what the draft does well]
Gap: [specific deficiency, with quote from draft if applicable]
Fix: [concrete action — not "improve" but exactly what to change]
```

Sum to total, assign letter grade:
- 90%+ = A (full marks territory)
- 80-89% = B+ (good, gaps remain)
- 70-79% = B (competent, multiple gaps)
- <70% = needs major rework

**Common gap checks** (Mode A/C — write-up):
- [ ] Addresses every dimension/question?
- [ ] Course frameworks explicitly named (not implicitly used)?
- [ ] Every alternative substantively developed (no thin strawmen)?
- [ ] Recommendation has a concrete timeline with phases?
- [ ] Risks identified with specific mitigations?
- [ ] Format matches the required type (memo / essay / report)?
- [ ] Page count within limits?
- [ ] All exhibits referenced in body?
- [ ] Both sides argued before dismissal?

**Common gap checks** (Mode B/C — presentation):
- [ ] Every slide title is a takeaway (not a topic)?
- [ ] Recommendation slide front and back?
- [ ] Each slide has a visual element (no walls of bullets)?
- [ ] Speaker notes present, 60-120 words, data-anchored?
- [ ] Slide count within budget?
- [ ] Visual variety across the deck?
- [ ] Consistent font / palette / title placement?
- [ ] Evaluation matrix shows the trade-offs honestly?

### Step 6: Rewrite (V2 Final)

Address every gap from Step 5. Generate `generate_v2.py` (write-up) and `generate_deck_v2.py` (presentation) and execute them.

#### 6a. Humanify (Bake In, Don't Post-Process)

Apply these rules during V2 generation — do not write AI-flavored prose first and clean it up later.

**Banned vocabulary** (Tier 1 AI tells):
- delve, leverage, robust, comprehensive, seamless, utilize, holistic, paradigm, navigate (the X), realm, landscape, tapestry, ever-evolving, cutting-edge, state-of-the-art, transformative, pivotal, watershed, game-changer

**Banned transitions**:
- Moreover, Furthermore, Additionally, In conclusion, Notably (overuse), It is worth noting, In essence

**Banned patterns**:
- No em dashes — use commas or periods
- No synonym cycling within a paragraph
- No hollow intensifiers (truly, genuinely, quite frankly, profoundly)
- No "serves as" or "features" — use "is" and "has"
- No formulaic openers ("In today's fast-paced world…")
- No three-item lists where two would do (the rule of three is overused)

**Sentence rhythm**:
- Vary length deliberately. Mix short (4-8 words) and long (20-30 words) sentences in the same paragraph.
- Don't start consecutive sentences the same way.
- Don't put a comma where a period works.

**Stance**:
- Direct statements over hedged ones. "We recommend X" not "It might be worth considering X."
- Position before nuance. State the call, then the caveats — not the reverse.

#### 6b. Validate All Numbers

Before generating the final document(s), verify every quantitative claim:

- Cross-reference all numbers, percentages, dollar figures, and calculations against the source case.
- For derived numbers ("cost per lead drops from $50 to $25"), show the math or verify the logic.
- For projections ("conversion from 4% to 8%"), state the basis ("based on 6x lead multiplier from bot test").
- Flag any number that cannot be traced to a specific case exhibit, paragraph, or data point.
- Verify totals in exhibits add up. Verify body-text percentages match exhibit values.
- Verify the **deck and write-up agree** on every number (Mode C).

If a number cannot be validated: cite the source explicitly, reframe as an estimate with stated assumptions, or remove it.

### Step 7: Cross-Format Coherence Check (Mode C only)

For both-deliverable mode, run these checks before submission:

- [ ] Same recommendation, identical wording in the executive summary of the write-up and slide 2 of the deck
- [ ] Same KPI targets in the action plan section and the action-plan slide
- [ ] Same framework named in both
- [ ] Same alternatives in the same order
- [ ] Same exhibits → slides mapping (every exhibit visualized once in the deck)
- [ ] Speaker notes condense, never contradict, the write-up

### Step 8: Submit Final

Deliver:

1. **Final files**: `.docx` (Mode A/C), `.pptx` (Mode B/C)
2. **Page / slide count verification** — confirm body pages and exhibit pages, or slide count and speaker-notes coverage, are within limits
3. **Final rubric score** — quick re-score of V2 against each rubric dimension (both rubrics for Mode C)
4. **Submission checklist** — file naming convention if specified, supplementary materials if required

---

## Analytical Framework Quick Reference

Use the framework that fits the assignment. If the assignment names one, use that. If not, select based on the strategic question:

| Framework | When to Use | Key Dimensions |
|---|---|---|
| **JTBD (Jobs to Be Done)** | Customer-centric innovation decisions | Functional, Emotional, Social job layers; rank by unmet demand |
| **Porter's 5 Forces** | Industry attractiveness / competitive pressure | Rivalry, Buyers, Suppliers, Substitutes, New Entrants |
| **SWOT** | Internal vs. external factor mapping | Strengths, Weaknesses, Opportunities, Threats |
| **BCG Matrix** | Portfolio strategy | Market growth vs. relative share |
| **Blue Ocean (ERRC)** | Creating new market space | Eliminate, Reduce, Raise, Create |
| **Technology S-Curve** | Timing of technology adoption / disruption | Performance vs. effort; inflection points |
| **Real Options** | Decisions under uncertainty with staged investment | Option value, exercise triggers, abandonment gates |
| **CRM Lifecycle** | Customer journey / funnel optimization | Awareness, Acquisition, Conversion, Retention, Advocacy |
| **Cost-Benefit Analysis** | Comparing financial trade-offs | Quantified costs vs. benefits per option |
| **TAM/SAM/SOM** | Market sizing | Total, Serviceable, Obtainable market |
| **NIST CSF** | Cybersecurity / risk governance cases | Identify, Protect, Detect, Respond, Recover |
| **Stakeholder Capitalism** | Ethics / responsibility cases | Customers, employees, shareholders, society — balanced |

---

## Citation Standard (APA 7th)

All deliverables use APA 7th edition for citations:

**In-text**: (Author, Year) or Author (Year). For 3+ authors: (First Author et al., Year).
**Tables/Figures**: "Source: Author (Year)" in italic 8pt below the exhibit.
**References page**: Full reference list at end of DOCX, alphabetical by author surname.

```
Journal:  Author, A. B. (Year). Title of article. Journal Name, Volume(Issue), Pages. https://doi.org/xxx
Book:     Author, A. B. (Year). Title of book (Edition). Publisher.
Web:      Author/Org. (Year). Title. Site Name. https://url
Report:   Organization. (Year). Title (Report No. XX). https://url
```

For slides: cite sources in speaker notes with abbreviated "(Author, Year)" and include a References slide at the end or source notes on each visual.

---

## JTBD Deep-Dive Template

When the assignment names JTBD, go beyond listing jobs. Use this structured analysis:

**1. Job Statement** (verb + object + context): "Help me [verb] my [object] when [context]"
- Functional: What the customer needs to get done physically
- Emotional: How they want to feel during/after
- Social: How they want to be perceived by others

**2. Current Hiring/Firing**: What solution does the customer currently "hire"? What are they "firing"?

**3. Outcome Metrics** (Ulwick's ODI framework):
- Effectiveness: Does it get the job done completely?
- Speed: How fast?
- Error reduction: How reliable?
- Perceived value: Worth the cost/effort?

**4. Over-served vs. Under-served**: Which jobs are already well-served (diminishing returns from innovation) vs. poorly served (high opportunity)?

**5. Competitive Hiring**: What non-obvious competitors get "hired" for the same job? (The milkshake competes with bananas, not other milkshakes.)

---

## Format Presets

Auto-detect from instructions, or use `academic` as default for write-ups and `professional-deck` as default for presentations.

**Write-up presets**

| Preset | Font | Size | Spacing | Margins | Use |
|---|---|---|---|---|---|
| `academic` | Times New Roman | 12pt | Double | 1" | Course assignments (default) |
| `professional` | Calibri | 11pt | 1.15 | 1" | Work memos, strategy docs |
| `executive` | Calibri | 11pt | 1.0 | 0.75" | C-suite briefs, one-pagers |

**Presentation presets**

| Preset | Title Font | Body Font | Aspect | Use |
|---|---|---|---|---|
| `professional-deck` | Calibri 28pt | Calibri 18pt | 16:9 | Default — class presentations, case decks |
| `executive-deck` | Calibri 32pt | Calibri 20pt | 16:9 | Senior-audience pitches, board presentations |
| `academic-poster` | Calibri 24pt | Calibri 14pt | 4:3 | Single-page summary visuals |

---

## Common Pitfalls to Avoid

**Write-up**
1. Summarizing the case — the professor has read it. Analyze, don't recap.
2. Thin alternatives — every alternative needs equal analytical depth.
3. Implicit frameworks — name the framework explicitly.
4. Vague recommendations — "improve the chatbot" earns zero. "Deploy chatbots at ToFu targeting 8% conversion by month 3" earns full marks.
5. Missing exhibit references — uncited exhibits are dead weight.
6. Over-length body — page limits are strict; 10-point deductions are common.
7. AI-sounding prose — bake humanify in.
8. Unverified numbers — one bad stat undermines the whole paper.

**Presentation**
9. Topic titles — "Alternatives" is a topic, "Three alternatives, but only Option B clears the cost gate" is a takeaway.
10. Wall-of-bullets slides — no visual = a worse slide than no slide.
11. Same recommendation twice without expansion — slide 2 (preview) and the late recommendation slide must both exist, but the late one carries detail.
12. Speaker notes empty or boilerplate — graders read them.
13. Reading the slide aloud — the deck and the speaker notes are different content, not the same.
14. 30-slide decks — strict limits matter; aim 10-14.

---

## Dependencies

- `python-docx` (`pip install python-docx`) — write-up generation
- `python-pptx` (`pip install python-pptx`) — presentation generation
- `pdfplumber` (`pip install pdfplumber`) — reading case PDFs
- Python 3.10+ recommended

For chart generation in slides, `matplotlib` (`pip install matplotlib`) is useful — render the chart to PNG, then insert as an image into the slide.

---

## Quick Start (Copy-Paste)

When the user shares an assignment folder:

```
1. Read every file in the folder. Build the fact sheet.
2. Confirm Mode (A / B / C). If both rubrics exist, default to C.
3. Run the 7-question clarifier (Step 2). Wait for answers.
4. Present the plan (Step 3). Wait for approval.
5. Generate V1 (Step 4). Use python-docx and/or python-pptx.
6. PhD reviewer pass (Step 5). Score every rubric dimension.
7. Rewrite V2 (Step 6) — humanify baked in, every number validated.
8. Cross-format coherence (Step 7) — Mode C only.
9. Deliver final files + re-scored rubric (Step 8).
```

---

## Why This Skill Exists

Master's-level case grading rewards three things: clear position, quantitative discipline, and rubric-completeness. This skill enforces all three by structure. The 8 write-up rules and 6 presentation rules are not preferences — they are the patterns that consistently move a deliverable from B+ to A/A+. The PhD reviewer pass is the difference between submitting a draft and submitting a graded paper.

The shareable design (no embedded paths, no skill dependencies, self-contained humanify rules) means this skill can be used by any student in any program with any assignment. Drop the SKILL.md into a Claude project, point Claude at the assignment folder, and follow the eight steps.
