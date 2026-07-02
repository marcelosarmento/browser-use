import asyncio
import sys
import time

from browser_use import Agent, Browser, ChatOllama, Tools

TARGET_URL = 'https://quotes.toscrape.com/'

TASK = f"""
Go to {TARGET_URL}.
Find the first quote on the page and its author.

Important completion rule:
- If the browser_state already shows the first quote and author, do not navigate again.
- Immediately call done with success=true.
- The done text must contain only two lines:
quote: <exact first quote text>
author: <exact author>
"""

OLLAMA_FINALIZATION_HINT = """
For this diagnostic, prefer task completion over further browsing:
- The initial navigation to quotes.toscrape.com is handled before the first model step.
- When Current tab is already https://quotes.toscrape.com/ and the first visible quote/author are present in browser_state, the next action MUST be done.
- Re-navigating to the same URL after the page content is visible is a failure.
- Do not use navigate as a way to 'locate' information that is already in browser_state.
"""


def safe_print(label: str, value: object) -> None:
	"""Print diagnostic values on Windows consoles without crashing on Unicode."""
	text = f'{label} {value}'
	print(text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))


async def main():
	start_total = time.perf_counter()

	llm = ChatOllama(
		model='qwen2.5:7b-instruct',
		host='http://localhost:11434',
		timeout=180,
		ollama_options={
			'temperature': 0,
			'num_ctx': 8192,
			'num_predict': 512,
		},
	)

	# Keep the action space small for local Ollama models, but leave browser navigation
	# available because the initial action uses the same action schema.
	tools = Tools(
		exclude_actions=[
			'search',
			'upload_file',
			'switch',
			'close',
			'extract',
			'screenshot',
			'save_as_pdf',
			'write_file',
			'replace_file',
			'read_file',
			'evaluate',
			'send_keys',
			'go_back',
			'wait',
			'click',
			'input',
			'scroll',
			'find_text',
			'dropdown_options',
			'select_dropdown',
		]
	)

	browser = Browser(
		headless=False,
		allowed_domains=['quotes.toscrape.com'],
		accept_downloads=False,
		auto_download_pdfs=False,
		cross_origin_iframes=False,
		minimum_wait_page_load_time=1,
		wait_for_network_idle_page_load_time=0.5,
		wait_between_actions=0.25,
		highlight_elements=False,
	)

	agent = Agent(
		task=TASK,
		llm=llm,
		browser=browser,
		tools=tools,
		initial_actions=[{'navigate': {'url': TARGET_URL, 'new_tab': False}}],
		directly_open_url=False,
		extend_system_message=OLLAMA_FINALIZATION_HINT,
		use_vision=False,
		flash_mode=False,
		enable_planning=False,
		use_judge=False,
		max_actions_per_step=1,
		max_history_items=6,
		max_failures=3,
		llm_timeout=180,
		step_timeout=120,
		message_compaction=False,
		include_tool_call_examples=True,
		include_recent_events=False,
		save_conversation_path='poc_ollama_conversation.json',
		calculate_cost=False,
		max_clickable_elements_length=8000,
	)

	print('=== POC START ===')
	print('model:', llm.model)
	print('target:', TARGET_URL)

	history = await agent.run(max_steps=4)

	elapsed = time.perf_counter() - start_total

	print('\n=== POC RESULT ===')
	print('elapsed_seconds:', round(elapsed, 2))
	print('steps:', history.number_of_steps())
	print('is_done:', history.is_done())
	print('is_successful:', history.is_successful())
	safe_print('final_result:', history.final_result())
	safe_print('errors:', history.errors())
	print('actions:', history.action_names())
	print('urls:', history.urls())
	print('conversation_file:', 'poc_ollama_conversation.json')


if __name__ == '__main__':
	asyncio.run(main())
