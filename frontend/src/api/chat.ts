import {apiUrl,request} from './client'; import type {StreamHandlers} from '../types/chat'; import type {DashboardSnapshot} from '../types/dashboard'
export async function streamChat(requestId:string,message:string,snapshot:DashboardSnapshot|undefined,handlers:StreamHandlers,signal:AbortSignal){
 const res=await fetch(apiUrl('/api/chat/stream'),{method:'POST',headers:{'Content-Type':'application/json','Accept':'text/event-stream'},body:JSON.stringify({requestId,message,snapshot,timeoutMs:30000,maxRetries:1}),signal}); if(!res.ok||!res.body) throw new Error(`AI 服务暂不可用 (${res.status})`)
 const reader=res.body.getReader(),decoder=new TextDecoder(); let buffer=''
 while(true){const {done,value}=await reader.read(); if(done)break; buffer+=decoder.decode(value,{stream:true}); const blocks=buffer.split('\n\n'); buffer=blocks.pop()||''
  for(const block of blocks){let event='message',data=''; for(const line of block.split('\n')){if(line.startsWith('event:'))event=line.slice(6).trim();if(line.startsWith('data:'))data+=line.slice(5).trim()}
   if(!data)continue; let payload:any; try{payload=JSON.parse(data)}catch{payload={content:data}}
   if(event==='start'&&payload.requestId) handlers.onTask(payload.requestId); if(event==='delta') handlers.onDelta(payload.content??''); if(event==='done'){handlers.onDone();return} if(event==='timeout'){const e=new Error(payload.message||'AI 响应超时');e.name='TimeoutError';throw e} if(event==='cancelled'){const e=new Error('已停止生成');e.name='CancelledError';throw e} if(event==='duplicate')throw new Error('该请求正在处理中，请勿重复提交');if(event==='error') throw new Error(payload.message||'生成失败')
  }} handlers.onDone()
}
export const cancelChat=(id:string)=>request(`/api/chat/${id}/cancel`,{method:'POST'})
