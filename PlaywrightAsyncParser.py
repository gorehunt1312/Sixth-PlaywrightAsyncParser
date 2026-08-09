from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from fake_useragent import UserAgent
import json

ua = UserAgent()

async def main():
    urls = [f'https://quotes.toscrape.com/js/page/{page}/' for page in range(1, 5)]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, timeout=(5000))
        context = await browser.new_context(user_agent=ua.random, viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        tasks = [dev(await context.new_page(), url) for url in urls]
        result = await asyncio.gather(*tasks)
        await browser.close()
        flat_data = [item for result in sublist for item in sublist]
        json_data = [{"text": text, "author": author} for text, author in flat_data]
        with open('quotes.json', 'a', encoding="utf-8") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=1)

async def dev(page, url):
    await page.goto(url, wait_until="networkidle")
    await page.mouse.wheel(0, 400)
    await page.wait_for_timeout(2000)
    html_code = await page.content()
    await page.close()
    soup = BeautifulSoup(html_code, 'html.parser')
    html = soup.find_all('div', class_='quote')
    raw_data = []
    for data in html:
        text = data.find('span', class_='text').text
        author = data.find('small', class_='author').text
        raw_data.append((text, author))
    return raw_data

if __name__ == "__main__":
    asyncio.run(main())