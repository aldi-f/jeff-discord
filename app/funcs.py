from requests import get
import json
import time
import requests
import hashlib
import luadata
from functools import cache
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redis_manager import RedisManager

def dispo(num:int):
    """
    
    """
    if num >= 0.5 and num <=0.69:
        return '●○○○○'
    elif num >= 0.7 and num <=0.89:
        return '●●○○○'
    elif num >= 0.9 and num <=1.1:
        return '●●●○○'
    elif num >= 1.11 and num <=1.3:
        return '●●●●○'
    elif num >= 1.31 and num <=1.55:
        return '●●●●●'


# async def pc_arcane(name:str, rank:int):
    
#     arcane = '_'.join(name.lower().split(' '))
#     res = get(f'https://api.warframe.market/v1/items/{arcane}/orders')
#     data = json.loads(res.text)
#     trades = data['payload']['orders']
#     lowest = [10000, 10000, 10000]
#     for trade in trades:
#         if trade['user']['status'] == 'ingame' and trade['order_type'] == 'sell' and trade['mod_rank'] == rank and trade['platform'] == 'pc':
#             if trade['platinum'] < lowest[0] :
#                 lowest[0] = trade['platinum']
#                 lowest.sort()
    
#     return lowest

# same function for both 
def pricecheck(name:str, rank:int = None):
    if not (name.lower().endswith('prime blueprint') or name.lower().endswith('collar blueprint')):
        name = name.lower().replace(' blueprint','')
    if '-' in name:
        name = ' '.join(name.split('-'))
    if '&' in name:
        name = name.replace('&','and')
    if '\'' in name:
        name = name.replace('\'','')
    prime = '_'.join(name.lower().split(' '))
    res = get(f'https://api.warframe.market/v1/items/{prime}/orders')
    data = json.loads(res.text)
    if "error" in data:
        prime+="_blueprint"
        res = get(f'https://api.warframe.market/v1/items/{prime}/orders')
        data = json.loads(res.text)
    trades = data['payload']['orders']

    lowest = [10000, 10000, 10000]
    for trade in trades:
        if 'mod_rank' in trade:
            if trade['user']['status'] == 'ingame' and trade['order_type'] == 'sell' and trade['mod_rank'] == rank and trade['user']['platform'] != 'switch':
                if trade['platinum'] < lowest[0] :
                    lowest[0] = trade['platinum']
                    lowest.sort(reverse=True)
        else:
            if trade['user']['status'] == 'ingame' and trade['order_type'] == 'sell' and trade['user']['platform'] != 'switch':
                if trade['platinum'] < lowest[0] :
                    lowest[0] = trade['platinum']
                    lowest.sort(reverse=True)
    
    return lowest

def optimized_find(string: str, output_dict: dict, output_key):
    if 'forma' in string.lower():
        output_dict[output_key] = ''
        return
    try:
        arr = pricecheck(string)
        for i,x in enumerate(arr):
            if x == 10000:
                arr[i] = "N/A"
                
        text = f"({arr[2]} , {arr[1]} , {arr[0]})<:Platinum:992917150358589550>"
        output_dict[output_key] = text
    except Exception as e:
        print(f"[optimized_find({string})] error. {e=}")
        output_dict[output_key] = "Failed"

# call function above to create the final string
def find(string: str, rank: int = None):
    if('forma' in string.lower()):
        return ''
    try:
        if int is None:
            arr = pricecheck(string)
        else:
            arr = pricecheck(string,rank)

        for i,x in enumerate(arr):
            if x == 10000:
                arr[i] = "N/A"
        return f"({arr[2]} , {arr[1]} , {arr[0]})<:Platinum:992917150358589550>"
    except Exception as e:
        print(f"[find({string=}, {rank=})] error. {e=}")
        return "Failed"



