<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import ConfirmDialog from '@/components/ConfirmDialog.vue'
import DependencyGraph from '@/components/DependencyGraph.vue'
import SimulationTimeline from '@/components/SimulationTimeline.vue'
import {
  getPipeline,
  simulatePipeline,
  updatePipeline,
  validatePipeline,
} from '@/api/pipelineApi.js'
import {
  createTask as createTaskRequest,
  deleteTask as deleteTaskRequest,
  updateTask as updateTaskRequest,
} from '@/api/taskApi.js'

const route = useRoute()
const pipelineId = computed(() => route.params.id)

const pipelineName = ref('')
const renameValue = ref('')
const isRenaming = ref(false)
const isSavingName = ref(false)
const renameError = ref('')

const tasks = ref([])
const isLoading = ref(false)
const loadError = ref('')

const newTaskName = ref('')
const newTaskDuration = ref(1)
const newTaskDependencies = ref([])
const taskError = ref('')
const isCreatingTask = ref(false)

const editingTaskId = ref(null)
const editTaskName = ref('')
const editTaskDuration = ref(1)
const editTaskDependencies = ref([])
const editTaskError = ref('')
const isSavingTask = ref(false)

const taskToDelete = ref(null)
const deletingTaskId = ref(null)
const deleteTaskError = ref('')

const validationResult = ref(null)
const validationError = ref('')
const isValidating = ref(false)

const workerCount = ref(2)
const simulationResult = ref(null)
const simulationError = ref('')
const isSimulating = ref(false)

const canRunAnalysis = computed(() => tasks.value.length > 0)

function clearAnalysis() {
  validationResult.value = null
  validationError.value = ''
  simulationResult.value = null
  simulationError.value = ''
}

async function loadPipeline() {
  isLoading.value = true
  loadError.value = ''

  try {
    const pipeline = await getPipeline(pipelineId.value)
    pipelineName.value = pipeline.name
    renameValue.value = pipeline.name
    tasks.value = pipeline.tasks
  } catch (error) {
    loadError.value =
      error.status === 404
        ? 'This pipeline no longer exists.'
        : 'Unable to load this pipeline. Please try again.'
  } finally {
    isLoading.value = false
  }
}

function beginRename() {
  renameValue.value = pipelineName.value
  renameError.value = ''
  isRenaming.value = true
}

function cancelRename() {
  renameValue.value = pipelineName.value
  renameError.value = ''
  isRenaming.value = false
}

async function savePipelineName() {
  const name = renameValue.value.trim()
  if (!name) {
    renameError.value = 'Pipeline name cannot be empty.'
    return
  }

  isSavingName.value = true
  renameError.value = ''
  try {
    const updated = await updatePipeline(pipelineId.value, name)
    pipelineName.value = updated.name
    renameValue.value = updated.name
    isRenaming.value = false
  } catch (error) {
    renameError.value = error.message
  } finally {
    isSavingName.value = false
  }
}

function validTaskValues(name, duration) {
  if (!name.trim()) return 'Please enter a task name.'
  if (!Number.isInteger(duration) || duration < 1) {
    return 'Duration must be a positive whole number.'
  }
  return ''
}

async function addTask() {
  taskError.value = validTaskValues(newTaskName.value, newTaskDuration.value)
  if (taskError.value) return

  isCreatingTask.value = true
  try {
    await createTaskRequest(pipelineId.value, {
      name: newTaskName.value.trim(),
      duration: newTaskDuration.value,
      dependencies: [...newTaskDependencies.value],
    })
    newTaskName.value = ''
    newTaskDuration.value = 1
    newTaskDependencies.value = []
    clearAnalysis()
    await loadPipeline()
  } catch (error) {
    taskError.value = error.message
  } finally {
    isCreatingTask.value = false
  }
}

function beginEditTask(task) {
  editingTaskId.value = task.id
  editTaskName.value = task.name
  editTaskDuration.value = task.duration
  editTaskDependencies.value = [...task.dependencies]
  editTaskError.value = ''
}

function cancelEditTask() {
  editingTaskId.value = null
  editTaskError.value = ''
}

