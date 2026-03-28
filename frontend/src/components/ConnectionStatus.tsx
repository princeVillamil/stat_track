interface Props {
  status: 'connecting' | 'connected' | 'disconnected' | 'error'
}

const config = {
  connecting:    { dot: 'bg-yellow-400 animate-pulse', label: 'Connecting...' },
  connected:     { dot: 'bg-green-400',                label: 'Live'          },
  disconnected:  { dot: 'bg-slate-500',                label: 'Offline'       },
  error:         { dot: 'bg-red-400',                  label: 'Error'         },
}

export default function ConnectionStatus({ status }: Props) {
  const { dot, label } = config[status]

  return (
    <div className="flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full ${dot}`} />
      <span className="text-xs text-slate-400">{label}</span>
    </div>
  )
}