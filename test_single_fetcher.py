import asyncio
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_fetcher import fetch_rub_to_byn, fetch_byn_to_kzt, fetch_usd_to_kzt


async def test_rub_to_byn():
    """Тестирует только RUB/BYN фетчер"""
    print("🧪 Тестирование RUB/BYN фетчера...")
    result = await fetch_rub_to_byn()
    print(f"Результат: {result}")
    return result


def test_byn_to_kzt():
    """Тестирует только BYN/KZT фетчер"""
    print("🧪 Тестирование BYN/KZT фетчера...")
    result = fetch_byn_to_kzt()
    print(f"Результат: {result}")
    return result


def test_usd_to_kzt():
    """Тестирует только USD/KZT фетчер"""
    print("🧪 Тестирование USD/KZT фетчера...")
    result = fetch_usd_to_kzt()
    print(f"Результат: {result}")
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Использование: python test_single_fetcher.py [rub|byn|usd]")
        print("  rub - тест RUB/BYN фетчера")
        print("  byn - тест BYN/KZT фетчера")
        print("  usd - тест USD/KZT фетчера")
        sys.exit(1)
    
    fetcher_type = sys.argv[1].lower()
    
    if fetcher_type == "rub":
        asyncio.run(test_rub_to_byn())
    elif fetcher_type == "byn":
        test_byn_to_kzt()
    elif fetcher_type == "usd":
        test_usd_to_kzt()
    else:
        print("Неизвестный тип фетчера. Используйте: rub, byn, usd")
        sys.exit(1) 