async function saveTask(taskId) {
  editTaskError.value = validTaskValues(editTaskName.value, editTaskDuration.value)
  if (editTaskError.value) return

  isSavingTask.value = true
  try {
    await updateTaskRequest(taskId, {
      name: editTaskName.value.trim(),
      duration: editTaskDuration.value,
      dependencies: [...editTaskDependencies.value],
    })
    editingTaskId.value = null
    clearAnalysis()
    await loadPipeline()
  } catch (error) {
    editTaskError.value = error.message
  } finally {
    isSavingTask.value = false
  }
}

function requestDeleteTask(task) {
  taskToDelete.value = task
  deleteTaskError.value = ''
}

function cancelDeleteTask() {
  if (deletingTaskId.value === null) taskToDelete.value = null
}

async function confirmDeleteTask() {
  if (!taskToDelete.value) return
  deletingTaskId.value = taskToDelete.value.id

  try {
    await deleteTaskRequest(taskToDelete.value.id)
    taskToDelete.value = null
    clearAnalysis()
    await loadPipeline()
  } catch (error) {
    const dependents = error.data?.dependents
    deleteTaskError.value = dependents?.length
      ? `${error.message} Used by: ${dependents.join(', ')}.`
      : error.message
    taskToDelete.value = null
  } finally {
    deletingTaskId.value = null
  }
}

function getDependencyNames(dependencyIds) {
  if (!dependencyIds.length) return 'None'
  return dependencyIds
    .map((id) => tasks.value.find((task) => task.id === id)?.name || `Unknown task (${id})`)
    .join(', ')
}

async function runValidation() {
  isValidating.value = true
  validationError.value = ''
  simulationResult.value = null

  try {
    validationResult.value = await validatePipeline(pipelineId.value)
  } catch (error) {
    validationError.value = error.message
  } finally {
    isValidating.value = false
  }
}

async function runSimulation() {
  simulationError.value = ''
  if (!Number.isInteger(workerCount.value) || workerCount.value < 1 || workerCount.value > 20) {
    simulationError.value = 'Worker count must be between 1 and 20.'
    return
  }

  isSimulating.value = true
  try {
    simulationResult.value = await simulatePipeline(pipelineId.value, workerCount.value)
    validationResult.value = await validatePipeline(pipelineId.value)
  } catch (error) {
    simulationError.value = error.data?.validation?.errors?.join(' ') || error.message
  } finally {
    isSimulating.value = false
  }
}

onMounted(loadPipeline)
</script>