def relic_pricecheck(string: str):
    
    relic = '_'.join(string.lower().split(' '))+'_relic'
    res = get(f'https://api.warframe.market/v1/items/{relic}/orders')
    data = json.loads(res.text)
    trades = data['payload']['orders']
    lowest = [[10000,0],[10000,0],[10000,0]]
    for trade in trades:
        if trade['user']['status'] == 'ingame' and trade['order_type'] == 'sell' and trade['user']['platform'] != 'switch':
            if trade['platinum'] <lowest[0][0]:
                lowest[0] = [trade['platinum'],trade['quantity']]
                lowest.sort(key=lambda x: x[0])

    return lowest

# special call for relics
def relic_finder(string: str):

    arr = relic_pricecheck(string)
    text = 'Price (Quantity): '
    for x in arr:
        if x[0] == 10000:
            text +=' N/A |'
        else:
            text +=f" {x[0]}<:Platinum:992917150358589550> ({x[1]}) |"
    
    return text[:-1]

# func for mod polarity emotes
def polarity(name:str):
    text = name.lower()
    if text == "vazarin":
        return "<:vazarin:1006594423620124812>"
    
    elif text == "madurai":
        return "<:madurai:1006594433422204989>"
    
    elif text == "naramon":
        return "<:naramon:1006594431782223932>"
    
    elif text == "zenurik":
        return "<:zenurik:1006594421262909590>"
    
    elif text == "unariu":
        return "<:unariu:1006594425595642016>"
    
    elif text == "penjaga":
        return "<:penjaga:1006594429651517551>"
    
    elif text == "umbra":
        return "<:umbra:1006594427772469248>"
    
    elif text == "aura":
        return "<:aura:1006594434718253148>"
    
    else: 
        return ""

def get_shard(archon: str):
    archon = archon.lower()
    if 'amar' in archon:
        return "<:CrimsonArchonShard:1052215232090620034>"

    elif 'nira' in archon:
        return "<:AmberArchonShard:1052215210657714327>"

    elif 'boreal' in archon:
        return "<:AzureArchonShard:1052215162704253030>"

    else:
        return ""
    
## TODO: Remove this
FIRST_WEEK = 1682899200

WIKI_URL_BASE = "https://wiki.warframe.com/api.php"
# Pulled from warframe wiki fandom page
WIKI_MODULE_BODY = {
    "ability:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Ability",
        "content": "return require('Module:LuaSerializer')._serialize('Ability/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "arcane:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Arcane",
        "content": "return require('Module:LuaSerializer')._serialize('Arcane/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "blueprint:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Blueprints",
        "content": "return require('Module:LuaSerializer')._serialize('Blueprints/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "companion:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Companions",
        "content": "return require('Module:LuaSerializer')._serialize('Companions/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "enemy:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Enemies",
        "content": "return require('Module:LuaSerializer')._serialize('Enemies/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "mod:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Mods",
        "content": "return require('Module:LuaSerializer')._serialize('Mods/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "tennogen:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:TennoGen",
        "content": "return require('Module:LuaSerializer')._serialize('TennoGen/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "void:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Void",
        "content": "return require('Module:LuaSerializer')._serialize('Void/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "warframe:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Warframes",
        "content": "return require('Module:LuaSerializer')._serialize('Warframes/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
    "weapon:1": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Weapons",
        "content": "return require('Module:LuaSerializer')._serialize('Weapons/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2"
    },
}

# Pulled from community developer github repo
WFCD = {
    "skins:1" : "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Skins.json",
}

CHECKSUMS = {
    "ability:1": "ability:checksum:1",
    "arcane:1": "arcane:checksum:1",
    "blueprint:1": "blueprint:checksum:1",
    "companion:1": "companion:checksum:1",
    "enemy:1": "enemy:checksum:1",
    "mod:1": "mod:checksum:1",
    "skins:1": "skins:checksum:1",
    "tennogen:1": "tennogen:checksum:1",
    "void:1": "void:checksum:1",
    "warframe:1": "warframe:checksum:1",
    "weapon:1": "weapon:checksum:1",
}

