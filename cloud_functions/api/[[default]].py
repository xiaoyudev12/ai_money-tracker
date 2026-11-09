import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import json

# 1. 安全读取 API Key（从云环境变量里拿）
api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-test")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
app = FastAPI()

# 2. 临时的内存数据库（先放弃 SQLite，为了能在云端跑）
mock_records = [] 

class RecordRequest(BaseModel):
    text: str

@app.post("/text")
async def api_text(boot: RecordRequest):
    prompt = f"""
    你现在是一名智能消费分析师。
    用户的消费记录是:{boot.text}
    请根据用户的消费记录进行拆解,提取出每一笔账的金额、分类,分类类型如(餐厅、交通、娱乐)。
    严格返回一个JSON数组。
    你的回答格式必须是:
    [{{"item":"物品名","amount":"金额数字","category":"分类(只能是餐厅/交通/娱乐/购物/其它)"}}]。
    不要包含任何的废话。
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    ai_text = response.choices[0].message.content
    try:
        clean_text = ai_text.replace("```json", "").replace("```", "").strip()
        records_list = json.loads(clean_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI返回格式有误,请重试")
    
    # 存入内存
    for i in records_list:
        mock_records.append(i)
    return {"message": "记账成功", "data": ai_text}

@app.get("/analysis")
async def api_analysis():
    if not mock_records:
        raise HTTPException(status_code=400, detail="当前暂无账单")
    
    # 简单统计
    stats = {"总金额": 0.0, "餐厅": 0.0, "交通": 0.0, "娱乐": 0.0, "购物": 0.0, "其它": 0.0}
    for i in mock_records:
        amount = float(i["amount"])
        stats["总金额"] += amount
        cat = i["category"]
        if cat in stats:
            stats[cat] += amount
        else:
            stats["其它"] += amount
            
    # 保留两位小数
    for k in stats:
        stats[k] = round(stats[k], 2)
    return stats