---
name: illustrated-panels-over-emoji
description: User prefers GPT Image 2 illustrated panels over emoji/shape cartoon strips for consultant-grade PPTX decks
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9055eea3-6ef7-4501-b1af-5635c15c4b21
---

For consultant-grade presentation slides, use GPT Image 2 generated illustrations instead of emoji + python-pptx shape-based cartoon strips.

**Why:** User was presented with 4 options for problem/solution storytelling slides: (A) emoji cartoon strip with colored panels, (B) emoji cartoon strip with colored panels, (C) GPT Image 2 illustrated panels with white panels/dark borders, (D) GPT Image 2 illustrated panels. User confirmed Options C/D "look good" and chose to keep all for comparison but clearly prefers the illustrated versions for stakeholder-facing decks.

**How to apply:** When building explainer, problem-statement, or storytelling slides for executive/stakeholder decks, generate flat 2D corporate illustrations via GPT Image 2 ([[gpt-image-2-azure]]) rather than using emoji characters and shape-based speech bubbles. Keep panel borders dark/black with white backgrounds for a professional look — avoid colored panel borders/backgrounds. Internal content (titles, captions, accent colors) should still use semantic colors (red for problems, green for solutions).

Pattern confirmed again (2026-05-26) on MSIS 550 case competition: 6 illustrated panels embedded into Veritas Clean design. Approach: generate text-only Veritas version first (82 KB), then create illustrated variant that replaces/adds right-panel images on 6 key slides (3 MB). Both versions validated with identical content. User requested both versions proactively — offer dual versions when building decks. See [[MSIS 550 Case Competition]].

Pattern extended (2026-05-27) on <ORG> AI Office Hours: 3-version approach proven — V1 text-only Veritas (1.4 MB), V2 illustrated on 8 key slides (7.4 MB, 10 images), V3 fully illustrated every slide (13.2 MB, 17 images). User explicitly requested fully illustrated V3 as a third option. For important presentations, always offer 3 tiers: clean text, selective illustration, full illustration. See [[AI Office Hours]].
