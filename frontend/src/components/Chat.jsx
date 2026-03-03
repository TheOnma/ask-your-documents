import { useEffect, useRef } from 'react'

function UserBubble({ text }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[75%]">
        <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-blue-300 text-right mb-1">You</p>
        <div className="bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 text-sm leading-relaxed">
          {text}
        </div>
      </div>
    </div>
  )
}

export default function Chat({ messages, loading }) {
  const bottomRef = useRef(null)

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-4">
      {messages.map((msg, i) => (
        msg.role === 'user'
          ? <UserBubble key={i} text={msg.text} />
          : null
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
