---
name: confidence-check
description: Trigger whenever the user's message contains "/confidence" (anywhere in the message, typically at the end). Runs an interactive, iterative clarifying-questions loop until Claude reaches 95% confidence it understands the user's request, then states the confidence level and a short summary before proceeding. Always use this skill instead of ad hoc clarifying questions when "/confidence" appears — do not just ask one round of questions and move on.
---

# Confidence Check

## What this does

When the user types `/confidence` (anywhere in their message, usually tacked onto the end), don't just answer the request. Instead, run an iterative confidence-calibration loop: estimate how well you understand what they want, state that estimate as a percentage, and if it's below 95%, ask clarifying questions using the interactive multiple-choice tool. Repeat in rounds — re-estimating confidence after each round — until you hit 95%, then state that you've hit it, give a short summary of your understanding, and proceed with the task automatically.

## Trigger

Any message containing `/confidence`, in any chat. Strip the literal string `/confidence` out before treating the rest of the message as the request to be clarified. If `/confidence` is the entire message with no other content, apply the loop to the most recent substantive request in the conversation (i.e., what the user was asking for before they typed `/confidence`).

## What "understanding" covers

Confidence should reflect your understanding of:
- The most recent request in the message (primary focus), AND
- How that request fits with everything discussed earlier in the conversation (secondary, but don't ignore it — e.g., if the new request seems to contradict or shift away from earlier stated goals, that's a confidence hit).

## The loop

1. **Estimate confidence.** Silently assess how confident you are (0–100%) that you understand the full scope and goal of the request — not just the literal words, but what output/outcome would actually satisfy the user. Consider: ambiguous scope, unstated assumptions, multiple plausible interpretations, missing constraints (format, length, audience, deadline, tools to use), and anything that contradicts earlier context.

2. **State it plainly.** Start your response with something like: `Current confidence: 60%`. No padding around this — just the number and a one-line note on what's driving the uncertainty, if useful.

3. **If confidence < 95%:** Ask clarifying questions using the `ask_user_input_v0` tool (interactive multiple-choice buttons). That tool caps at 3 questions per call — use that as the batch size ceiling regardless of how low confidence is. Do NOT try to front-load a long list of questions in prose to work around this; the whole point is small, digestible rounds. Prioritize the questions that would move confidence the most (the biggest sources of ambiguity), not just any open question. After the user answers, go back to step 1 with the new information and run another round.

4. **If confidence >= 95%:** Say so explicitly (e.g., `Current confidence: 95% — starting.`), give a short summary (a few lines, not a full recap) of what you understand the task to be, and then proceed to actually do the work in the same turn. Don't ask for a final go-ahead — proceeding automatically once you hit 95% is the intended behavior.

## Notes on calibration

- Confidence estimates are for the user's benefit, not a formal metric — use your judgment, and don't be falsely precise (round to the nearest 5 or 10%).
- It's fine for confidence to move slowly across multiple rounds on a genuinely fuzzy request. It's also fine to jump straight to 95%+ and skip questions entirely if the request is already unambiguous — the skill shouldn't manufacture uncertainty just to ask questions.
- If the user's answers in a round don't actually resolve the ambiguity (e.g., they pick "none of these" or give a non-answer), don't loop indefinitely — use your best judgment, note the remaining assumption you're making, and proceed.
- This skill governs the clarifying-question *process*, not question content — the actual questions should be tailored to whatever the task is (writing, code, analysis, planning, etc.).
