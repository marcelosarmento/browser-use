# browser-use + Ollama diagnostic: Surface run

This branch contains a small diagnostic package for a local browser-use run on a Windows Surface using Ollama.

## Scenario

- browser-use: 0.13.3
- model: `qwen2.5:7b-instruct` via Ollama / `ChatOllama`
- target: `https://quotes.toscrape.com/`
- goal: find the first quote and author, then finish with `done`
- observed result: the browser state contained the correct quote and author, but the model returned another `navigate` action instead of `done`; later steps timed out.

## Files

- `poc_ollama_browser_use.py` — test script and browser-use configuration
- `conversation_06a460da-00aa-7cb8-8000-94b7d80ed5ed_1.txt` — browser-use conversation/prompt/browser_state/model response for the 7B run
- `poc_ollama_run_7b.err.log` — browser-use execution log for the 7B run
- `poc_ollama_run_7b.out.log` — script stdout summary for the 7B run
- `poc_ollama_run_iframe1.log` — previous qwen2.5-coder:3b comparison run where DOM extraction was working but finalization/action selection was still poor

## Prompt for analysis

```text
I’m testing browser-use 0.13.3 with Ollama on a local Windows Surface.

Repository branch:
https://github.com/marcelosarmento/browser-use/tree/codex/browser-use-ollama-diagnostics-2026-07-02/diagnostics/browser-use-ollama-surface-2026-07-02

Goal:
Open https://quotes.toscrape.com/, identify the first quote and author, then finish with done.

Model:
qwen2.5:7b-instruct via Ollama / ChatOllama.

Relevant files in this branch:
- diagnostics/browser-use-ollama-surface-2026-07-02/poc_ollama_browser_use.py: the test script
- diagnostics/browser-use-ollama-surface-2026-07-02/conversation_06a460da-00aa-7cb8-8000-94b7d80ed5ed_1.txt: browser-use conversation/prompt/browser_state/model response
- diagnostics/browser-use-ollama-surface-2026-07-02/poc_ollama_run_7b.err.log: browser-use execution log
- diagnostics/browser-use-ollama-surface-2026-07-02/poc_ollama_run_7b.out.log: script stdout summary
- diagnostics/browser-use-ollama-surface-2026-07-02/poc_ollama_run_iframe1.log: previous qwen2.5-coder:3b comparison run

Observed behavior:
The browser state already contains the first quote and author:
"The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking."
Author: Albert Einstein

But the model returned a navigate action back to the same URL instead of calling done. Then later steps timed out and browser-use stopped after consecutive failures.

Assume the site and DOM extraction are working. Focus on why action selection/finalization fails.

Please analyze:
1. Whether this is likely a browser-use prompting/action-schema issue, a ChatOllama/Ollama model behavior issue, or a script/config issue.
2. Why the model might choose navigate again even though the answer is present in browser_state.
3. What concrete changes you would make to the script or browser-use configuration to make this task succeed reliably.
4. Whether we should restrict available actions further, change the task prompt, add examples, change max_actions_per_step/timeouts, or use a different output/tool strategy.
5. Any bug or suspicious behavior visible in the logs.

Please be specific and propose code/config changes, not just general advice.
```

## Analysis and recommended changes

### Diagnosis

This failure is most likely an Ollama / local model action-selection problem amplified by prompt and action-schema choices, not a DOM extraction problem. The saved browser state already contains the exact first quote and author, and the execution log shows browser-use successfully performed the initial URL load before the first model step. The model then produced a second `navigate` action to the same URL instead of finalizing with `done`.

The most suspicious prompt detail is that the conversation's output-format example shows only a `navigate` action. With `include_tool_call_examples=False`, a small local model has less guidance for the `done` action shape, and with the task beginning “Go to …” the model appears to anchor on navigation even after the initial action completed. The model memory says it still needs to “locate” and “extract” the quote, even though that content is visible in `browser_state`, which suggests the model did not treat browser state text as sufficient evidence for completion.

### Concrete script/config recommendations

The updated proof-of-concept script applies these changes:

1. Use an explicit `initial_actions` navigation and set `directly_open_url=False` so URL loading is deterministic and not inferred from the task text.
2. Add an Ollama-specific finalization hint via `extend_system_message` that says visible first quote/author in `browser_state` means the next action must be `done`.
3. Re-enable tool-call examples so `done` has a better chance of appearing in the prompt/schema demonstrations.
4. Reduce the action surface much further for this one-page diagnostic by excluding click/scroll/input/wait/go_back/etc.; after initial navigation, the only useful model action should be completion.
5. Increase Ollama context and generation budgets (`num_ctx=8192`, `num_predict=512`) and agent/model timeouts to reduce local CPU timeout artifacts.
6. Add Windows-safe diagnostic printing so a failed run does not crash while printing Unicode or emoji-containing history errors under cp1252.

### Additional observations from the logs

- Page readiness timeouts are warnings, not the root cause: the browser state was populated with the target page content before the bad model action.
- The repeated step timeouts after the duplicate navigation look secondary: the model selected an unnecessary browser action, then browser-use spent time waiting on page readiness/action completion.
- The final `UnicodeEncodeError` is a separate script bug caused by printing emoji/non-cp1252 characters on a Windows console; it masks the summary output but did not cause the wrong action selection.
- For production reliability, prefer `ChatBrowserUse()` for browser automation tasks. If you must use local Ollama, consider a deterministic custom action that extracts the first quote from the current DOM and returns `ActionResult(is_done=True, success=True, extracted_content=...)`, or use a structured `output_model_schema` after deterministic navigation rather than asking a small local model to choose among browser tools.
