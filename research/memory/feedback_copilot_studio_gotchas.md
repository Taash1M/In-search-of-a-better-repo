---
name: feedback-copilot-studio-gotchas
description: "Copilot Studio gotchas — Power Fx unsupported functions, auth/channel blocking, accessControlPolicy valid values, push/pull sequencing"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d84d7827-0050-4797-95b8-9b273946000e
---

## Power Fx in Copilot Studio Conditions

`contains()` and `toLower()` are UNSUPPORTED in Copilot Studio Power Fx conditions. Use exact string equality with `||` operator instead.

**Why:** Copilot Studio uses a restricted subset of Power Fx. These functions exist in full Power Fx (Power Apps/Automate) but are not available in topic condition expressions. The LSP validator catches them as `PowerFxError`.

**How to apply:** When writing ConditionGroup conditions in topic YAML:
- BAD: `=contains(toLower(Topic.X), "score")`
- GOOD: `=Topic.X = "Score" || Topic.X = "score"`
- List both upper and lower case variants explicitly
- Keep condition strings short — match the exact options shown in the Question prompt

## Demo Website Channel Requires No Auth

The Demo Website channel is BLOCKED when `authenticationMode: Integrated`. Must set to `None`.

**Why:** With Microsoft authentication enabled, Copilot Studio only allows Teams, M365, and SharePoint channels. The demo website has no OAuth redirect infrastructure, so it can't complete the auth flow — it shows "This channel is turned off because of authentication settings" + a JavaScript error.

**How to apply:** For testing via demo website:
```yaml
accessControlPolicy: Any
authenticationMode: None
authenticationTrigger: AsNeeded
```
For production via Teams: switch back to `Integrated` + `GroupMembership`.

## accessControlPolicy Valid Values

`AnyUser` is NOT a valid enum value and causes validation errors. Valid values: `Any`, `ChatbotReaders`, `GroupMembership`, `AnyMultiTenant`.

**Why:** The Copilot Studio schema uses `Any` (not `AnyUser`) for unrestricted access. Using an invalid value causes the agent to fail silently — the test site shows auth errors and JavaScript errors with no clear root cause.

**How to apply:** Always use one of the 4 valid values. For open testing use `Any`. For org-restricted use `GroupMembership`.

## Push After UI Changes

After making changes in the Copilot Studio browser UI, always pull before pushing from Claude Code.

**Why:** The UI modifies row versions and may add fields (voice settings, speech settings, etc.). Pushing without pulling causes `ConcurrencyVersionMismatch`. The pull also picks up any renames (e.g., `displayName` changed in UI).

**How to apply:** If push fails with version mismatch, run pull first, then push again. The manage-agent skill handles this automatically when it encounters the error.

## Custom Canvas: Use Direct Line Secret, Not Token Endpoint

For custom HTML canvas (Bot Framework Web Chat SDK), use the Direct Line secret instead of the Token Endpoint URL.

**Why:** The Token Endpoint URL is buried in Copilot Studio UI (Settings > Channels > Mobile app or Email) and hard to find. The regional URL format (`default{guid}.{region}.environment.api.powerplatform.com`) is not guessable — tried 15 region codes, all DNS failures. The Direct Line secret (Settings > Security > Web channel security > Secret 1) is easier to find and works with the standard endpoint.

**How to apply:** In the custom HTML:
```javascript
const resp = await fetch('https://directline.botframework.com/v3/directline/tokens/generate', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + DIRECT_LINE_SECRET }
});
const { token } = await resp.json();
// Use token with WebChat.createDirectLine({ domain: DIRECTLINE_URL, token })
```

## Custom Canvas: bubbleMessageMaxWidth Is Ignored for Tables

The `bubbleMessageMaxWidth` styleOption does NOT control table rendering width in Web Chat SDK. Tables overflow their bubble regardless of the setting.

**Why:** The Web Chat SDK applies `bubbleMessageMaxWidth` to the outer bubble container, but markdown-rendered tables inside use their own layout. The internal CSS classes (`[class*="bubble"]`, `[class*="content"]`, `[class*="stackedLayout"]`) have their own max-width that overrides the styleOption.

**How to apply:** Must add direct CSS `!important` overrides:
```css
#webchat [class*="bubble"] { max-width: 100% !important; }
#webchat [class*="bubble__content"] { max-width: 100% !important; }
#webchat [class*="stackedLayout"] { max-width: 100% !important; }
#webchat [class*="row"] { max-width: 100% !important; }
#webchat [class*="markdown"] { overflow-x: auto !important; max-width: 100% !important; }
```
Also style table headers with `white-space: nowrap` and short columns (# / Score / Weight) with `text-align: center`.

## Sonnet Ignores Scoring Constraints Unless Reinforced at Topic Level

System-level instructions saying "only use 10, 5, or 1" are insufficient. The Sonnet model in Copilot Studio will use intermediate values (8, 9, etc.) unless the constraint is also repeated in the `AnswerQuestionWithAI` topic prompt.

**Why:** Discovered during v3 testing (2026-06-04). First test: C2=8, C4=9 despite agent.mcs.yml saying "only 10, 5, or 1." After adding `CRITICAL SCORING RULE: Every criterion score MUST be exactly 10, 5, or 1` to the ScoreAccount research prompt, second test: all scores correct.

**How to apply:** For any strict-value constraint (discrete scores, specific formats, mandatory fields), put the rule in BOTH:
1. `agent.mcs.yml` system instructions (global)
2. The specific `AnswerQuestionWithAI` node's `userInput` prompt (local)

Related: [[project-copilot-studio-agents]], [[project-growth-kaizen]]