<template>
  <main class="page-shell editor-page">
    <RouterLink class="back-link" :to="{ name: 'dashboard' }">
      <span aria-hidden="true">&larr;</span>
      Back to pipelines
    </RouterLink>

    <header class="editor-header">
      <div class="editor-heading">
        <p class="eyebrow">Pipeline {{ pipelineId }}</p>

        <form v-if="isRenaming" class="rename-form" @submit.prevent="savePipelineName">
          <input
            v-model="renameValue"
            class="field-input"
            aria-label="Pipeline name"
            :disabled="isSavingName"
          />
          <button class="button button-primary" type="submit" :disabled="isSavingName">
            {{ isSavingName ? 'Saving...' : 'Save' }}
          </button>
          <button
            class="button button-secondary"
            type="button"
            :disabled="isSavingName"
            @click="cancelRename"
          >
            Cancel
          </button>
        </form>

        <div v-else class="title-row">
          <h1 class="page-title">{{ pipelineName || 'Pipeline Editor' }}</h1>
          <button v-if="pipelineName" class="text-button" type="button" @click="beginRename">
            Rename
          </button>
        </div>

        <p v-if="renameError" class="form-error" role="alert">{{ renameError }}</p>
        <p class="page-description">
          Define tasks, inspect dependencies, and simulate limited CI/CD workers.
        </p>
      </div>

      <div class="header-actions">
        <button
          class="button button-secondary"
          type="button"
          :disabled="!canRunAnalysis || isValidating"
          @click="runValidation"
        >
          {{ isValidating ? 'Validating...' : 'Validate' }}
        </button>
        <label class="worker-control">
          <span>Workers</span>
          <input
            v-model.number="workerCount"
            type="number"
            min="1"
            max="20"
            :disabled="isSimulating"
          />
        </label>
        <button
          class="button button-primary"
          type="button"
          :disabled="!canRunAnalysis || isSimulating"
          @click="runSimulation"
        >
          {{ isSimulating ? 'Simulating...' : 'Run simulation' }}
        </button>
      </div>
    </header>

    <p v-if="isLoading" class="state-panel panel">Loading pipeline...</p>
    <section v-else-if="loadError" class="state-panel panel error-state">
      <p>{{ loadError }}</p>
      <RouterLink class="button button-secondary" :to="{ name: 'dashboard' }"
        >Return to dashboard</RouterLink
      >
    </section>

    <div v-else class="editor-layout">
      <section class="task-workspace">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Configuration</p>
            <h2>Tasks</h2>
          </div>
          <span>{{ tasks.length }} total</span>
        </div>

        <form class="task-form panel" @submit.prevent="addTask">
          <div class="form-field task-name-field">
            <label class="field-label" for="task-name">Task name</label>
            <input
              id="task-name"
              v-model="newTaskName"
              class="field-input"
              type="text"
              placeholder="e.g. Deploy application"
              :disabled="isCreatingTask"
            />
          </div>
          <div class="form-field duration-field">
            <label class="field-label" for="task-duration">Duration (seconds)</label>
            <input
              id="task-duration"
              v-model.number="newTaskDuration"
              class="field-input"
              type="number"
              min="1"
              :disabled="isCreatingTask"
            />
          </div>
          <fieldset v-if="tasks.length" class="dependency-field" :disabled="isCreatingTask">
            <legend>Dependencies</legend>
            <label v-for="task in tasks" :key="task.id" class="dependency-option">
              <input v-model="newTaskDependencies" type="checkbox" :value="task.id" />
              {{ task.name }}
            </label>
          </fieldset>
          <button
            class="button button-primary add-task-button"
            type="submit"
            :disabled="isCreatingTask"
          >
            {{ isCreatingTask ? 'Adding task...' : 'Add task' }}
          </button>
          <p v-if="taskError" class="form-error" role="alert">{{ taskError }}</p>
        </form>

        <p v-if="deleteTaskError" class="form-error standalone-error" role="alert">
          {{ deleteTaskError }}
        </p>

        <div v-if="tasks.length" class="task-list">
          <article v-for="task in tasks" :key="task.id" class="task-card panel">
            <form
              v-if="editingTaskId === task.id"
              class="edit-task-form"
              @submit.prevent="saveTask(task.id)"
            >
              <div>
                <label class="field-label" :for="`edit-name-${task.id}`">Task name</label
                ><input
                  :id="`edit-name-${task.id}`"
                  v-model="editTaskName"
                  class="field-input"
                  :disabled="isSavingTask"
                />
              </div>
              <div>
                <label class="field-label" :for="`edit-duration-${task.id}`">Duration</label
                ><input
                  :id="`edit-duration-${task.id}`"
                  v-model.number="editTaskDuration"
                  class="field-input"
                  type="number"
                  min="1"
                  :disabled="isSavingTask"
                />
              </div>
              <fieldset class="dependency-field" :disabled="isSavingTask">
                <legend>Dependencies</legend>
                <label
                  v-for="candidate in tasks.filter((item) => item.id !== task.id)"
                  :key="candidate.id"
                  class="dependency-option"
                >
                  <input v-model="editTaskDependencies" type="checkbox" :value="candidate.id" />
                  {{ candidate.name }}
                </label>
              </fieldset>
              <p v-if="editTaskError" class="form-error" role="alert">{{ editTaskError }}</p>
              <div class="form-actions">
                <button class="button button-primary" type="submit" :disabled="isSavingTask">
                  {{ isSavingTask ? 'Saving...' : 'Save task' }}</button
                ><button
                  class="button button-secondary"
                  type="button"
                  :disabled="isSavingTask"
                  @click="cancelEditTask"
                >
                  Cancel
                </button>
              </div>
            </form>

            <template v-else>
              <div class="task-card-main">
                <div class="task-number">{{ String(task.id).slice(-2) }}</div>
                <div>
                  <div class="task-heading">
                    <h3>{{ task.name }}</h3>
                    <span class="status-badge">{{ task.status }}</span>
                  </div>
                  <p class="task-dependencies">
                    Depends on: {{ getDependencyNames(task.dependencies) }}
                  </p>
                </div>
              </div>
              <div class="task-actions">
                <span class="duration-value">{{ task.duration }}s</span>
                <button class="button button-secondary" type="button" @click="beginEditTask(task)">
                  Edit
                </button>
                <button class="button button-danger" type="button" @click="requestDeleteTask(task)">
                  Delete
                </button>
              </div>
            </template>
          </article>
        </div>
        <p v-else class="empty-state panel">
          No tasks yet. Add the first stage of this pipeline above.
        </p>
      </section>

      <aside class="visualisation-column">
        <section class="visual-panel panel">
          <p class="section-kicker">Structure</p>
          <h2>Dependency graph</h2>
          <DependencyGraph :tasks="tasks" />
        </section>

        <section class="visual-panel panel validation-panel">
          <p class="section-kicker">Quality gate</p>
          <h2>Validation</h2>
          <p v-if="validationError" class="form-error" role="alert">{{ validationError }}</p>
          <template v-else-if="validationResult">
            <p :class="['validation-status', validationResult.valid ? 'is-valid' : 'is-invalid']">
              {{ validationResult.valid ? 'Pipeline is valid' : 'Pipeline needs attention' }}
            </p>
            <ul v-if="validationResult.errors.length">
              <li v-for="error in validationResult.errors" :key="error">{{ error }}</li>
            </ul>
            <ol v-else class="execution-order">
              <li v-for="task in validationResult.execution_order" :key="task.id">
                {{ task.name }}
              </li>
            </ol>
          </template>
          <p v-else class="panel-hint">
            Run validation to check missing dependencies, cycles, and execution order.
          </p>
        </section>

        <section class="visual-panel panel timeline-panel">
          <p class="section-kicker">Simulation</p>
          <h2>Worker timeline</h2>
          <p v-if="simulationError" class="form-error" role="alert">{{ simulationError }}</p>
          <SimulationTimeline :result="simulationResult" />
        </section>
      </aside>
    </div>

    <ConfirmDialog
      :open="taskToDelete !== null"
      title="Delete task?"
      :message="
        taskToDelete
          ? `Delete ${taskToDelete.name}? Tasks that depend on it must be updated first.`
          : ''
      "
      confirm-label="Delete task"
      :busy="deletingTaskId !== null"
      @cancel="cancelDeleteTask"
      @confirm="confirmDeleteTask"
    />
  </main>
