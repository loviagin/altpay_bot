import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import re
from typing import Tuple, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service

async def fetch_rub_to_byn() -> Optional[float]:
    """Фетчит курс RUB к BYN с сайта Альфа-Банка"""
    try:
        # Попробуем несколько источников
        sources = [
            "https://www.alfabank.by/exchange/cards/"
        ]
        
        for url in sources:
            try:
                print(f"🔄 Пробуем получить RUB/BYN с {url}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Ищем курсы в разных форматах
                            patterns = [
                                r'RUB.*?(\d+[.,]\d+)',
                                r'рубль.*?(\d+[.,]\d+)',
                                r'российский.*?(\d+[.,]\d+)'
                            ]
                            
                            for pattern in patterns:
                                matches = re.findall(pattern, html, re.IGNORECASE)
                                if matches:
                                    rate = float(matches[0].replace(',', '.'))
                                    while rate < 1 and rate < 10:
                                        rate *= 10
                                    print(f"✅ Получен курс RUB/BYN: {rate}")
                                    return rate
                            
                            print(f"⚠️ Не найдены курсы на {url}")
                        else:
                            print(f"⚠️ HTTP {response.status} для {url}")
                            
            except Exception as e:
                print(f"⚠️ Ошибка при запросе к {url}: {e}")
                continue
        
        # Если все источники недоступны, используем дефолтное значение
        print("⚠️ Все источники недоступны, используем дефолтное значение")
        return 3.66
        
    except Exception as e:
        print(f"❌ Общая ошибка при фетчинге RUB/BYN: {e}")
        return 3.66

def fetch_usd_to_kzt() -> float | None: 
    url = "https://guide.kaspi.kz/client/ru/app/q1971"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(5)
        # Найти все колонки "Продажа"
        sale_columns = driver.find_elements(By.XPATH, "//div[contains(@class, 'exchange__column') and .//div[contains(text(), 'Продажа')]]")
        if sale_columns:
            # Внутри колонки "Продажа" найти все значения
            sale_items = sale_columns[0].find_elements(By.CLASS_NAME, "exchange__column-item")
            if sale_items:
                # for idx, item in enumerate(sale_items):
                #     print(f"sale_items[{idx}].text: '{item.text}'")
                # Попробуйте взять sale_items[0], sale_items[1], ... и посмотрите, где 525
                usd_sale = sale_items[4].text.replace(",", ".").strip()
                value = float(usd_sale)
                print(f"✅ Курс USD/KZT (продажа): {value}")
                return value
            print("⚠️ Не найдено подходящее числовое значение для продажи USD")
            return None
        print("⚠️ Не найдена колонка продажи или значение USD")
        return None
    finally:
        driver.quit()


def fetch_byn_to_kzt() -> float | None:
    url = "https://wise.com/gb/currency-converter/byn-to-kzt-rate"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")
            # Ищем блок с курсом вида: Br1.000 BYN = ₸160.0 KZT
            match = re.search(r'BYN\s*=\s*₸<span[^>]*>([\d.,]+)</span>', html)
            if match:
                rate = float(match.group(1).replace(",", "."))
                print(f"✅ Курс BYN/KZT с Wise: {rate}")
                return rate
            # Альтернативный способ — искать по классу
            h3 = soup.find("h3", class_="cc__source-to-target")
            if h3:
                text = h3.get_text()
                match = re.search(r'BYN\s*=\s*₸([\d.,]+)', text)
                if match:
                    rate = float(match.group(1).replace(",", "."))
                    print(f"✅ Курс BYN/KZT с Wise: {rate}")
                    return rate
        print("⚠️ Не удалось найти курс BYN/KZT на странице Wise")
        return None
    except Exception as e:
        print(f"❌ Ошибка при фетчинге BYN/KZT с Wise: {e}")
        return None


async def fetch_all_rates() -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Фетчит все три курса валют одновременно"""
    tasks = [
        fetch_rub_to_byn(),
    ]

    # Используем run_in_executor для запуска синхронной функции fetch_usd_to_kzt
    loop = asyncio.get_event_loop()
    usd_to_kzt = await loop.run_in_executor(None, fetch_usd_to_kzt)

    # Используем run_in_executor для запуска синхронной функции fetch_byn_to_kzt
    loop = asyncio.get_event_loop()
    byn_to_kzt = await loop.run_in_executor(None, fetch_byn_to_kzt)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    rub_to_byn = results[0] if not isinstance(results[0], Exception) else None
    byn_to_kzt = results[1] if not isinstance(results[1], Exception) else None
    usd_to_kzt = results[2] if not isinstance(results[2], Exception) else None
    
    print(f"📊 Полученные курсы:")
    print(f"   RUB/BYN: {rub_to_byn}")
    print(f"   BYN/KZT: {byn_to_kzt}")
    print(f"   USD/KZT: {usd_to_kzt}")
    
    return rub_to_byn, byn_to_kzt, usd_to_kzt 