import streamlit as st
import requests
url="http://127.0.0.1:8000"
st.title("🤖AI智能记账本")
st.write("你只需要用大白话输入,AI帮你自动拆解分类。")
user_input=st.text_input("请输入你的消费记录",placeholder="例如:打车花了20,中午吃面花了30,晚上充值100")
if st.button("开始记账"):
    if user_input:
        with st.spinner("AI正在分析并记账..."):
            res=requests.post(f"{url}/text",json={"text":user_input})
            if res.status_code==200:
                st.success("记账成功")
                st.rerun()
            else:
                st.error(f"记账失败:{res.json().get('detail','未知错误')}")
    else:
        st.warning("请输入消费记录!")
st.divider()
st.subheader("消费统计")
analysis_res=requests.get(f"{url}/analysis")
if analysis_res.status_code==200:
    data=analysis_res.json()
    st.metric(label="总支出(元)",value=data["总金额"])
    st.write("**分类明细:**")
    table_data=[
        {"分类":"餐厅","金额":data["餐厅"]},
        {"分类":"交通","金额":data["交通"]},
        {"分类":"娱乐","金额":data["娱乐"]},
        {"分类":"购物","金额":data["购物"]},
        {"分类":"其它","金额":data["其它"]},
    ]
    st.table(table_data)
elif analysis_res.status_code==400:
    st.info("当前还没有任何账单哦,快去记一笔吧!")
else:
    st.error("获取统计信息失败,请检查后端是否正常运行。")