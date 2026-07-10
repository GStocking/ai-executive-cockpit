<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import MarkdownIt from 'markdown-it'

type Message = { role: 'user' | 'assistant'; content: string }
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const nav = ref('经营总览'), period = ref('本月'), chat = ref(false), input = ref(''), sending = ref(false), loadingReport = ref(false), report = ref('')
const messages = ref<Message[]>([{ role:'assistant', content:'早上好，陈总。我已同步最新经营数据，可以帮您分析销售、库存、生产或利润情况。' }])
const renderedReport = computed(() => new MarkdownIt({breaks:true}).render(report.value))
const kpis = [
  ['本月销售额','¥ 12,860,400','+12.8%','较上月','cyan'],['库存总值','¥ 4,230,800','-3.2%','周转效率提升','violet'],
  ['生产完成率','94.6%','+2.4%','超过目标 1.6%','green'],['综合利润率','18.7%','+1.9%','连续 3 月增长','orange']
]
const alerts = [['高','华东区 A 类产品库存低于安全线','10 分钟前','#ff6b78'],['中','二号产线良品率较昨日下降 1.8%','42 分钟前','#ffb44c'],['低','华南区域回款周期延长 2.3 天','1 小时前','#41d9b5']]

function initCharts(){
  const tooltip={trigger:'axis',backgroundColor:'#142138',borderColor:'#2a3c59',textStyle:{color:'#fff'}}
  const sales=echarts.init(document.querySelector('#sales') as HTMLElement)
  sales.setOption({tooltip,grid:{left:45,right:20,top:25,bottom:28},xAxis:{type:'category',boundaryGap:false,data:['1日','5日','10日','15日','20日','25日','30日'],axisLine:{lineStyle:{color:'#26364d'}},axisLabel:{color:'#71839d'}},yAxis:{type:'value',axisLabel:{color:'#71839d',formatter:'{value}万'},splitLine:{lineStyle:{color:'#1c2b40'}}},series:[{type:'line',smooth:true,symbolSize:7,data:[280,340,318,430,475,520,604],lineStyle:{width:3,color:'#4fe0d0'},itemStyle:{color:'#4fe0d0'},areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(79,224,208,.28)'},{offset:1,color:'rgba(79,224,208,0)'}])}}]})
  const region=echarts.init(document.querySelector('#region') as HTMLElement)
  region.setOption({tooltip,grid:{left:55,right:45,top:15,bottom:15},xAxis:{type:'value',show:false},yAxis:{type:'category',data:['西南','华北','华南','华东'],axisLine:{show:false},axisTick:{show:false},axisLabel:{color:'#91a3ba'}},series:[{type:'bar',barWidth:10,data:[138,196,243,318],itemStyle:{borderRadius:8,color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#6457d8'},{offset:1,color:'#a07cff'}])},label:{show:true,position:'right',color:'#c8d3e3',formatter:'¥{c}万'}}]})
  const stock=echarts.init(document.querySelector('#stock') as HTMLElement)
  stock.setOption({series:[{type:'pie',radius:['62%','82%'],center:['50%','48%'],padAngle:3,label:{show:false},itemStyle:{borderRadius:8},data:[{value:68,itemStyle:{color:'#42d6b3'}},{value:21,itemStyle:{color:'#f5ac4b'}},{value:11,itemStyle:{color:'#f16878'}}]}],graphic:[{type:'text',left:'center',top:'37%',style:{text:'68%',fill:'#fff',font:'600 26px sans-serif'}},{type:'text',left:'center',top:'55%',style:{text:'库存健康',fill:'#7f91aa',font:'12px sans-serif'}}]})
  window.addEventListener('resize',()=>[sales,region,stock].forEach(c=>c.resize()))
}
async function ask(text?:string){
  const value=(text||input.value).trim(); if(!value||sending.value)return
  messages.value.push({role:'user',content:value},{role:'assistant',content:''}); input.value=''; sending.value=true
  const target=messages.value.at(-1)!
  try{const response=await fetch(`${API}/api/chat/stream?message=${encodeURIComponent(value)}`);if(!response.ok||!response.body)throw Error('服务暂时不可用');const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='';while(true){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const parts=buffer.split('\n\n');buffer=parts.pop()||'';for(const event of parts){const line=event.split('\n').find(v=>v.startsWith('data: '));if(line){const data=JSON.parse(line.slice(6));if(data.token)target.content+=data.token}}}}catch(e){target.content=`暂时无法完成分析：${e instanceof Error?e.message:'未知错误'}`}finally{sending.value=false}
}
async function generateReport(){loadingReport.value=true;report.value='';try{const res=await fetch(`${API}/api/report`,{method:'POST'});if(!res.ok)throw Error();report.value=(await res.json()).report}catch{report.value='# 生成失败\n\n请确认分析服务已启动后重试。'}finally{loadingReport.value=false}}
onMounted(async()=>{await nextTick();initCharts()})
</script>

<template>
<div class="app">
  <aside class="side"><div class="brand"><b>A</b><div><strong>AI Executive</strong><small>智能经营驾驶舱</small></div></div><nav>
    <button v-for="(item,i) in ['经营总览','销售分析','库存管理','生产运营','财务分析']" :class="{active:nav===item}" @click="nav=item"><i>{{['◈','↗','◇','⬡','◎'][i]}}</i><span>{{item}}</span></button>
    <label>AI 智能能力</label><button @click="chat=true"><i>✦</i><span>AI 智能助手</span><em>Beta</em></button><button @click="generateReport"><i>▤</i><span>经营分析报告</span></button>
  </nav><div class="user"><b>陈</b><div><strong>陈思远</strong><small>集团总经理</small></div></div></aside>
  <main><header><div><h1>{{nav}}</h1><p>实时洞察关键经营指标，把握业务增长脉搏</p></div><div class="actions"><span class="sync"><i></i>数据已更新 · 09:42</span><button>♢</button><button class="ask" @click="chat=true">✦ 问问 AI</button></div></header>
    <section class="intro"><div><label>GOOD MORNING, 陈总</label><h2>今天的经营态势 <em>稳中向好</em></h2><p>销售额连续 3 周增长，生产履约率高于目标。AI 发现 3 项需要关注的业务信号。</p></div><div class="tabs"><button v-for="p in ['今日','本周','本月','本季']" :class="{active:period===p}" @click="period=p">{{p}}</button></div></section>
    <section class="kpis"><article v-for="k in kpis" :class="k[4]"><div><span>{{k[0]}}</span><button>•••</button></div><strong>{{k[1]}}</strong><footer><em>↗ {{k[2]}}</em><small>{{k[3]}}</small><span class="spark">⌁</span></footer></article></section>
    <section class="grid">
      <article class="panel sales"><div class="head"><div><h3>销售趋势</h3><p>本月累计销售额 · 万元</p></div><span>同比 +18.4%</span></div><div id="sales" class="chart"></div></article>
      <article class="panel"><div class="head"><div><h3>区域销售排行</h3><p>各区域销售贡献</p></div><button>查看全部 →</button></div><div id="region" class="chart"></div></article>
      <article class="panel"><div class="head"><div><h3>库存状态</h3><p>库存结构与风险</p></div></div><div id="stock" class="stock chart"></div><div class="legend"><span>● 健康 68%</span><span>● 临界 21%</span><span>● 预警 11%</span></div></article>
      <article class="panel alerts"><div class="head"><div><h3>AI 经营预警</h3><p>基于实时数据智能识别</p></div><span>✦ AI INSIGHT</span></div><div class="alert" v-for="a in alerts"><em :style="{color:a[3],background:a[3]+'18'}">{{a[0]}}</em><div><b>{{a[1]}}</b><small>{{a[2]}}</small></div><button>›</button></div></article>
    </section>
  </main>
  <div v-if="chat" class="overlay" @click.self="chat=false"><aside class="drawer"><div class="chathead"><div><b class="orb">✦</b><span><strong>AI 经营助手</strong><small>● 在线 · 已连接企业数据</small></span></div><button @click="chat=false">×</button></div><div class="suggest"><button v-for="q in ['分析销售增长原因','当前有哪些经营风险？','给出下月经营建议']" @click="ask(q)">{{q}}</button></div><div class="messages"><div v-for="m in messages" :class="['msg',m.role]"><i v-if="m.role==='assistant'">✦</i><p>{{m.content||'正在分析经营数据…'}}</p></div></div><form @submit.prevent="ask()"><textarea v-model="input" placeholder="输入经营问题，按 Enter 发送" @keydown.enter.exact.prevent="ask()"></textarea><button :disabled="!input.trim()||sending">↑</button></form></aside></div>
  <div v-if="loadingReport||report" class="overlay" @click.self="report='';loadingReport=false"><section class="report"><div class="reporthead"><div><b>✦</b><span><h3>AI 月度经营分析报告</h3><p>基于当前驾驶舱数据自动生成</p></span></div><button @click="report='';loadingReport=false">×</button></div><div v-if="loadingReport" class="loading"><i></i><h3>AI 正在分析经营数据</h3><p>正在汇总销售、库存、生产与利润指标…</p></div><div v-else class="markdown" v-html="renderedReport"></div></section></div>
</div>
</template>
