import asyncio
import aiohttp
import time
import concurrent.futures
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Retry strategy for requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

# HTTP adapter with retry strategy
adapter = HTTPAdapter(max_retries=retry_strategy)
payload = {"type": 1}
url = 'https://api.quackquack.games/nest/collect'
url2 = 'https://api.quackquack.games/balance/get'
url3 = 'https://api.quackquack.games/golden-duck/reward'
url4 = 'https://api.quackquack.games/golden-duck/claim'
url_hatch = 'https://api.quackquack.games/nest/hatch'
collect_url = 'https://api.quackquack.games/nest/collect-duck'
# Create a session with retry and connection pooling
session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
def read_tokens_nest_ids(filename):
        tokens_nest_ids = []
        with open(filename, 'r') as file:
            for line in file:
                tokens_nest_ids.append(line.strip().split('|'))
        return tokens_nest_ids
async def get_nest_ids(session, token):
    headers = {'Authorization': f'Bearer {token}'}
    async with session.get('https://api.quackquack.games/nest/list-reload', headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            nest_ids = [nest['id'] for nest in data.get('data', {}).get('nest', [])]
            for nest in data.get('data', {}).get('nest', []):
                egg_config_id = nest.get('egg_config_id')
                if egg_config_id is not None and egg_config_id >= 7:
                    try:
                        async with session.post('https://api.quackquack.games/nest/hatch', json={'nest_id': nest['id']}, headers=headers) as response_hatch:
                            response_hatch.raise_for_status()
                            print("Hatch successfully.")
                            await asyncio.sleep(1)
                    except aiohttp.ClientError as e:
                        pass
                try:
                    async with session.post('https://api.quackquack.games/nest/collect-duck', json={'nest_id': nest['id']}, headers=headers) as collect_duck:
                        collect_duck.raise_for_status()
                        print("collect successfully.")
                except aiohttp.ClientError as e:
                    pass
            return nest_ids
        else:
            return []

async def process_nest(session, token_nest_id, idx):
    while True:
        token, *_ = token_nest_id
        nest_ids = await get_nest_ids(session, token)
        if not nest_ids:
            return

        headers = {'Authorization': f'Bearer {token}'}
        for nest_id in nest_ids:
            data = {'nest_id': nest_id}
            
            try:
                async with session.post('https://api.quackquack.games/nest/collect', json=data, headers=headers) as response:
                    response.raise_for_status()
                    
                async with session.get('https://api.quackquack.games/golden-duck/reward', headers=headers) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        amount = json_data["data"]["amount"]
                        data_type = json_data.get("data", {}).get("type")
                        
                        if data_type == 0:
                            print('\033[91mTrúng cái nịt\033[0m')  # Red color
                        elif data_type == 1:
                            with open('tonclaim.txt', 'a') as file:
                                file.write(f'{idx}-ton-Amount: {amount}\n')
                            async with session.post('https://api.quackquack.games/golden-duck/claim', json={"type": 2}, headers=headers) as response:
                                print('\033[94m{}-ton-Amount: {}\033[0m'.format(idx, amount))  # Blue color
                        elif data_type == 2:
                            async with session.post('https://api.quackquack.games/golden-duck/claim', json=payload, headers=headers) as response:
                                print('\033[92m{}-Pepets-Amount: {}\033[0m'.format(idx, amount))  # Green color
                                with open('pepetsclaim.txt', 'a') as file:
                                    file.write(f'{idx}-Pepets-Amount: {amount}\n')
                        elif data_type == 3:
                            async with session.post('https://api.quackquack.games/golden-duck/claim', json=payload, headers=headers) as response:
                                print('{}-Eggs-Amount: {}'.format(idx, amount))
                        else:
                            pass

                        amount = json_data["data"]["amount"]
                        if json_data.get("data", {}).get("type") == 0 :
                            print('Trúng cái nịt')
                        elif json_data.get("data", {}).get("type") == 1 :
                            async with session.post('https://api.quackquack.games/golden-duck/claim', json={"type": 2}, headers=headers) as response:
                                print(f'{idx}-ton-Amount: {amount}')
                        try:
                            async with session.post('https://api.quackquack.games/golden-duck/claim', json=payload, headers=headers) as response:
                                if response.status == 200:
                                    print(f'{idx}-Claimed-golden-duck')
                                else:
                                    pass
                        except aiohttp.ClientError as e:
                            pass
                    
                async with session.get('https://api.quackquack.games/balance/get', headers=headers) as response:
                    response_json = await response.json()
                    account_data = response_json['data']['data']
                    balance = account_data[2]['balance']
                    print(f"{idx} | TỔNG SỐ TRỨNG VỊT 🐥: {balance}")
            except aiohttp.ClientError as e:
                pass

async def main():
    tokens_nest_ids = read_tokens_nest_ids('tokens.txt')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [process_nest(session, token_nest_id, idx) for idx, token_nest_id in enumerate(tokens_nest_ids, start=1)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
