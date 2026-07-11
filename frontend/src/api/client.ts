const configured = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/,'') || ''
export const apiUrl=(path:string)=>`${configured}${path}`
export async function request<T>(path:string,init?:RequestInit):Promise<T>{
 const res=await fetch(apiUrl(path),init); if(!res.ok) throw new Error(`请求失败 (${res.status})`); return res.json() as Promise<T>
}
