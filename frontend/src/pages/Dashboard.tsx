import {useMemo, useState} from 'react'
import {Bot, CalendarDays, ChevronDown, Filter, LayoutDashboard, RefreshCw, Sparkles} from 'lucide-react'
import {useDashboard} from '../hooks/useDashboard'
import type {Filters, RangeKey} from '../types/dashboard'
import {MetricCard} from '../components/MetricCard'
import {CategoryChart, RegionChart, TrendChart} from '../components/Charts'
import {ChatPanel} from '../components/ChatPanel'

const ranges: {key: RangeKey; label: string}[] = [
  {key: '7d', label: '近7天'},
  {key: '30d', label: '近30天'},
  {key: '90d', label: '近90天'},
  {key: 'ytd', label: '本年'},
]

const regionOptions = [
  ['all', '全部'], ['east', '华东'], ['south', '华南'], ['north', '华北'], ['west', '西部'],
]
const categoryOptions = [
  ['all', '全部'], ['womens', '女装'], ['mens', '男装'], ['kids', '童装'], ['sports', '运动'], ['accessories', '配饰'],
]
const categoryValue = Object.fromEntries(categoryOptions.map(([value, label]) => [label, value]))
const regionValue = Object.fromEntries(regionOptions.map(([value, label]) => [label, value]))

export default function Dashboard() {
  const [filters, setFilters] = useState<Filters>({range: '30d', region: 'all', category: 'all'})
  const [active, setActive] = useState('sales')
  const [chat, setChat] = useState(false)
  const stableFilters = useMemo(() => filters, [filters])
  const {data, loading, error, refresh} = useDashboard(stableFilters)
  const selectedMetric = data?.metrics.find((metric) => metric.key === active) ?? data?.metrics[0]
  const setFilter = <K extends keyof Filters>(key: K, value: Filters[K]) => setFilters((current) => ({...current, [key]: value}))

  return <div className="app">
    <nav>
      <div className="brand"><span><Sparkles/></span><b>智策驾驶舱<small>AI EXECUTIVE COCKPIT</small></b></div>
      <a className="nav-active"><LayoutDashboard/>经营总览</a>
      <div className="nav-bottom"><span className="avatar">EC</span><div>经营分析团队<small>数据每 2 秒更新</small></div></div>
    </nav>
    <main>
      <header className="topbar">
        <div><h1>经营总览</h1><p>实时洞察核心经营指标，把握业务脉搏</p></div>
        <div className="live"><i/>数据实时连接</div>
        <button className="ai-button" onClick={() => setChat(true)}><Bot/>问问 AI</button>
      </header>
      <section className="filters">
        <div className="range">{ranges.map((item) => <button className={filters.range === item.key ? 'active' : ''} onClick={() => setFilter('range', item.key)} key={item.key}>{item.label}</button>)}</div>
        <label><CalendarDays/><select value={filters.region} onChange={(event) => setFilter('region', event.target.value)}>{regionOptions.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select><ChevronDown/></label>
        <label><Filter/><select value={filters.category} onChange={(event) => setFilter('category', event.target.value)}>{categoryOptions.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select><ChevronDown/></label>
        <button className="refresh" onClick={() => refresh()} disabled={loading}><RefreshCw className={loading ? 'spin' : ''}/>{loading ? '更新中' : '刷新'}</button>
        <span className="updated">更新于 {data?.updatedAt ? new Date(data.updatedAt).toLocaleTimeString('zh-CN', {hour12: false}) : '--:--:--'}</span>
      </section>
      {error && !data
        ? <div className="state"><b>数据加载失败</b><p>{error}</p><button onClick={() => refresh()}>重新加载</button></div>
        : data && selectedMetric
          ? <><section className="metrics">{data.metrics.map((metric) => <MetricCard key={metric.key} metric={metric} active={active === metric.key} onClick={() => setActive(metric.key)}/>)}</section><section className="grid"><TrendChart data={data.trend} metric={selectedMetric}/><CategoryChart data={data.categories} selected={categoryOptions.find(([value]) => value === filters.category)?.[1] ?? '全部'} onSelect={(label) => setFilter('category', categoryValue[label] ?? 'all')}/><RegionChart data={data.regions} onSelect={(label) => setFilter('region', regionValue[label] ?? 'all')}/></section></>
          : <div className="skeletons">{Array(8).fill(0).map((_, index) => <i key={index}/>)}</div>}
    </main>
    <ChatPanel open={chat} onClose={() => setChat(false)} snapshot={data?.snapshot}/>
    {chat && <div className="overlay" onClick={() => setChat(false)}/>}
  </div>
}
