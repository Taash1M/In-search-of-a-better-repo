---
name: project-i485-expedite
description: "I-485 Expedite Request letter for Taashi — EB-2 AOS, <ORG> Corporation, court ruling cited, DOCX+PDF finalized"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08c5d4d2-4f9c-4e86-9f3a-c03eb1f00dad
---

## I-485 Expedite Request

Employment-based (EB-2) adjustment of status expedite request letter, dated June 6, 2026.

**Why:** Case pending ~18 months (filed Dec 2024), interview completed Sep 19, 2025 with no decision for 9+ months. Benefits Hold Policy froze adjudication for Zimbabwe nationals. Federal court vacated that policy on June 5, 2026.

**How to apply:** If the user revisits this letter or needs updates, all source data is in `<USER_HOME>/OneDrive\Taashi M\USCIS\` and the generated files are in the `Expedite Request\` subfolder.

### Key Case Details
- **A-Number**: A-209492662
- **I-485 Receipt**: IOE0929138841
- **I-765 Receipt**: IOE0929138842
- **I-140 Receipt**: LIN2390210527 (Approved)
- **H-1B Receipt**: IOE0928244029 (Valid 10/23/2024–10/10/2027)
- **Employment Category**: EB-2
- **Priority Date**: August 24, 2022
- **Employer**: <ORG> Corporation (<ORG_PARENT>), since April 2, 2018
- **Current Salary**: $176,784.70/year
- **Job Title**: Data and Analytics Lead (petitioned as Business Intelligence Functional Lead, SOC 15-2051)
- **Attorney**: Laura Bloniarz, Wolfsdorf Rosenthal LLP (I-485); Seyfarth Shaw LLP (H-1B)
- **Children**: Mwatipa Andrew Manyanga (DOB 08/08/2022, U.S. citizen), Hapson Manyanga (DOB 10/26/2025, U.S. citizen)
- **Marital Status**: Single (as of I-485 filing Nov 2024)

### Court Ruling Cited
- **Case**: *Dorcas International Institute of Rhode Island v. USCIS*, No. 1:26-cv-00132 (D.R.I.)
- **Judge**: Chief Judge John J. McConnell, Jr.
- **Date**: June 5, 2026
- **Ruling**: Nationwide vacatur of 4 USCIS policies (Benefits Hold, Global Asylum Hold, Comprehensive Re-Review, Country-Specific Factors) under APA
- **135-page memorandum and order** — PDF downloaded as Exhibit D

### Deliverables (in `Expedite Request\`)
- `I-485_Expedite_Request_Taashi_Manyanga_2026-06-06.docx` — final letter
- `I-485_Expedite_Request_Taashi_Manyanga_2026-06-06.pdf` — final letter
- `Expedite_Request_Cover_Email.docx` — brief cover email for online portal submission
- `Exhibit_D_Dorcas_International_v_USCIS_Court_Order.pdf` — 135-page court order
- `generate_expedite_letter.py` — letter generation script (python-docx + docx2pdf)
- `generate_cover_email.py` — cover email generation script

### Letter Structure
1. **Opening** — cites USCIS Policy Manual Vol 1, Part A, Ch 5; references court ruling
2. **Section 1: Severe Financial Loss** — <ORG> Corporation, $176K salary, travel restrictions, Benefits Hold vacatur, appellate hedge
3. **Section 2: Family Hardship** — two U.S.-citizen children (Mwatipa age 3, Hapson age 7 months), sole provider
4. **Section 3: Case Readiness** — I-140 approved, biometrics done, interview done, priority date current, no RFE/NOID
5. **Enclosures** — 6 labeled exhibits (A–F)

### Key Decisions
- Invoked only ONE formal criterion (severe financial loss) — per USCIS review, focused > scattered
- Removed AC21/job portability mention (Supplement J confirms still with <ORG>, not porting)
- Removed "spouse" (marital status is single)
- Removed "humanitarian" as formal criterion — family hardship presented as supporting context instead
- Repositioned "biometrics completed" from standalone ground to supporting case readiness context
- Added appellate hedge: "regardless of any future appellate proceedings, the facts independently satisfy the criteria"
- Humanization pass applied — personal voice ("the urgency I feel as a father"), varied sentence structure, no AI-sounding patterns

### Filing Recommendations
- Triple-channel: USCIS Contact Center Tier 2 (1-800-375-5283) + USPS Certified Mail + e-Request on myUSCIS
- Consider having Wolfsdorf Rosenthal file on user's behalf for added weight
- Cover email created for electronic portal submission — brief, lists all identifiers and exhibits, "primary provider" (consistent with main letter)

### Status (2026-06-07)
- Letter and cover email finalized, ready to submit
- Exhibit D (court order PDF) downloaded and verified (135 pages)
- Remaining exhibits (A, B, C, E, F) to be attached by user from personal files
