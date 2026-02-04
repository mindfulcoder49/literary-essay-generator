import { ref, onUnmounted } from 'vue'

export function useJobStream(jobId: string) {
  const step = ref('')
  const detail = ref('')
  const done = ref(false)
  const status = ref('')

  let eventSource: EventSource | null = null

  function start() {
    eventSource = new EventSource(`/api/jobs/${jobId}/stream`)

    eventSource.addEventListener('progress', (e: MessageEvent) => {
      const data = JSON.parse(e.data)
      step.value = data.step
      detail.value = data.detail
    })

    eventSource.addEventListener('done', (e: MessageEvent) => {
      const data = JSON.parse(e.data)
      status.value = data.status
      done.value = true
      eventSource?.close()
    })

    eventSource.addEventListener('error', () => {
      done.value = true
      status.value = 'error'
      eventSource?.close()
    })
  }

  function stop() {
    eventSource?.close()
    eventSource = null
  }

  onUnmounted(stop)

  start()

  return { step, detail, done, status, stop }
}
