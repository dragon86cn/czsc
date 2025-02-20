# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2022/7/12 14:22
describe: 使用 QMT 数据进行 CZSC K线检查

环境：
streamlit-echarts
"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
sys.path.insert(0, '../..')
import streamlit as st
import pandas as pd
from datetime import datetime
from czsc.utils import KlineChart
from czsc.traders.base import CzscSignals, BarGenerator
from czsc.utils import freqs_sorted
from czsc.connectors import qmt_connector as qmc

st.set_page_config(layout="wide")

config = {
    "scrollZoom": True,
    "displayModeBar": True,
    "displaylogo": False,
    'modeBarButtonsToRemove': [
        'zoom2d',
        'toggleSpikelines',
        'pan2d',
        'select2d',
        'zoomIn2d',
        'zoomOut2d',
        'lasso2d',
        'autoScale2d',
        'hoverClosestCartesian',
        'hoverCompareCartesian']}


with st.sidebar:
    st.title("CZSC复盘工具")
    symbol = st.selectbox("选择合约", options=qmc.get_symbols('train'), index=0)
    sdt = st.date_input("开始日期", value=datetime(2015, 1, 1))
    edt = st.date_input("结束日期", value=datetime.now())
    freqs = st.multiselect("选择频率", options=['1分钟', '5分钟', '15分钟', '30分钟', '60分钟', '日线', '周线', '月线'], default=['30分钟', '日线'])
    freqs = freqs_sorted(freqs)

bars = qmc.get_raw_bars(symbol, freqs[0], sdt=sdt, edt=edt)
bg = BarGenerator(base_freq=freqs[0], freqs=freqs[1:], max_count=1000)
counts = 100
for bar in bars[:-counts]:
    bg.update(bar)
cs, remain_bars = CzscSignals(bg), bars[-counts:]
for bar in remain_bars:
    cs.update_signals(bar)

for i, freq in enumerate(freqs):
    c = cs.kas[freq]
    df = pd.DataFrame(c.bars_raw)
    df['text'] = "测试"
    kline = KlineChart(n_rows=3, title=f"{freq} K线", width="100%")
    kline.add_kline(df, name="K线")
    kline.add_sma(df, ma_seq=(5, 10, 21), row=1, visible=True)
    kline.add_sma(df, ma_seq=(34, 55, 89, 144), row=1, visible=False)
    kline.add_vol(df, row=2)
    kline.add_macd(df, row=3)
    if len(c.bi_list) > 0:
        bi = pd.DataFrame(
            [{'dt': x.fx_a.dt, "bi": x.fx_a.fx, "text": x.fx_a.mark.value} for x in c.bi_list] +
            [{'dt': c.bi_list[-1].fx_b.dt, "bi": c.bi_list[-1].fx_b.fx,
              "text": c.bi_list[-1].fx_b.mark.value}])
        fx = pd.DataFrame([{'dt': x.dt, "fx": x.fx} for x in c.fx_list])
        kline.add_scatter_indicator(fx['dt'], fx['fx'], name="分型", row=1, line_width=1.2)
        kline.add_scatter_indicator(bi['dt'], bi['bi'], name="笔", text=bi['text'], row=1, line_width=1.2)
    st.plotly_chart(kline.fig, use_container_width=True, height=300, config=config)


