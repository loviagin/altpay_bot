import asyncio
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_fetcher import fetch_rub_to_byn, fetch_byn_to_kzt, fetch_usd_to_kzt, fetch_all_rates


async def test_individual_fetchers():
    """Тестирует каждый фетчер отдельно"""
    print("🧪 Тестирование отдельных фетчеров...")
    print("=" * 50)
    
    # Тест 1: RUB/BYN фетчер
    print("\n1️⃣ Тестируем RUB/BYN фетчер...")
    try:
        rub_to_byn = await fetch_rub_to_byn()
        if rub_to_byn:
            print(f"✅ RUB/BYN успешно получен: {rub_to_byn}")
        else:
            print("❌ RUB/BYN не удалось получить")
    except Exception as e:
        print(f"❌ Ошибка при тестировании RUB/BYN: {e}")
    
    # Тест 2: BYN/KZT фетчер
    print("\n2️⃣ Тестируем BYN/KZT фетчер...")
    try:
        byn_to_kzt = await fetch_byn_to_kzt()
        if byn_to_kzt:
            print(f"✅ BYN/KZT успешно получен: {byn_to_kzt}")
        else:
            print("❌ BYN/KZT не удалось получить")
    except Exception as e:
        print(f"❌ Ошибка при тестировании BYN/KZT: {e}")
    
    # Тест 3: USD/KZT фетчер
    print("\n3️⃣ Тестируем USD/KZT фетчер...")
    try:
        usd_to_kzt = await fetch_usd_to_kzt()
        if usd_to_kzt:
            print(f"✅ USD/KZT успешно получен: {usd_to_kzt}")
        else:
            print("❌ USD/KZT не удалось получить")
    except Exception as e:
        print(f"❌ Ошибка при тестировании USD/KZT: {e}")


async def test_all_fetchers():
    """Тестирует все фетчеры одновременно"""
    print("\n🧪 Тестирование всех фетчеров одновременно...")
    print("=" * 50)
    
    try:
        rub_to_byn, byn_to_kzt, usd_to_kzt = await fetch_all_rates()
        
        print("\n📊 Результаты:")
        print(f"   RUB/BYN: {rub_to_byn}")
        print(f"   BYN/KZT: {byn_to_kzt}")
        print(f"   USD/KZT: {usd_to_kzt}")
        
        success_count = sum(1 for rate in [rub_to_byn, byn_to_kzt, usd_to_kzt] if rate is not None)
        print(f"\n✅ Успешно получено курсов: {success_count}/3")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании всех фетчеров: {e}")


async def test_with_calculation():
    """Тестирует фетчинг с расчетом цены"""
    print("\n🧪 Тестирование с расчетом цены...")
    print("=" * 50)
    
    # Импортируем функции расчета
    from db import summarize, rounded_sum
    
    # Тестовые данные
    test_amount = 100.0  # USD
    
    try:
        # Фетчим курсы
        rub_to_byn, byn_to_kzt, usd_to_kzt = await fetch_all_rates()
        
        # Обновляем глобальные переменные в db.py
        import db
        if usd_to_kzt is not None:
            db.usd_to_kzt = usd_to_kzt
        if byn_to_kzt is not None:
            db.byn_to_kzt = byn_to_kzt
        if rub_to_byn is not None:
            db.rub_to_byn = rub_to_byn
        
        # Рассчитываем цену
        calculated_price = summarize(test_amount)
        if calculated_price:
            final_price = rounded_sum(calculated_price)
            
            print(f"\n💰 Расчет цены для {test_amount} USD:")
            print(f"   Рассчитанная цена: {calculated_price}")
            print(f"   Округленная цена: {final_price}")
            
            if final_price:
                print(f"✅ Финальная цена: {final_price} RUB")
            else:
                print("❌ Не удалось округлить цену")
        else:
            print("❌ Не удалось рассчитать цену")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании расчета: {e}")


async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов фетчеров курсов валют")
    print("=" * 50)
    
    # Тест 1: Отдельные фетчеры
    await test_individual_fetchers()
    
    # Тест 2: Все фетчеры одновременно
    await test_all_fetchers()
    
    # Тест 3: С расчетом цены
    await test_with_calculation()
    
    print("\n🏁 Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main()) 