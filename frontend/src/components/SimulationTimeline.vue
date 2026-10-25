<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
})

const workers = computed(() => {
  if (!props.result) return []
  return Array.from({ length: props.result.worker_count }, (_, index) => {
    const workerId = index + 1
    return {
      id: workerId,
      tasks: props.result.schedule.filter((item) => item.worker_id === workerId),
    }
  })
})

const activeWorkerCount = computed(() => {
  return new Set(props.result?.schedule.map((item) => item.worker_id) ?? []).size
})

const idleWorkerCount = computed(() => {
  return Math.max((props.result?.worker_count ?? 0) - activeWorkerCount.value, 0)
})

function blockStyle(item) {
  const total = props.result.total_duration || 1
  return {
    left: `${(item.start_time / total) * 100}%`,
    width: `${Math.max(((item.end_time - item.start_time) / total) * 100, 4)}%`,
  }
}
</script>

<template>
  <div v-if="result" class="timeline">
    <div class="timeline-summary">
      <div>
        <span>Total time</span><strong>{{ result.total_duration }}s</strong>
      </div>
      <div>
        <span>Workers</span><strong>{{ result.worker_count }}</strong>
      </div>
      <div>
        <span>Tasks</span><strong>{{ result.schedule.length }}</strong>
      </div>
    </div>

    <p v-if="idleWorkerCount" class="worker-note">
      {{ activeWorkerCount }} of {{ result.worker_count }} workers were used.
      {{ idleWorkerCount }} remained idle because task dependencies limited parallel work.
    </p>

    <div class="timeline-grid">
      <div v-for="worker in workers" :key="worker.id" class="worker-row">
        <span class="worker-label">Worker {{ worker.id }}</span>
        <div class="worker-track">
          <div
            v-for="item in worker.tasks"
            :key="item.task_id"
            class="timeline-block"
            :style="blockStyle(item)"
            :title="`${item.task_name}: ${item.start_time}s to ${item.end_time}s`"
          >
            <span>{{ item.task_name }}</span>
            <small>{{ item.start_time }}-{{ item.end_time }}s</small>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="timeline-empty">
    Validate the pipeline, choose workers, then run a simulation.
  </div>
</template>

<style scoped>
.timeline-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 16px;
}

.timeline-summary div {
  border-left: 2px solid #0f766e;
  background: #f5f8f9;
  padding: 9px 11px;
}

.timeline-summary span,
.timeline-summary strong {
  display: block;
}

.timeline-summary span {
  color: #71808e;
  font-size: 0.7rem;
  font-weight: 750;
  text-transform: uppercase;
}

.timeline-summary strong {
  margin-top: 3px;
  color: #1d2a36;
}

.timeline-grid {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.worker-note {
  margin: 14px 0 0;
  border-left: 3px solid #c25b18;
  background: #fff7ed;
  color: #7c3d12;
  padding: 9px 11px;
  font-size: 0.78rem;
  line-height: 1.45;
}

.worker-row {
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.worker-label {
  color: #52606d;
  font-size: 0.76rem;
  font-weight: 750;
}

.worker-track {
  position: relative;
  height: 48px;
  overflow: hidden;
  border: 1px solid #d8e1e8;
  border-radius: 5px;
  background: repeating-linear-gradient(90deg, #f8fafb 0, #f8fafb 19%, #e8edf1 20%);
}

.timeline-block {
  position: absolute;
  top: 5px;
  bottom: 5px;
  overflow: hidden;
  border: 1px solid #0f766e;
  border-radius: 4px;
  background: #dff2ee;
  color: #0a5d56;
  padding: 4px 6px;
  white-space: nowrap;
}

.timeline-block span,
.timeline-block small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-block span {
  font-size: 0.72rem;
  font-weight: 750;
}

.timeline-block small {
  font-size: 0.65rem;
}

.timeline-empty {
  display: grid;
  min-height: 150px;
  place-items: center;
  margin-top: 16px;
  border: 1px dashed #b9c6d0;
  border-radius: 6px;
  color: #6b7885;
  padding: 20px;
  text-align: center;
}

@media (max-width: 560px) {
  .timeline-summary {
    grid-template-columns: 1fr;
  }

  .worker-row {
    grid-template-columns: 1fr;
  }
}
</style>
