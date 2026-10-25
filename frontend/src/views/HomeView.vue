<script setup></script>

<template>
  <main class="home-page">
    <section class="home-intro">
      <div class="home-copy">
        <p class="eyebrow">Visual CI/CD learning workspace</p>
        <h1 class="page-title">PipelinePilot</h1>
        <p class="page-description">
          Build task dependencies, validate execution order, and understand how limited workers
          affect a deployment pipeline.
        </p>

        <div class="home-actions">
          <RouterLink class="button button-primary" to="/dashboard">Open workspace</RouterLink>
        </div>
      </div>

      <div class="pipeline-preview panel" aria-label="Example pipeline">
        <div class="preview-header">
          <span>Example pipeline</span>
          <span class="status-badge">Ready</span>
        </div>
        <ol class="preview-flow">
          <li><span>01</span><strong>Install</strong><small>2 seconds</small></li>
          <li><span>02</span><strong>Test</strong><small>4 seconds</small></li>
          <li><span>03</span><strong>Build</strong><small>3 seconds</small></li>
          <li><span>04</span><strong>Deploy</strong><small>5 seconds</small></li>
        </ol>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  min-height: calc(100vh - 67px);
  background: #f4f6f8;
}

.home-intro {
  display: grid;
  width: min(1180px, calc(100% - 40px));
  min-height: calc(100vh - 116px);
  grid-template-columns: minmax(0, 1.05fr) minmax(360px, 0.95fr);
  align-items: center;
  gap: 72px;
  margin: 0 auto;
  padding: 60px 0 90px;
}

.home-copy {
  padding: 22px 0;
}

.home-copy .page-title {
  font-size: clamp(3rem, 7vw, 5.7rem);
}

.home-copy .page-description {
  max-width: 620px;
  font-size: 1.12rem;
}

.home-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 30px;
}

.pipeline-preview {
  padding: 24px;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8ee;
  padding-bottom: 18px;
  color: #273647;
  font-weight: 750;
}

.preview-flow {
  display: grid;
  gap: 0;
  margin: 0;
  padding: 18px 0 0;
  list-style: none;
}

.preview-flow li {
  position: relative;
  display: grid;
  min-height: 62px;
  grid-template-columns: 38px 1fr auto;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #edf1f4;
}

.preview-flow li:last-child {
  border-bottom: 0;
}

.preview-flow li > span {
  color: #b45309;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.8rem;
  font-weight: 750;
}

.preview-flow strong {
  color: #1d2a36;
}

.preview-flow small {
  color: #708090;
}

@media (max-width: 820px) {
  .home-intro {
    width: min(100% - 28px, 1180px);
    min-height: auto;
    grid-template-columns: 1fr;
    gap: 28px;
    padding: 52px 0 72px;
  }
}
</style>
