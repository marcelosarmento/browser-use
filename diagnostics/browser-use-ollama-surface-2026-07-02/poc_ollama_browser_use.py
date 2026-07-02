import asyncio
import time

from browser_use import Agent, Browser, ChatOllama, Tools


async def main():
 start_total = time.perf_counter()

 llm = ChatOllama(
 model="qwen2.5:7b-instruct",
 host="http://localhost:11434",
 timeout=120,
 ollama_options={
 "temperature": 0,
 "num_ctx": 4096,
 "num_predict": 256,
 },
 )

 # Bloqueia tools desnecessárias para reduzir risco e prompt/schema.
 tools = Tools(
 exclude_actions=[
 "search",
 "upload_file",
 "switch",
 "close",
 "extract",
 "screenshot",
 "save_as_pdf",
 "write_file",
 "replace_file",
 "read_file",
 "evaluate",
 "send_keys",
 ]
 )

 browser = Browser(
 headless=False,
 allowed_domains=["quotes.toscrape.com"],
 accept_downloads=False,
 auto_download_pdfs=False,
 cross_origin_iframes=False,
 max_iframes=1,
 max_iframe_depth=1,
 minimum_wait_page_load_time=2,
 wait_for_network_idle_page_load_time=2,
 wait_between_actions=0.5,
 highlight_elements=False,
 )

 task = """
 Go to https://quotes.toscrape.com/.
 Find the first quote on the page and its author.
 Finish with done and report only:
 - quote
 - author
 """

 agent = Agent(
 task=task,
 llm=llm,
 browser=browser,
 tools=tools,
 use_vision=False,
 flash_mode=True,
 enable_planning=False,
 use_judge=False,
 max_actions_per_step=1,
 max_history_items=6,
 max_failures=2,
 llm_timeout=120,
 step_timeout=60,
 message_compaction=False,
 include_tool_call_examples=False,
 include_recent_events=False,
 save_conversation_path="poc_ollama_conversation.json",
 calculate_cost=False,
 max_clickable_elements_length=8000,
 )

 print("=== POC START ===")
 print("model:", llm.model)
 print("target:", "https://quotes.toscrape.com/")

 history = await agent.run(max_steps=8)

 elapsed = time.perf_counter() - start_total

 print("\n=== POC RESULT ===")
 print("elapsed_seconds:", round(elapsed, 2))
 print("steps:", history.number_of_steps())
 print("is_done:", history.is_done())
 print("is_successful:", history.is_successful())
 print("final_result:", history.final_result())
 print("errors:", history.errors())
 print("actions:", history.action_names())
 print("urls:", history.urls())
 print("conversation_file:", "poc_ollama_conversation.json")


if __name__ == "__main__":
 asyncio.run(main())
