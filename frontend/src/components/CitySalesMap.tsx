import {useMemo, useState} from 'react'
import china from '@svg-maps/china'

interface MapLocation {
  id: string
  name: string
  path: string
}

const chinaMap = china as {viewBox: string; locations: MapLocation[]}

interface CityPoint {
  name: string
  x: number
  y: number
  share: number
  labelX: number
  labelY: number
}

const cities: CityPoint[] = [
  {name: '北京', x: 546, y: 250, share: .15, labelX: 560, labelY: 214},
  {name: '上海', x: 620, y: 404, share: .18, labelX: 642, labelY: 374},
  {name: '杭州', x: 602, y: 424, share: .12, labelX: 628, labelY: 448},
  {name: '广州', x: 536, y: 506, share: .14, labelX: 554, labelY: 535},
  {name: '成都', x: 405, y: 387, share: .11, labelX: 363, labelY: 414},
  {name: '武汉', x: 520, y: 396, share: .10, labelX: 498, labelY: 358},
  {name: '西安', x: 445, y: 330, share: .08, labelX: 411, labelY: 302},
  {name: '沈阳', x: 626, y: 230, share: .07, labelX: 650, labelY: 202},
  {name: '重庆', x: 448, y: 405, share: .05, labelX: 414, labelY: 451},
]

const formatSales = (value: number) => `${Math.round(value).toLocaleString('zh-CN')} 件`

export function CitySalesMap({totalSales}: {totalSales: number}) {
  const [activeCity, setActiveCity] = useState<string>('')
  const data = useMemo(() => cities.map((city) => ({...city, sales: totalSales * city.share})), [totalSales])
  const maxSales = Math.max(...data.map((city) => city.sales))
  const highlighted = data.find((city) => city.name === activeCity)

  return <section className="city-map-card">
    <div className="city-map-head">
      <div><b>城市销量地图</b><span>核心城市销量分布 · 气泡大小代表销量</span></div>
      <div className="city-map-total"><small>城市样本销量</small><strong>{formatSales(totalSales)}</strong></div>
    </div>
    <div className="city-map-stage">
      <svg viewBox={chinaMap.viewBox} role="img" aria-label="中国城市销量分布地图">
        <defs>
          <filter id="map-shadow" x="-15%" y="-15%" width="130%" height="130%"><feDropShadow dx="0" dy="4" stdDeviation="5" floodColor="#506e74" floodOpacity=".18"/></filter>
          <radialGradient id="city-pulse"><stop offset="0" stopColor="#ff7a2f" stopOpacity=".5"/><stop offset="1" stopColor="#ff7a2f" stopOpacity="0"/></radialGradient>
          <linearGradient id="province-tech" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#153c5b"/><stop offset="1" stopColor="#0b263f"/></linearGradient>
          <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <g className="china-shape" filter="url(#map-shadow)">{chinaMap.locations.map((location) => <path d={location.path} key={location.id}><title>{location.name}</title></path>)}</g>
        {data.map((city) => {
          const radius = 5 + city.sales / maxSales * 8
          const anchorY = city.labelY < city.y ? city.labelY + 8 : city.labelY - 14
          return <g className={`city-marker ${activeCity === city.name ? 'active' : ''}`} key={city.name} tabIndex={0} role="button" aria-label={`${city.name}销量 ${formatSales(city.sales)}`} onMouseEnter={() => setActiveCity(city.name)} onMouseLeave={() => setActiveCity('')} onFocus={() => setActiveCity(city.name)} onBlur={() => setActiveCity('')}>
            <title>{city.name}：{formatSales(city.sales)}</title>
            <line x1={city.x} y1={city.y} x2={city.labelX} y2={anchorY}/>
            <circle className="city-pulse" cx={city.x} cy={city.y} r={radius * 2.2}/>
            <circle className="city-dot" cx={city.x} cy={city.y} r={radius}/>
            <circle className="city-core" cx={city.x} cy={city.y} r="2.8"/>
            <text className="city-name" x={city.labelX} y={city.labelY}>{city.name}</text>
            <text className="city-sales" x={city.labelX} y={city.labelY + 14}>{formatSales(city.sales)}</text>
          </g>
        })}
      </svg>
      <div className={`map-hud ${highlighted ? 'visible' : ''}`}>
        <small>LIVE CITY SIGNAL</small>
        <b>{highlighted?.name ?? '城市节点'}</b>
        <strong>{highlighted ? formatSales(highlighted.sales) : '移动到城市查看'}</strong>
        <span><i/>DATA CONNECTED</span>
      </div>
      <div className="city-map-legend"><i/><span>销量越高，城市标记越大</span></div>
    </div>
  </section>
}
