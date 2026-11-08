from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy import create_engine,Column,String,Integer,Boolean
from sqlalchemy.orm import declarative_base,sessionmaker
import json
client=OpenAI(api_key="sk-test",base_url="https://api.deepseek.com")
app=FastAPI()
a="sqlite:///./iii.db"
engine=create_engine(a,connect_args={"check_same_thread":False})
Sessionmaker=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
class Record(Base):
    __tablename__="records"
    id=Column(Integer,primary_key=True,index=True)
    item=Column(String)
    amount=Column(String)
    category=Column(String)
Base.metadata.create_all(bind=engine)
class RecordRequest(BaseModel):
    text:str
@app.post("/api/text")
async def api_text(boot:RecordRequest):
    prompt=f"""
    你现在是一名智能消费分析师。
    用户的消费记录是:"""+boot.text+"""
    请根据用户的消费记录进行拆解,提取出每一笔账的金额、分类,分类类型如(餐厅、交通、娱乐)。
    严格返回一个JSON数组。
    你的回答格式必须是:
    [{"item":"物品名","amount":"金额数字","category":"分类(只能是餐厅/交通/娱乐/购物/其它)"}]。
    不要包含任何的废话,不要用'json包裹。
    """
    response=client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":prompt}]
    )
    ai_text=response.choices[0].message.content
    try:
        clean_text=ai_text.replace("```json","").replace("```","").strip()
        records_list=json.loads(clean_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500,detail="AI返回格式有误,请重试")
    db=Sessionmaker()
    for i in records_list:
        items=Record(item=i["item"],amount=i["amount"],category=i["category"])
        db.add(items)
    db.commit()
    db.close()
    return{"message":"记账成功","data":ai_text}
@app.get("/api/analysis")
async def api_analysis():
    db=Sessionmaker()
    item=db.query(Record).all()
    db.close()
    http=0
    lan=0
    lan1=0
    lan2=0
    lan3=0
    lan4=0
    if item:
        for i in item:
            amount=float(i.amount)
            http+=amount
            if i.category=="餐厅":
                lan+=amount
            elif i.category=="交通":
                lan1+=amount
            elif i.category=="娱乐":
                lan2+=amount
            elif i.category=="购物":
                lan3+=amount
            else:
                lan4+=amount
        return {"总金额":round(http,2),
                "餐厅":round(lan,2),
                "交通":round(lan1,2),
                "娱乐":round(lan2,2),
                "购物":round(lan3,2),
                "其它":round(lan4,2)
            }
    else:
        raise HTTPException(status_code=400,detail="当前暂无账单")