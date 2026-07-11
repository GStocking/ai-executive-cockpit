export type ChatStatus='idle'|'connecting'|'streaming'|'done'|'error'|'timeout'|'cancelled'
export interface ChatMessage { id:string; role:'user'|'assistant'; content:string; status?:ChatStatus; question?:string }
export interface StreamHandlers { onTask:(id:string)=>void; onDelta:(text:string)=>void; onDone:()=>void }