</template>

<style scoped>
.back-link {
  display: inline-flex;
  min-height: 36px;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  border: 1px solid #d3dde5;
  border-radius: 5px;
  background: #fff;
  color: #52606d;
  padding: 7px 11px;
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
}
.back-link:hover {
  border-color: #9eacb8;
  background: #f5f7f9;
  color: #1d2a36;
}
.editor-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 30px;
  border-bottom: 1px solid #d9e1e7;
  padding-bottom: 28px;
}
.editor-heading {
  min-width: 0;
}
.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.text-button {
  border: 0;
  background: transparent;
  color: #0f766e;
  padding: 6px;
  font-weight: 700;
}
.rename-form {
  display: grid;
  max-width: 620px;
  grid-template-columns: minmax(220px, 1fr) auto auto;
  gap: 8px;
}
.header-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: flex-end;
  gap: 10px;
}
.worker-control {
  display: grid;
  gap: 5px;
  color: #52606d;
  font-size: 0.75rem;
  font-weight: 750;
}
.worker-control input {
  width: 82px;
  min-height: 42px;
  border: 1px solid #cbd5df;
  border-radius: 6px;
  padding: 8px;
}
.button:disabled,
fieldset:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}
.editor-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.8fr);
  gap: 22px;
  padding-top: 30px;
}
.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 14px;
}
.section-heading h2,
.visual-panel h2 {
  margin: 0;
  color: #1d2a36;
  font-size: 1.18rem;
}
.section-heading > span {
  color: #71808e;
  font-size: 0.86rem;
}
.section-kicker {
  margin: 0 0 4px;
  color: #b45309;
  font-size: 0.72rem;
  font-weight: 750;
  text-transform: uppercase;
}
.task-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px;
  gap: 18px;
  padding: 22px;
}
.dependency-field {
  display: flex;
  grid-column: 1 / -1;
  flex-wrap: wrap;
  gap: 8px;
  border: 0;
  margin: 0;
  padding: 0;
}
.dependency-field legend {
  width: 100%;
  margin-bottom: 7px;
  color: #263341;
  font-size: 0.88rem;
  font-weight: 700;
}
.dependency-option {
  display: inline-flex;
  min-height: 36px;
  align-items: center;
  gap: 7px;
  border: 1px solid #d3dde5;
  border-radius: 5px;
  background: #f8fafb;
  color: #43515f;
  padding: 6px 10px;
  font-size: 0.84rem;
}
.dependency-option:has(input:checked) {
  border-color: #67a69f;
  background: #eaf5f3;
  color: #0f665e;
}
.dependency-option input {
  width: 16px;
  height: 16px;
  accent-color: #0f766e;
}
.add-task-button {
  justify-self: start;
}
.form-error {
  grid-column: 1 / -1;
  margin: 0;
  border-left: 3px solid #b42318;
  background: #fff1f0;
  color: #8f1d14;
  padding: 10px 12px;
  font-size: 0.9rem;
}
.standalone-error {
  margin-top: 14px;
}
.task-list {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}
.task-card {
  display: flex;
  min-height: 108px;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px;
}
.task-card-main {
  display: grid;
  min-width: 0;
  grid-template-columns: 42px minmax(0, 1fr);
  align-items: center;
  gap: 13px;
}
.task-number {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid #cad5de;
  border-radius: 6px;
  background: #edf2f5;
  color: #516170;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  font-weight: 750;
}
.task-heading {
  display: flex;
  align-items: center;
  gap: 10px;
}
.task-heading h3 {
  overflow-wrap: anywhere;
  margin: 0;
  color: #17212b;
  font-size: 1rem;
}
.task-dependencies {
  margin: 8px 0 0;
  color: #667482;
  font-size: 0.84rem;
  line-height: 1.45;
}
.task-actions {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 9px;
}
.duration-value {
  color: #354555;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.88rem;
  font-weight: 750;
}
.edit-task-form {
  display: grid;
  width: 100%;
  grid-template-columns: minmax(0, 1fr) 130px;
  gap: 14px;
}
.edit-task-form .form-actions {
  display: flex;
  grid-column: 1 / -1;
  gap: 8px;
}
.visualisation-column {
  display: grid;
  align-content: start;
  gap: 16px;
}
.visual-panel {
  min-width: 0;
  padding: 20px;
}
.panel-hint {
  margin: 15px 0 0;
  color: #6b7885;
  font-size: 0.86rem;
  line-height: 1.55;
}
.validation-status {
  margin: 15px 0 0;
  border-left: 3px solid;
  padding: 10px 12px;
  font-weight: 750;
}
.validation-status.is-valid {
  border-color: #0f766e;
  background: #eaf5f3;
  color: #0f665e;
}
.validation-status.is-invalid {
  border-color: #b42318;
  background: #fff1f0;
  color: #8f1d14;
}
.validation-panel ul,
.execution-order {
  margin: 12px 0 0;
  color: #52606d;
  padding-left: 22px;
  line-height: 1.7;
}
.state-panel {
  margin-top: 22px;
  padding: 30px;
  text-align: center;
}
.error-state {
  color: #8f1d14;
}
.error-state .button {
  margin-top: 12px;
}
.empty-state {
  color: #647180;
  margin-top: 16px;
  padding: 28px;
  text-align: center;
}
@media (max-width: 980px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }
  .visualisation-column {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 700px) {
  .editor-header {
    align-items: stretch;
    flex-direction: column;
  }
  .header-actions {
    justify-content: flex-start;
  }
  .rename-form,
  .task-form,
  .edit-task-form {
    grid-template-columns: 1fr;
  }
  .dependency-field,
  .form-error,
  .edit-task-form .form-actions {
    grid-column: 1;
  }
  .task-card {
    align-items: stretch;
    flex-direction: column;
  }
  .task-actions {
    justify-content: space-between;
    border-top: 1px solid #e3e9ee;
    padding-top: 12px;
  }
}
</style>
