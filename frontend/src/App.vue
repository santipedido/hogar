<script setup>
import { ref } from 'vue'
import ResidentList from './components/ResidentList.vue'
import ResidentProfile from './components/ResidentProfile.vue'
import VitalSignList from './components/VitalSignList.vue'

const selectedResidentId = ref(null)
const showProfile = ref(false)
const currentView = ref('residents') // 'residents' o 'vital-signs'

function handleSelectResident(resident) {
  selectedResidentId.value = resident.id
  showProfile.value = true
}

function handleBackToList() {
  showProfile.value = false
  selectedResidentId.value = null
}

function switchView(view) {
  currentView.value = view
  showProfile.value = false
  selectedResidentId.value = null
}
</script>

<template>
  <div class="app">
    <header>
      <h1>Hogar Geriátrico</h1>
      <nav>
        <div v-if="showProfile">
          <button @click="handleBackToList" class="back-btn">
            ← Volver a la lista
          </button>
        </div>
        <div v-else class="nav-tabs">
          <button 
            @click="switchView('residents')" 
            :class="['tab-btn', { active: currentView === 'residents' }]"
          >
            👥 Residentes
          </button>
          <button 
            @click="switchView('vital-signs')" 
            :class="['tab-btn', { active: currentView === 'vital-signs' }]"
          >
            ❤️ Signos Vitales
          </button>
        </div>
      </nav>
    </header>

    <main>
      <ResidentProfile 
        v-if="showProfile && selectedResidentId"
        :residentId="selectedResidentId"
        @edit="showProfile = false"
      />
      <ResidentList 
        v-else-if="currentView === 'residents'"
        @select-resident="handleSelectResident"
      />
      <VitalSignList 
        v-else-if="currentView === 'vital-signs'"
      />
    </main>
  </div>
</template>

<style scoped>
.app {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-heading);
}

.back-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--color-background-mute);
}

.nav-tabs {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--color-background-mute);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

main {
  min-height: calc(100vh - 150px);
}

@media (max-width: 768px) {
  .app {
    padding: 0.5rem;
  }

  header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    margin-bottom: 1rem;
  }
}
</style>