def unserialize_lua_table(lua_table: str)-> dict:
    start_idx = lua_table.find('{')
    end_idx = lua_table.rfind('}') + 1
    lua_table = lua_table[start_idx:end_idx]
    return luadata.unserialize(lua_table)

def update_cache(data_key:str, redis_cache: "RedisManager"):
    ready = False
    retries = 0
    while not ready and retries < 100:
        retries += 1
        print(f"[refill_wiki_data][{time.ctime()}]:\t[Downloading data for '{data_key}'...]")
        try:
            res = requests.post(url=WIKI_URL_BASE, data=WIKI_MODULE_BODY[data_key])
        except:
            print(f"[refill_wiki_data][{time.ctime()}]:\t[Downloading failed '{data_key}'{chr(10)}]")
            continue
        
        return_data = res.json().get('return')

        if return_data:
            # get valid lua table result
            unserialized_data = unserialize_lua_table(return_data)

            checksum = hashlib.md5(bytes("".join(json.dumps(unserialized_data)),encoding="utf-8")).hexdigest()
            cached = False
            # check if we have data cached
            old_checksum = ""
            if redis_cache.cache.exists(CHECKSUMS[data_key]):
                cached = True
                old_checksum = redis_cache.cache.get(CHECKSUMS[data_key])

            ready = True
            if checksum == old_checksum:
                # create a new checksum
                if not cached:
                    text = json.dumps(unserialized_data)
                    # save data
                    redis_cache.cache.set(data_key, text)
                    # save checksum
                    redis_cache.cache.set(CHECKSUMS[data_key],checksum)
                    print(f"[refill_wiki_data][{time.ctime()}]:\t[{data_key} data ready on redis!']")
                else:
                    print(f"[refill_wiki_data][{time.ctime()}]:\t[No new data for {data_key}! Skipping']")
            else:
                text = json.dumps(unserialized_data)
                redis_cache.cache.set(data_key, text)
                redis_cache.cache.set(CHECKSUMS[data_key],checksum)
                print(f"[refill_wiki_data][{time.ctime()}]:\t[{data_key} data ready on redis!']")

            break
        else:
            print(f"[refill_wiki_data][{time.ctime()}]:\t[Downloading not succesful for '{data_key}'data retrieved: {data_key}. Retrying...({retries})]")

@cache
def find_internal_warframe_name(internal_name: str, redis_cache: "RedisManager")-> str|None:
    if not redis_cache.cache.exists("warframe:1"):
        update_cache("warframe:1", redis_cache)

    data = json.loads(redis_cache.cache.get("warframe:1"))['Warframes']
    for name, object in data.items():
        if object.get('InternalName') == internal_name:
            return name

    return None

@cache
def find_internal_skin_name(internal_name: str, redis_cache: "RedisManager")-> str|None:
    if not redis_cache.cache.exists("skin:1"):
        update_cache("skin:1", redis_cache)

    data = json.loads(redis_cache.cache.get("skin:1"))
    for object in data:
        if object.get('uniqueName') == internal_name:
            return object.get('name')

    return None

@cache
def find_internal_companion_name(internal_name: str, redis_cache: "RedisManager")-> str|None:
    if not redis_cache.cache.exists("companion:1"):
        update_cache("companion:1", redis_cache)

    data = json.loads(redis_cache.cache.get("companion:1"))['Companions']
    for name, object in data.items():
        if object.get('InternalName') == internal_name:
            return name

    return None

@cache
def find_internal_ability_name(internal_name: str, redis_cache: "RedisManager")-> str|None:
    if not redis_cache.cache.exists("ability:1"):
        update_cache("ability:1", redis_cache)

    data = json.loads(redis_cache.cache.get("ability:1"))['Ability']
    for name, object in data.items():
        if object.get('InternalName') == internal_name:
            return f"{object.get('Powersuit')}: {name}"

    return None