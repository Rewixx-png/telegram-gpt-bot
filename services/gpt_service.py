# services/gpt_service.py

import logging
import re
import asyncio
import httpx
from playwright.async_api import async_playwright
from typing import List, Dict

from openai import AsyncOpenAI
from config_data.config import config
from services import history_service

client = AsyncOpenAI(api_key=config.gpt.api_key, base_url=config.gpt.base_url)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

async def search_with_tavily_api(query: str) -> List[Dict[str, str]] | str:
    logging.info(f"Выполняется API-поиск (Tavily) по запросу: '{query}'")
    payload = {"api_key": config.gpt.tavily_api_key, "query": query, "search_depth": "basic", "include_answer": False, "max_results": 5}
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post("https://api.tavily.com/search", json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            return [{"url": item.get("url"), "content": item.get("content")} for item in data.get("results", [])]
    except Exception as e:
        logging.error(f"Критическая ошибка при поиске через Tavily API: {e}")
        return "Произошла непредвиденная ошибка при поиске."

async def take_website_screenshot(url: str) -> str | None:
    screenshot_path = "website_screenshot.png"
    logging.info(f"Делаем скриншот сайта: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            try:
                button_locator = page.get_by_text(re.compile(r"I am 18|Enter|Accept|Agree|Confirm|Continue|18\+|I Agree", re.IGNORECASE)).first
                await button_locator.click(timeout=3000)
                await page.wait_for_timeout(1500)
            except Exception:
                pass
            await page.screenshot(path=screenshot_path)
            return screenshot_path
        except Exception as e:
            logging.error(f"Ошибка при создании скриншота сайта: {e}")
            return None
        finally:
            await browser.close()

async def get_gpt_response(user_id: int, prompt: str) -> tuple[str | None, str | None]:
    messages = await history_service.get_history(user_id)
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(model=config.gpt.model, messages=messages)
        assistant_response = response.choices[0].message.content.strip()

        search_match = re.fullmatch(r"<search>(.*?)</search>", assistant_response)
        screenshot_match = re.fullmatch(r"<screenshot>(.*?)</screenshot>", assistant_response)
        find_and_screenshot_match = re.fullmatch(r"<find_and_screenshot>(.*?)</find_and_screenshot>", assistant_response)

        if find_and_screenshot_match:
            query = find_and_screenshot_match.group(1)
            logging.info(f"ИИ запустил суперинструмент: найти и сделать скриншот '{query}'")
            search_results = await search_with_tavily_api(query)
            if isinstance(search_results, str) or not search_results:
                return ("Ни хрена не нашел по твоему запросу.", None)
            first_url = search_results[0].get("url")
            if not first_url:
                return ("Нашел какую-то дичь без ссылок, не могу сделать скриншот.", None)
            logging.info(f"Найдена ссылка: {first_url}. Делаю скриншот...")
            file_path = await take_website_screenshot(first_url)
            if file_path:
                return ("Нашел эту херню и сфоткал. Держи.", file_path)
            else:
                return ("Нашел сайт, но он, похоже, сдох. Скриншот не получился.", None)

        elif search_match:
            query = search_match.group(1)
            logging.info(f"ИИ решил искать: '{query}'")
            search_results = await search_with_tavily_api(query)
            # Tavily теперь возвращает список, а не строку, адаптируем
            if isinstance(search_results, str):
                context = search_results
            else:
                context = "\n\n".join([res.get("content", "") for res in search_results])

            final_prompt_messages = [
                {"role": "system", "content": history_service.get_system_prompt()},
                {"role": "user", "content": f"Мой первоначальный вопрос был: '{prompt}'. Информация, найденная в интернете: '{context}'. Основываясь на этой информации, дай мне окончательный ответ."},
            ]
            final_response = await client.chat.completions.create(model=config.gpt.model, messages=final_prompt_messages)
            final_answer = final_response.choices[0].message.content
            await history_service.add_message_to_history(user_id, "user", prompt)
            await history_service.add_message_to_history(user_id, "assistant", final_answer)
            return (final_answer, None)

        elif screenshot_match:
            url = screenshot_match.group(1)
            logging.info(f"ИИ решил сделать скриншот: '{url}'")
            if url.startswith("http"):
                 file_path = await take_website_screenshot(url)
            else:
                 return ("Ты что, дебил? Это не ссылка.", None)
            if file_path:
                return ("Держи, чего уставился?", file_path)
            else:
                return ("Не смог сделать скриншот, сайт не отвечает или какая-то херня случилась.", None)
        
        else:
            await history_service.add_message_to_history(user_id, "user", prompt)
            await history_service.add_message_to_history(user_id, "assistant", assistant_response)
            return (assistant_response, None)

    except Exception as e:
        logging.error(f"Критическая ошибка в get_gpt_response: {e}", exc_info=True)
        return ("У меня в мозгах что-то коротнуло. Попробуй позже.", None)

async def generate_single_response(prompt: str) -> str | None:
    try:
        system_prompt = history_service.get_system_prompt()
        messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}]
        response = await client.chat.completions.create(model=config.gpt.model, messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Ошибка при генерации одиночного ответа от OpenAI: {e}", exc_info=True)
        return None