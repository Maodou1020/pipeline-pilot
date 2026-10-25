<script setup>
defineProps({
  open: Boolean,
  title: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    required: true,
  },
  confirmLabel: {
    type: String,
    default: 'Confirm',
  },
  busy: Boolean,
})

defineEmits(['cancel', 'confirm'])
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-backdrop" @click.self="$emit('cancel')">
      <section
        class="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-message"
      >
        <p class="dialog-kicker">Please confirm</p>
        <h2 id="confirm-dialog-title">{{ title }}</h2>
        <p id="confirm-dialog-message">{{ message }}</p>

        <div class="dialog-actions">
          <button
            class="button button-secondary"
            type="button"
            :disabled="busy"
            @click="$emit('cancel')"
          >
            Cancel
          </button>
          <button
            class="button button-danger"
            type="button"
            :disabled="busy"
            @click="$emit('confirm')"
          >
            {{ busy ? 'Deleting...' : confirmLabel }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-backdrop {
  position: fixed;
  z-index: 100;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(17, 24, 39, 0.52);
  padding: 20px;
}

.confirm-dialog {
  width: min(100%, 430px);
  border: 1px solid #dce3e9;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 22px 60px rgba(17, 24, 39, 0.24);
  padding: 26px;
}

.dialog-kicker {
  margin: 0 0 7px;
  color: #a52a2a;
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: #17212b;
  font-size: 1.3rem;
}

#confirm-dialog-message {
  margin: 12px 0 0;
  color: #5b6673;
  line-height: 1.6;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}
</style>
