import aiohttp
import asyncio
from tqdm import tqdm

async def fetch(session, url, status_count, sem, pbar):
    async with sem:
        try:
            async with session.get(url) as response:
                status_count[response.status] = status_count.get(response.status, 0) + 1
        except:
            status_count["Failed"] = status_count.get("Failed", 0) + 1
        pbar.update(1)

async def main():
    with open('badqueries.txt', 'r') as f:
        bad_queries = [line.strip() for line in f.readlines()]
    #DEFINIR O DOMAIN AQUI:
    domain = "http://SEU.DOMINIO.br"
    full_urls = [f"{domain}{uri}" for uri in bad_queries]
    status_count = {}

    sem = asyncio.Semaphore(50)  # Limita para 50 requisições concorrentes

    async with aiohttp.ClientSession() as session:
        tasks = []
        with tqdm(total=len(full_urls), desc="Sending requests", ncols=100) as pbar:
            for url in full_urls:
                task = fetch(session, url, status_count, sem, pbar)
                tasks.append(task)

            await asyncio.gather(*tasks)

    total_requests = len(full_urls)
    print("\nStatus Summary:")
    for status, count in status_count.items():
        percentage = (count / total_requests) * 100
        print(f"{status}: {count} ({percentage:.2f}%)")

if __name__ == '__main__':
    asyncio.run(main())
