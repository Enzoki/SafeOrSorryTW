from bs4 import BeautifulSoup
import requests # 確保 requests 函式庫已引入
import re
import datetime as dt
import asyncio
import os
import sys

# Discord Configuration
# 將 TELEGRAM_TOKEN 替換為 DISCORD_WEBHOOK_URL
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def get_travel_advisory(country="taiwan"):
    country = country.lower().replace(' ', '-')
    url = f"https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/{country}-travel-advisory.html"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        text = soup.get_text()
        level = re.search(rf'{country.title().replace("-", " ")} - (Level \d+: [^\n]+)', text).group(1)
        
        alert = soup.find('div', class_='tsg-rwd-emergency-alert-text')
        description = alert.find_all('p')[1].get_text(strip=True) if (alert and len(alert.find_all('p')) > 1) else 'No reason found'

        reasons = {
            i.get_text(strip=True, separator=' ') : i.get('data-tooltip').replace('\xa0', ' ').strip() \
            for i in soup.find_all(class_='showThreat')
        }
            
        return {'country': country.title(), 'level_num': int(level.split(':')[0].split(' ')[1]), 'level_text': level, 'description': description, 'reasons': reasons}
            
    except requests.RequestException as e:
        return {"error": f"Error fetching data: {str(e)}"}

def generate_message_test(travel_adv:dict, levels_map=None):
    
    current_time = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    weekday_phrase = '乖乖去上班吧' if current_time.weekday() < 5 else '好好享受假日吧'
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    levels_map = {
        1: f'今天很安全，{weekday_phrase}。',
        2: '🚨🚨 警戒升級！建議提高警覺！',
        3: '🚨🚨🚨 非常危險！請立即採取應對措施！！！',
        4: '🚨🚨🚨🚨 極度危險！請立即採取應對措施！！！',
    } if levels_map is None else levels_map
    reasons_map = {
        "C": "犯罪率",
        "T": "恐怖主義活動",
        "U": "社會動盪",
        "N": "天災",
        "H": "衛生健康問題",
        "K": "綁架或扣押人質",
        "D": "不正當拘留",
        "O": "其他",
    }
    message = f"{levels_map[travel_adv['level_num']]}\n\n"
    if travel_adv['reasons']!={}:
        message += f"警戒原因：{'、'.join(reasons_map[k] for k in sorted(travel_adv['reasons'].keys()))}。\n\n"
    message += f"原始訊息: \n{travel_adv['country']} - {travel_adv['level_text']}\n"
    if travel_adv['reasons']!={}:
        message += '\n'
        for k, v in travel_adv['reasons'].items():
            message += f"{k}: {v}\n"
    message += f"\n{travel_adv['description']}\n\n"
    message += f"更新時間: {current_time}\n\n"
    message += F"----------"
    
    return message

import datetime as dt

def generate_message(travel_adv: dict, levels_map=None):
    current_time = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    weekday_phrase = '該上班的上班' if current_time.weekday() < 5 else '該享受假日的享受假日'
    current_time_formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # 這部分會被新模板覆寫，但保留以防萬一或作為靈活擴展的基礎
    # levels_map = {
    #     1: f'今天很安全，{weekday_phrase}。',
    #     2: '🚨🚨 警戒升級！建議提高警覺！',
    #     3: '🚨🚨🚨 非常危險！請立即採取應對措施！！！',
    #     4: '🚨🚨🚨🚨 極度危險！請立即採取應對措施！！！',
    # } if levels_map is None else levels_map
    reasons_map = {
        "C": "犯罪率",
        "T": "恐怖主義活動",
        "U": "社會動盪",
        "N": "天災",
        "H": "衛生健康問題",
        "K": "綁架或扣押人質",
        "D": "不正當拘留",
        "O": "其他",
    }

    # --- 根據「選項二」風格重新建構訊息 ---
    message = "✈️ **台灣旅遊警示更新！**\n\n"

    # 處理 Level 1 的特殊說法，並加入表情符號
    if travel_adv['level_num'] == 1:
        message += f"✨ **Level 1 - 正常預防措施** ✨\n"
        message += f"一切安好！今天很安全，{weekday_phrase}囉！😊\n\n"
    else:
        # 對於非 Level 1 的警示，使用更嚴肅的表達方式
        level_phrase = ""
        if travel_adv['level_num'] == 2:
            level_phrase = "🚨🚨 警戒升級！建議提高警覺！"
        elif travel_adv['level_num'] == 3:
            level_phrase = "🚨🚨🚨 非常危險！請立即採取應對措施！！！"
        elif travel_adv['level_num'] == 4:
            level_phrase = "🚨🚨🚨🚨 極度危險！請立即採取應對措施！！！"
        
        message += f"‼️ **{travel_adv['level_text']}** ‼️\n"
        message += f"{level_phrase}\n\n"
        
        if travel_adv['reasons']:
            reasons_list = '、'.join(reasons_map[k] for k in sorted(travel_adv['reasons'].keys()))
            message += f"⚠️ **主要原因：** {reasons_list}。\n\n"
            for k, v in travel_adv['reasons'].items():
                message += f"• **{k}:** {v}\n"
            message += "\n"


    message += "🇹🇼 **美國國務院指出：**\n"
    message += f"**{travel_adv['country']} - {travel_adv['level_text']}**\n\n"

    message += "📋 **詳細說明：**\n"
    message += f"{travel_adv['description']}\n\n"

    message += f"⏰ **更新時間：** {current_time_formatted} (台灣時間)\n"
    # --- 訊息建構結束 ---

    return message

# 新增的 Discord 訊息發送函式
async def send_discord_message(webhook_url, text):
    payload = {
        "content": text
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status() # 如果請求失敗，會拋出 HTTPError
        print("Message sent to Discord successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Discord: {str(e)}", file=sys.stderr)
        sys.exit(1)

# 主執行邏輯，您可以將其放在一個 main 函式中
async def main():
    travel_advisory_data = get_travel_advisory("taiwan") # 替換成您想查詢的國家
    if "error" in travel_advisory_data:
        print(travel_advisory_data["error"], file=sys.stderr)
        sys.exit(1)
    
    message_to_send = generate_message(travel_advisory_data)
    
    if DISCORD_WEBHOOK_URL:
        await send_discord_message(DISCORD_WEBHOOK_URL, message_to_send)
    else:
        print("DISCORD_WEBHOOK_URL environment variable not set.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
