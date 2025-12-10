<script setup>
import { ref } from "vue";
import LandingPage from "./components/LandingPage.vue";
import Dashboard from "./components/Dashboard.vue";

const currentView = ref("landing");

function goToLanding() {
  currentView.value = "landing";
}
</script>

<template>
  <div class="app">
    <Transition name="fade" mode="out-in">
      <LandingPage
        v-if="currentView === 'landing'"
        @explore-dashboard="currentView = 'dashboard'"
        key="landing"
      />
      <Dashboard v-else @go-to-landing="goToLanding" key="dashboard" />
    </Transition>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  background: #ffffff;
  color: #1e293b;
  overflow-x: hidden;
}

.app {
  min-height: 100vh;
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: #f8fafc;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

* {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.tooltip,
.chart-tooltip {
  position: absolute;
  background: rgba(255, 255, 255, 0.98);
  color: #1e293b;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  backdrop-filter: blur(10px);
}

.chart-box {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.chart-box h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1e293b;
}

.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-2 {
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
}

button {
  cursor: pointer;
  font-family: inherit;
  border: none;
  outline: none;
  transition: all 0.3s ease;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

input,
select {
  font-family: inherit;
  outline: none;
}

.text-center {
  text-align: center;
}

.mt-1 {
  margin-top: 0.5rem;
}
.mt-2 {
  margin-top: 1rem;
}
.mt-3 {
  margin-top: 1.5rem;
}
.mt-4 {
  margin-top: 2rem;
}

.mb-1 {
  margin-bottom: 0.5rem;
}
.mb-2 {
  margin-bottom: 1rem;
}
.mb-3 {
  margin-bottom: 1.5rem;
}
.mb-4 {
  margin-bottom: 2rem;
}

.p-1 {
  padding: 0.5rem;
}
.p-2 {
  padding: 1rem;
}
.p-3 {
  padding: 1.5rem;
}
.p-4 {
  padding: 2rem;
}

@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>
