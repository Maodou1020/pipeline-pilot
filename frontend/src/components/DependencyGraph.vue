<script setup>
import { computed } from 'vue'

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
  },
})

const graph = computed(() => {
  const taskMap = new Map(props.tasks.map((task) => [task.id, task]))
  const levelMemo = new Map()

  function taskLevel(taskId, visiting = new Set()) {
    if (levelMemo.has(taskId)) return levelMemo.get(taskId)
    if (visiting.has(taskId)) return 0

    const task = taskMap.get(taskId)
    if (!task || task.dependencies.length === 0) {
      levelMemo.set(taskId, 0)
      return 0
    }

    const nextVisiting = new Set(visiting).add(taskId)
    const level = 1 + Math.max(...task.dependencies.map((id) => taskLevel(id, nextVisiting)))
    levelMemo.set(taskId, level)
    return level
  }

  const levels = new Map()
  for (const task of props.tasks) {
    const level = taskLevel(task.id)
    if (!levels.has(level)) levels.set(level, [])
    levels.get(level).push(task)
  }

  const maxLevel = Math.max(0, ...levels.keys())
  const maxRows = Math.max(1, ...[...levels.values()].map((items) => items.length))
  const width = Math.max(620, (maxLevel + 1) * 190)
  const height = Math.max(220, maxRows * 100 + 60)
  const positions = new Map()

  for (const [level, items] of levels) {
    items.forEach((task, index) => {
      positions.set(task.id, {
        x: 35 + level * 190,
        y: 35 + index * 100,
      })
    })
  }

  const edges = []
  for (const task of props.tasks) {
    for (const dependencyId of task.dependencies) {
      const from = positions.get(dependencyId)
      const to = positions.get(task.id)
      if (from && to) edges.push({ from, to, key: `${dependencyId}-${task.id}` })
    }
  }

  return {
    width,
    height,
    edges,
    nodes: props.tasks.map((task) => ({ ...task, ...positions.get(task.id) })),
  }
})
</script>

<template>
  <div v-if="tasks.length" class="graph-scroll" aria-label="Pipeline dependency graph">
    <svg :viewBox="`0 0 ${graph.width} ${graph.height}`" role="img">
      <defs>
        <marker
          id="arrow"
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          markerWidth="7"
          markerHeight="7"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#78909f" />
        </marker>
      </defs>

      <path
        v-for="edge in graph.edges"
        :key="edge.key"
        class="graph-edge"
        :d="`M ${edge.from.x + 140} ${edge.from.y + 29} C ${edge.from.x + 165} ${edge.from.y + 29}, ${edge.to.x - 25} ${edge.to.y + 29}, ${edge.to.x} ${edge.to.y + 29}`"
      />

      <g v-for="node in graph.nodes" :key="node.id" :transform="`translate(${node.x}, ${node.y})`">
        <rect class="graph-node" width="140" height="58" rx="6" />
        <text class="node-name" x="12" y="24">{{ node.name.slice(0, 18) }}</text>
        <text class="node-duration" x="12" y="43">{{ node.duration }}s</text>
      </g>
    </svg>
  </div>

  <div v-else class="graph-empty">Add tasks to generate the dependency graph.</div>
</template>

<style scoped>
.graph-scroll {
  overflow-x: auto;
  margin-top: 16px;
  border: 1px solid #dce3e9;
  border-radius: 6px;
  background: #f8fafb;
}

svg {
  display: block;
  width: 100%;
  min-width: 0;
}

@media (max-width: 640px) {
  svg {
    min-width: 620px;
  }
}

.graph-edge {
  fill: none;
  stroke: #78909f;
  stroke-width: 2;
  marker-end: url(#arrow);
}

.graph-node {
  fill: #ffffff;
  stroke: #0f766e;
  stroke-width: 1.5;
}

.node-name {
  fill: #17212b;
  font-size: 12px;
  font-weight: 700;
}

.node-duration {
  fill: #667482;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
}

.graph-empty {
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
</style>
