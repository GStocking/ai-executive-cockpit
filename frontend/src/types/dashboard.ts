export type RangeKey = '7d'|'30d'|'90d'|'ytd'
export interface Filters { range: RangeKey; region: string; category: string }
export interface Metric { key: string; label: string; value: number; unit: string; change: number; trend: number[]; secondary?:string }
export interface TrendPoint { date: string; sales: number; volume: number; target?: number }
export interface CategoryDatum { name: string; value: number; share: number }
export interface RegionDatum { name: string; sales: number; target: number }
export interface DashboardData { snapshot:DashboardSnapshot; metrics: Metric[]; trend: TrendPoint[]; categories: CategoryDatum[]; regions: RegionDatum[]; updatedAt: string }
export interface ApiMetric { value:number; unit:string; change:number; trend:'up'|'down'|'flat' }
export interface DashboardSnapshot { snapshot_id:string; generated_at:string; refresh_interval_ms:number; filters:Filters; sales_amount:ApiMetric; sales_volume:ApiMetric; discount_rate:ApiMetric; inventory_turnover:ApiMetric; productivity_per_capita:ApiMetric; on_time_delivery_rate:ApiMetric }
