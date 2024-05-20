import asyncio
import aiohttp

lay_egg_url = 'https://api.quackquack.games/nest/lay-egg'

def read_tokens_nest_ids(filename):
    tokens_nest_ids = []
    with open(filename, 'r') as file:
        for line in file:
            tokens_nest_ids.append(line.strip().split('|'))
    return tokens_nest_ids

async def lay_egg_if_ready(session, token, nest_id, duck_id):
    headers = {'Authorization': f'Bearer {token}'}
    payload = {'nest_id': nest_id, 'duck_id': duck_id}
    try:
        async with session.post(lay_egg_url, json=payload, headers=headers) as response:
            if response.status == 200:
                print(f"Lay egg successfully for nest_id: {nest_id} and duck_id: {duck_id}")
            else:
                pass
                #print(f"Error laying egg for nest_id: {nest_id} and duck_id: {duck_id}")
    except aiohttp.ClientError as e:
        pass

async def check_and_lay_eggs(tokens_nest_ids):
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for token_info in tokens_nest_ids:
                token, *_ = token_info
                headers = {'Authorization': f'Bearer {token}'}
                try:
                    async with session.get('https://api.quackquack.games/nest/list-reload', headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            for nest in data['data']['nest']:
                                nest_id = nest['id']
                                if nest['egg_config_id'] is None:
                                    for duck in data['data']['duck']:
                                        duck_id = duck['id']
                                        if duck['status'] == 1:
                                            task = asyncio.create_task(lay_egg_if_ready(session, token, nest_id, duck_id))
                                            tasks.append(task)
                                else:
                                    pass
                                  #  print(f"Nest {nest_id} already has an egg.")
                        else:
                            pass
                           # print(f"Error getting nest IDs: {response.status}")
                except aiohttp.ClientError as e:
                    pass
            await asyncio.gather(*tasks)

tokens_nest_ids = read_tokens_nest_ids('tokens.txt')
asyncio.run(check_and_lay_eggs(tokens_nest_ids))
