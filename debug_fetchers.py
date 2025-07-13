import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import re
from typing import Optional


async def debug_rub_to_byn():
    """Отладка RUB/BYN фетчера"""
    print("🔍 Отладка RUB/BYN фетчера...")
    try:
        url = "https://www.alfabank.by/exchange/cards/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"📡 Статус ответа: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"📄 Размер HTML: {len(html)} символов")
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Ищем все таблицы
                    tables = soup.find_all('table')
                    print(f"📊 Найдено таблиц: {len(tables)}")
                    
                    for i, table in enumerate(tables):
                        print(f"\n📋 Таблица {i+1}:")
                        rows = table.find_all('tr')
                        print(f"   Строк: {len(rows)}")
                        
                        for j, row in enumerate(rows[:5]):  # Показываем первые 5 строк
                            cells = row.find_all(['td', 'th'])
                            cell_texts = [cell.get_text(strip=True) for cell in cells]
                            print(f"   Строка {j+1}: {cell_texts}")
                            
                            # Ищем RUB
                            if any('RUB' in text or 'рубль' in text.lower() for text in cell_texts):
                                print(f"   ✅ Найдена строка с RUB в таблице {i+1}")
                                if len(cells) > 2:
                                    sell_text = cells[2].get_text(strip=True)
                                    print(f"   💰 Значение продажи: {sell_text}")
                else:
                    print(f"❌ Ошибка HTTP: {response.status}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def debug_byn_to_kzt():
    """Отладка BYN/KZT фетчера"""
    print("🔍 Отладка BYN/KZT фетчера...")
    try:
        # Попробуем разные тикеры
        tickers = ["BYNKZT=X", "BYNKZT", "BYN-KZT"]
        
        for ticker in tickers:
            print(f"📈 Пробуем тикер: {ticker}")
            try:
                ticker_obj = yf.Ticker(ticker)
                info = ticker_obj.info
                print(f"📊 Информация о тикере: {list(info.keys())}")
                
                if 'regularMarketPrice' in info:
                    print(f"💰 Цена: {info['regularMarketPrice']}")
                    return float(info['regularMarketPrice'])
                else:
                    print("⚠️ Нет данных о цене")
                    
            except Exception as e:
                print(f"❌ Ошибка с тикером {ticker}: {e}")
        
        print("❌ Не удалось получить данные ни с одним тикером")
        return None
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return None


async def debug_usd_to_kzt():
    """Отладка USD/KZT фетчера"""
    print("🔍 Отладка USD/KZT фетчера...")
    try:
        url = "https://fin24.kz/currency/bank/kaspi-bank"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"📡 Статус ответа: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    print(f"📄 Размер HTML: {len(html)} символов")
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Ищем все таблицы
                    tables = soup.find_all('table')
                    print(f"📊 Найдено таблиц: {len(tables)}")
                    
                    for i, table in enumerate(tables):
                        print(f"\n📋 Таблица {i+1}:")
                        rows = table.find_all('tr')
                        print(f"   Строк: {len(rows)}")
                        
                        for j, row in enumerate(rows[:5]):  # Показываем первые 5 строк
                            cells = row.find_all(['td', 'th'])
                            cell_texts = [cell.get_text(strip=True) for cell in cells]
                            print(f"   Строка {j+1}: {cell_texts}")
                            
                            # Ищем USD
                            if any('USD' in text or 'доллар' in text.lower() for text in cell_texts):
                                print(f"   ✅ Найдена строка с USD в таблице {i+1}")
                                if len(cells) > 2:
                                    sell_text = cells[2].get_text(strip=True)
                                    print(f"   💰 Значение продажи: {sell_text}")
                else:
                    print(f"❌ Ошибка HTTP: {response.status}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def main():
    """Главная функция отладки"""
    print("🚀 Запуск отладки фетчеров")
    print("=" * 50)
    
    print("\n1️⃣ Отладка RUB/BYN:")
    await debug_rub_to_byn()
    
    print("\n2️⃣ Отладка BYN/KZT:")
    await debug_byn_to_kzt()
    
    print("\n3️⃣ Отладка USD/KZT:")
    await debug_usd_to_kzt()
    
    print("\n🏁 Отладка завершена!")


if __name__ == "__main__":
    asyncio.run(main()) 