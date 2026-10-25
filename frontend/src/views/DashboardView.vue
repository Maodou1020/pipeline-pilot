<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import ConfirmDialog from '@/components/ConfirmDialog.vue'
import {
  createPipeline as createPipelineRequest,
  deletePipeline as deletePipelineRequest,
  getPipelines,
} from '@/api/pipelineApi.js'
import { formatDateTime } from '@/utils/formatters.js'

const router = useRouter()

const pipelines = ref([])
const isLoading = ref(false)
const loadError = ref('')

const showCreateForm = ref(false)
const newPipelineName = ref('')
const createError = ref('')
const isCreating = ref(false)
const deletingPipelineId = ref(null)
const deleteError = ref('')
const pipelineToDelete = ref(null)

function openCreateForm() {
  showCreateForm.value = true
  createError.value = ''
}

function closeCreateForm() {
  showCreateForm.value = false
  newPipelineName.value = ''
  createError.value = ''
}

async function loadPipelines() {
  isLoading.value = true
  loadError.value = ''

  try {
    const data = await getPipelines()

    pipelines.value = data.map((pipeline) => ({
      id: pipeline.id,
      name: pipeline.name,
      status: pipeline.status === 'DRAFT' ? 'Draft' : 'Configured',
      taskCount: pipeline.task_count,
      updatedAt: formatDateTime(pipeline.updated_at),
    }))
  } catch (error) {
    loadError.value = 'Unable to load pipelines. Please make sure the server is running.'

    console.error(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadPipelines()
})

function openPipeline(pipelineId) {
  router.push({
    name: 'pipeline-editor',
    params: { id: pipelineId },
  })
}

async function createPipeline() {
  createError.value = ''

  const name = newPipelineName.value.trim()

  if (name === '') {
    createError.value = 'Please enter a pipeline name.'
    return
  }

  isCreating.value = true

  try {
    await createPipelineRequest(name)
    await loadPipelines()
    closeCreateForm()
  } catch (error) {
    createError.value = error.message
  } finally {
    isCreating.value = false
  }
}

function requestDeletePipeline(pipeline) {
  pipelineToDelete.value = pipeline
  deleteError.value = ''
}

function cancelDeletePipeline() {
  if (deletingPipelineId.value === null) {
    pipelineToDelete.value = null
  }
}

async function confirmDeletePipeline() {
  const pipeline = pipelineToDelete.value
  if (!pipeline) return

  deletingPipelineId.value = pipeline.id

  try {
    await deletePipelineRequest(pipeline.id)
    await loadPipelines()
    pipelineToDelete.value = null
  } catch (error) {
    deleteError.value = error.message
  } finally {
    deletingPipelineId.value = null
  }
}
</script>

<template>
  <main class="page-shell dashboard-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Pipeline workspace</p>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-description">
          Review saved pipelines and continue building their task flow.
        </p>
      </div>

      <button class="button button-primary" type="button" @click="openCreateForm">
        New pipeline
      </button>
    </header>
    <section v-if="showCreateForm" class="create-panel panel">
      <div class="create-heading">
        <div>
          <p class="section-kicker">New configuration</p>
          <h2>Create pipeline</h2>
        </div>

        <button class="button button-secondary" type="button" @click="closeCreateForm">
          Cancel
        </button>
      </div>

      <form class="create-form" @submit.prevent="createPipeline">
        <div class="form-field">
          <label class="field-label" for="pipeline-name"> Pipeline name </label>

          <input
            id="pipeline-name"
            v-model="newPipelineName"
            class="field-input"
            type="text"
            placeholder="e.g. Web application deployment"
          />
        </div>

        <button class="button button-primary" type="submit" :disabled="isCreating">
          {{ isCreating ? 'Creating...' : 'Create pipeline' }}
        </button>
      </form>

      <p v-if="createError" class="form-error" role="alert">
        {{ createError }}
      </p>
    </section>

    <section class="pipeline-section">
      <div class="section-heading">
        <h2>Your pipelines</h2>
        <span>{{ pipelines.length }} total</span>
      </div>

      <p v-if="deleteError" class="form-error" role="alert">
        {{ deleteError }}
      </p>

      <p v-if="isLoading" class="empty-state panel">Loading pipelines...</p>

      <p v-else-if="loadError" class="form-error" role="alert">
        {{ loadError }}
      </p>

      <div v-else-if="pipelines.length > 0" class="pipeline-grid">
        <article class="pipeline-card panel" v-for="pipeline in pipelines" :key="pipeline.id">
          <div class="card-heading">
            <h3>{{ pipeline.name }}</h3>
            <span class="status-badge">{{ pipeline.status }}</span>
          </div>
          <dl class="pipeline-meta">
            <div>
              <dt>Tasks</dt>
              <dd>{{ pipeline.taskCount }}</dd>
            </div>
            <div>
              <dt>Updated</dt>
              <dd>{{ pipeline.updatedAt }}</dd>
            </div>
          </dl>

          <div class="pipeline-card-actions">
            <button
              class="button button-secondary"
              type="button"
              @click="openPipeline(pipeline.id)"
            >
              Open pipeline
            </button>

            <button
              class="button button-danger"
              type="button"
              :disabled="deletingPipelineId === pipeline.id"
              @click="requestDeletePipeline(pipeline)"
            >
              {{ deletingPipelineId === pipeline.id ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </article>
      </div>

      <p v-else class="empty-state panel">You have not created any pipelines yet.</p>
    </section>

    <ConfirmDialog
      :open="pipelineToDelete !== null"
      title="Delete pipeline?"
      :message="
        pipelineToDelete
          ? `Delete ${pipelineToDelete.name} and all of its tasks? This cannot be undone.`
          : ''
      "
      confirm-label="Delete pipeline"
      :busy="deletingPipelineId !== null"
      @cancel="cancelDeletePipeline"
      @confirm="confirmDeletePipeline"
    />
  </main>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;
  border-bottom: 1px solid #d9e1e7;
  padding-bottom: 28px;
}

.pipeline-section {
  padding-top: 30px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-heading h2 {
  margin: 0;
  color: #1d2a36;
  font-size: 1.18rem;
}

.section-heading span {
  color: #71808e;
  font-size: 0.88rem;
}

.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.pipeline-card {
  display: flex;
  min-height: 232px;
  flex-direction: column;
  padding: 22px;
}

.card-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.card-heading h3 {
  margin: 0;
  color: #17212b;
  font-size: 1.08rem;
  line-height: 1.4;
}

.pipeline-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin: 24px 0;
}

.pipeline-meta div {
  border-left: 2px solid #d8e0e7;
  padding-left: 10px;
}

.pipeline-meta dt {
  color: #758392;
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
}

.pipeline-meta dd {
  margin: 4px 0 0;
  color: #273647;
  font-weight: 700;
}

.empty-state {
  color: #647180;
  padding: 30px;
  text-align: center;
}

@media (max-width: 700px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .page-header .button {
    align-self: flex-start;
  }

  .pipeline-grid {
    grid-template-columns: 1fr;
  }
}

.create-panel {
  margin-top: 24px;
  padding: 22px;
}

.create-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.create-heading h2 {
  margin: 0;
  color: #1d2a36;
  font-size: 1.18rem;
}

.create-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 14px;
}

@media (max-width: 600px) {
  .create-form {
    grid-template-columns: 1fr;
  }

  .create-form .button {
    width: 100%;
  }
}

.pipeline-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: auto;
}

.pipeline-card-actions .button {
  margin-top: 0;
}
</style>
