import {request} from './client'; import type {DashboardSnapshot,Filters} from '../types/dashboard'
export const getDashboard=(f:Filters,signal?:AbortSignal)=>request<DashboardSnapshot>(`/api/dashboard?${new URLSearchParams({range:f.range,region:f.region,category:f.category})}`,{signal})
