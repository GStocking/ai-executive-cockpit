import {useState} from 'react'
import {Bot, Check, Copy, RotateCcw, Send, Square, Sparkles, ThumbsDown, ThumbsUp, X} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {useChat} from '../hooks/useChat'
import type {DashboardSnapshot} from '../types/dashboard'

type Feedback = 'up' | 'down'

export function ChatPanel({open, onClose, snapshot}: {open: boolean; onClose: () => void; snapshot?: DashboardSnapshot}) {
  const [text, setText] = useState('')
  const [copiedId, setCopiedId] = useState('')
  const [feedback, setFeedback] = useState<Record<string, Feedback>>({})
  const {messages, status, send, cancel, retry, busy} = useChat(snapshot)

  const submit = () => {
    if (text.trim() && !busy) {
      send(text)
      setText('')
    }
  }

  const copyMessage = async (id: string, content: string) => {
    await navigator.clipboard.writeText(content)
    setCopiedId(id)
    window.setTimeout(() => setCopiedId((current) => current === id ? '' : current), 1600)
  }

  const toggleFeedback = (id: string, value: Feedback) => {
    setFeedback((current) => {
      if (current[id] === value) {
        const next = {...current}
        delete next[id]
        return next
      }
      return {...current, [id]: value}
    })
  }

  return <aside className={`chat-panel ${open ? 'open' : ''}`}>
    <header>
      <span><Bot/>AI 经营助手<small><i/>在线</small></span>
      <button onClick={onClose} aria-label="关闭 AI 助手"><X/></button>
    </header>
    <div className="messages">
      {messages.length === 0
        ? <div className="chat-empty">
            <Sparkles/><b>你好，我是经营助手</b><p>可询问业绩波动、区域表现或经营建议</p>
            {['为什么本月销售额下降？', '哪个区域达成率最高？', '给出三条库存优化建议'].map((question) => <button key={question} onClick={() => send(question)}>{question}</button>)}
          </div>
        : messages.map((message) => <div key={message.id} className={`message ${message.role}`}>
            <div className="message-bubble">
              {message.content
                ? message.role === 'assistant'
                  ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                  : message.content
                : <i className="typing">● ● ●</i>}
            </div>
            {message.role === 'assistant' && message.content && message.status === 'done' && <div className="message-actions">
              <button onClick={() => copyMessage(message.id, message.content)} aria-label="复制回答" title="复制回答">
                {copiedId === message.id ? <Check/> : <Copy/>}<span>{copiedId === message.id ? '已复制' : '复制'}</span>
              </button>
              <button className={feedback[message.id] === 'up' ? 'active' : ''} onClick={() => toggleFeedback(message.id, 'up')} aria-label="赞同回答" title="赞同回答"><ThumbsUp/></button>
              <button className={feedback[message.id] === 'down' ? 'active negative' : ''} onClick={() => toggleFeedback(message.id, 'down')} aria-label="反对回答" title="反对回答"><ThumbsDown/></button>
            </div>}
            {message.role === 'assistant' && ['error', 'timeout'].includes(message.status || '') && <button className="retry" onClick={retry}><RotateCcw/>重试</button>}
          </div>)}
    </div>
    <div className="composer">
      <textarea value={text} onChange={(event) => setText(event.target.value)} onKeyDown={(event) => {if (event.key === 'Enter' && !event.shiftKey) {event.preventDefault(); submit()}}} placeholder="问问经营数据…" disabled={busy}/>
      {busy ? <button className="stop" onClick={cancel}><Square/>停止</button> : <button onClick={submit} disabled={!text.trim()} aria-label="发送"><Send/></button>}
      <small>{status === 'connecting' ? '正在连接 AI…' : 'Enter 发送 · Shift+Enter 换行'}</small>
    </div>
  </aside>
}
