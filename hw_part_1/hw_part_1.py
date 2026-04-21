import sys
from datetime import datetime, timedelta

import httpx
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")


async def main(index_day):
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime("%d.%m.%Y")
    try:
        response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        return response
    except HttpError as err:
        print(err)
        return None


def print_rates(data):
    if not data:
        print("Немає даних")
        return

    date = data.get("date", "?")
    rates = data.get("exchangeRate", [])

    wanted = {"USD", "EUR"}

    print(f"\n{'='*40}")
    print(f"  Курси валют ПриватБанк — {date}")
    print(f"{'='*40}")
    print(f"{'Валюта':<8} {'Купівля':>10} {'Продаж':>10}")
    print(f"{'-'*8} {'-'*10} {'-'*10}")

    for rate in rates:
        currency = rate.get("currency", "")
        if currency not in wanted:
            continue
        buy  = rate.get("purchaseRate") or rate.get("purchaseRateNB")
        sell = rate.get("saleRate")     or rate.get("saleRateNB")
        buy_str  = f"{buy:.4f}"  if buy  else "—"
        sell_str = f"{sell:.4f}" if sell else "—"
        print(f"{currency:<8} {buy_str:>10} {sell_str:>10}")

    print(f"{'='*40}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Використання: python hw_part_1.py <кількість днів тому>")
        print("Приклад: python hw_part_1.py 0  (сьогодні)")
        print("         python hw_part_1.py 2  (2 дні тому)")
        sys.exit(1)

    r = asyncio.run(main(sys.argv[1]))
    print_rates(r)