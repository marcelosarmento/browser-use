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
