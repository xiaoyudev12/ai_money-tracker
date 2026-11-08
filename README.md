# AI 智能记账本

一个本地跑的全栈记账工具。

平时记账太麻烦，要选分类要填表。这个工具直接用大模型处理自然语言，你只要打字输入“打车20，吃面30”，它就能自己识别金额和分类，然后存进 SQLite 数据库里。

前端用 Streamlit 写的，后端是 FastAPI。

怎么运行：
1. 装包：pip install fastapi uvicorn sqlalchemy openai streamlit requests pydantic
2. 去 backend.py 里填入自己的 DeepSeek API Key。
3. 跑后端：uvicorn backend:app --reload
4. 跑前端：streamlit run frontend.py

自用练手项目，主打一个极简。
