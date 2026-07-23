<script setup>
import { computed, onMounted, ref } from "vue";

const emit = defineEmits(["explore-dashboard"]);

const summary = ref(null);
const summaryUnavailable = ref(false);

onMounted(async () => {
  try {
    const response = await fetch("/data/dataset-summary.json");
    if (!response.ok) throw new Error("Dataset summary could not be loaded");
    summary.value = await response.json();
  } catch {
    summaryUnavailable.value = true;
  }
});

const stats = computed(() => {
  const coverage = summary.value?.coverage;
  return [
    { value: coverage?.observations?.toLocaleString() ?? "—", label: "state-year observations" },
    { value: coverage?.states ?? "—", label: "corn-reporting states" },
    {
      value: coverage ? coverage.endYear - coverage.startYear + 1 : "—",
      label: "years of annual data",
    },
  ];
});

const findings = computed(() => {
  const correlations = summary.value?.pooledCorrelations;
  const changes = summary.value?.nationalStateAverageChange;
  if (!correlations || !changes) return [];

  return [
    {
      number: `${changes.yieldBuPerAcre > 0 ? "+" : ""}${changes.yieldBuPerAcre.toFixed(0)}`,
      unit: "bu/acre",
      title: "Higher state-average yield",
      detail: "Difference between the 2000 and 2024 national state averages.",
    },
    {
      number: correlations.temperatureYield.toFixed(3),
      unit: "Pearson r",
      title: "Temperature–yield association",
      detail: "A very weak negative relationship across pooled state-year observations.",
    },
    {
      number: correlations.precipitationYield.toFixed(3),
      unit: "Pearson r",
      title: "Precipitation–yield association",
      detail: "Almost no linear relationship in the pooled national sample.",
    },
  ];
});

const questions = [
  {
    number: "01",
    title: "Where are yields highest?",
    detail: "Use the choropleth and rankings to compare long-run state patterns.",
  },
  {
    number: "02",
    title: "How have conditions changed?",
    detail: "Follow annual yield, temperature, and precipitation from 2000 to 2024.",
  },
  {
    number: "03",
    title: "Do relationships vary by state?",
    detail: "Select any reporting state for a focused trend and correlation view.",
  },
];
</script>

<template>
  <main class="landing-page">
    <section class="hero" aria-labelledby="project-title">
      <div class="hero-nav">
        <a class="wordmark" href="#project-title" aria-label="Climate and Corn home">
          <span class="wordmark-mark" aria-hidden="true">CC</span>
          <span>Climate + Corn</span>
        </a>
        <span class="case-study-label">Interactive data case study</span>
      </div>

      <div class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">United States · 2000–2024</p>
          <h1 id="project-title">
            Climate patterns and
            <span>corn yield, explored state by state.</span>
          </h1>
          <p class="hero-summary">
            A coordinated visualization of NOAA climate observations and USDA
            corn-yield estimates—designed to reveal trends, regional differences,
            and relationships without treating correlation as causation.
          </p>

          <div class="hero-actions">
            <button class="primary-action" @click="emit('explore-dashboard')">
              Explore the dashboard
              <span aria-hidden="true">→</span>
            </button>
            <a class="text-action" href="#methodology">Read the methodology</a>
          </div>

          <p v-if="summaryUnavailable" class="data-notice" role="status">
            The project summary is temporarily unavailable. The interactive dashboard
            can still be opened.
          </p>
        </div>

        <aside class="hero-evidence" aria-label="Dataset overview">
          <p class="evidence-label">The analytical frame</p>
          <p class="evidence-statement">
            Corn yields rose over the study period, while pooled annual climate
            variables alone show weak linear relationships with yield.
          </p>
          <div class="evidence-rule"></div>
          <p class="evidence-note">
            That tension is the starting point—not a causal conclusion.
          </p>
        </aside>
      </div>

      <dl class="stats-row" aria-label="Dataset coverage">
        <div v-for="stat in stats" :key="stat.label" class="stat-item">
          <dt>{{ stat.label }}</dt>
          <dd>{{ stat.value }}</dd>
        </div>
      </dl>
    </section>

    <section class="questions-section" aria-labelledby="questions-title">
      <div class="section-heading">
        <p class="eyebrow">Exploration guide</p>
        <h2 id="questions-title">Three questions shape the experience.</h2>
      </div>

      <div class="question-grid">
        <article v-for="question in questions" :key="question.number" class="question-card">
          <span class="question-number">{{ question.number }}</span>
          <h3>{{ question.title }}</h3>
          <p>{{ question.detail }}</p>
        </article>
      </div>
    </section>

    <section class="findings-section" aria-labelledby="findings-title">
      <div class="section-heading light-heading">
        <p class="eyebrow">Verified overview</p>
        <h2 id="findings-title">What the complete dataset shows.</h2>
        <p>
          These values are generated from the same CSV used by the dashboard, so
          the case-study copy and visual analysis stay aligned.
        </p>
      </div>

      <div class="finding-grid" aria-live="polite">
        <article v-for="finding in findings" :key="finding.title" class="finding-card">
          <div class="finding-measure">
            <strong>{{ finding.number }}</strong>
            <span>{{ finding.unit }}</span>
          </div>
          <h3>{{ finding.title }}</h3>
          <p>{{ finding.detail }}</p>
        </article>
      </div>

      <p class="finding-caveat">
        Pearson correlations pool all state-year observations. They combine
        differences between states with changes over time and should be read as
        descriptive associations only.
      </p>
    </section>

    <section id="methodology" class="method-section" aria-labelledby="method-title">
      <div class="method-intro">
        <p class="eyebrow">Methodology</p>
        <h2 id="method-title">Built from traceable public data.</h2>
        <p>
          The repository includes the collection, cleaning, merge, and validation
          scripts used to produce the dashboard dataset.
        </p>
      </div>

      <div class="source-grid">
        <article class="source-card">
          <span class="source-tag">Climate</span>
          <h3>NOAA Global Summary of the Year</h3>
          <p>
            Annual average temperature and precipitation observations are aggregated
            to state-year values from available GSOY stations.
          </p>
          <a href="https://www.ncei.noaa.gov/cdo-web/webservices/v2" target="_blank" rel="noreferrer">
            NOAA source documentation <span aria-hidden="true">↗</span>
          </a>
        </article>

        <article class="source-card">
          <span class="source-tag">Agriculture</span>
          <h3>USDA NASS Quick Stats</h3>
          <p>
            State-level corn grain yield estimates are measured in bushels per acre
            for the 41 states with complete reporting coverage.
          </p>
          <a href="https://www.nass.usda.gov/Quick_Stats/" target="_blank" rel="noreferrer">
            USDA source documentation <span aria-hidden="true">↗</span>
          </a>
        </article>

        <article class="source-card limitations-card">
          <span class="source-tag">Interpretation</span>
          <h3>Important limitations</h3>
          <p>
            Annual state averages do not control for irrigation, soil, technology,
            crop genetics, farm practices, or within-state weather variation.
          </p>
          <span class="plain-link">Association is not causation.</span>
        </article>
      </div>
    </section>

    <footer class="landing-footer">
      <p>Designed and developed by Manikanta Macha and Yashwanth Kumar Mogili.</p>
      <p>Originally created for Interactive Data Visualization, University of Iowa.</p>
    </footer>
  </main>
</template>

<style scoped>
:global(html) {
  scroll-behavior: smooth;
}

.landing-page {
  --ink: #18332b;
  --muted: #5f6f68;
  --paper: #f5f2e9;
  --paper-deep: #e9e3d3;
  --corn: #e3aa35;
  --leaf: #2f6b4f;
  min-height: 100vh;
  color: var(--ink);
  background: var(--paper);
}

.hero,
.questions-section,
.method-section,
.landing-footer {
  max-width: 1240px;
  margin: 0 auto;
  padding-left: 2rem;
  padding-right: 2rem;
}

.hero {
  padding-top: 1.5rem;
  padding-bottom: 4.5rem;
}

.hero-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 4.5rem;
}

.wordmark {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--ink);
  font-weight: 750;
  text-decoration: none;
  letter-spacing: -0.02em;
}

.wordmark-mark {
  display: grid;
  place-items: center;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 50%;
  background: var(--ink);
  color: var(--paper);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
}

.case-study-label,
.eyebrow,
.evidence-label,
.source-tag {
  font-size: 0.75rem;
  font-weight: 750;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.case-study-label {
  color: var(--muted);
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.75fr);
  gap: clamp(3rem, 8vw, 8rem);
  align-items: end;
}

.eyebrow {
  color: var(--leaf);
  margin-bottom: 1.2rem;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  max-width: 870px;
  margin-bottom: 1.75rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(3.2rem, 7vw, 6.6rem);
  font-weight: 500;
  line-height: 0.96;
  letter-spacing: -0.055em;
}

h1 span {
  color: var(--leaf);
}

.hero-summary {
  max-width: 720px;
  margin-bottom: 2rem;
  color: var(--muted);
  font-size: clamp(1.05rem, 2vw, 1.3rem);
  line-height: 1.65;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1.4rem;
}

.primary-action {
  display: inline-flex;
  align-items: center;
  gap: 1.25rem;
  padding: 0.95rem 1.25rem;
  border: 1px solid var(--ink);
  border-radius: 0;
  background: var(--ink);
  color: white;
  font-weight: 700;
  box-shadow: none;
}

.primary-action:hover {
  background: var(--leaf);
  border-color: var(--leaf);
  transform: translateY(-2px);
}

.text-action,
.source-card a {
  color: var(--ink);
  font-weight: 700;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.3rem;
}

.hero-evidence {
  padding: 1.75rem;
  border-top: 4px solid var(--corn);
  background: var(--ink);
  color: white;
}

.evidence-label {
  color: #e9c779;
}

.evidence-statement {
  margin: 1.4rem 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.45rem;
  line-height: 1.35;
}

.evidence-rule {
  width: 100%;
  height: 1px;
  margin: 1.5rem 0;
  background: rgba(255, 255, 255, 0.22);
}

.evidence-note,
.data-notice {
  color: #c7d2ce;
  line-height: 1.55;
}

.data-notice {
  color: #8b4b20;
  margin-top: 1rem;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  margin: 4.5rem 0 0;
  border-top: 1px solid #b8b5a9;
  border-bottom: 1px solid #b8b5a9;
}

.stat-item {
  display: flex;
  flex-direction: column-reverse;
  gap: 0.35rem;
  padding: 1.5rem 2rem;
  border-right: 1px solid #b8b5a9;
}

.stat-item:last-child {
  border-right: 0;
}

.stat-item dt {
  color: var(--muted);
  font-size: 0.85rem;
}

.stat-item dd {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 2.4rem;
}

.questions-section,
.method-section {
  padding-top: 7rem;
  padding-bottom: 7rem;
}

.section-heading {
  display: grid;
  grid-template-columns: minmax(0, 0.6fr) minmax(0, 1.4fr);
  gap: 3rem;
  align-items: start;
  margin-bottom: 3rem;
}

.section-heading .eyebrow {
  margin: 0;
}

.section-heading h2,
.method-intro h2 {
  margin-bottom: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2.4rem, 5vw, 4.2rem);
  font-weight: 500;
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.question-grid,
.finding-grid,
.source-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.question-card {
  min-height: 260px;
  padding: 1.75rem;
  border: 1px solid #c9c4b6;
  background: rgba(255, 255, 255, 0.35);
}

.question-number {
  display: block;
  margin-bottom: 4rem;
  color: var(--leaf);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.15rem;
}

.question-card h3,
.finding-card h3,
.source-card h3 {
  margin-bottom: 0.7rem;
  font-size: 1.2rem;
}

.question-card p,
.finding-card p,
.source-card p,
.method-intro > p:last-child {
  color: var(--muted);
  line-height: 1.6;
}

.findings-section {
  padding: 7rem max(2rem, calc((100vw - 1240px) / 2 + 2rem));
  background: var(--ink);
  color: white;
}

.light-heading {
  grid-template-columns: 0.45fr 1fr 0.85fr;
}

.light-heading .eyebrow {
  color: #e9c779;
}

.light-heading > p:last-child {
  color: #bcc9c4;
  line-height: 1.6;
}

.finding-card {
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.finding-measure {
  display: flex;
  align-items: baseline;
  gap: 0.65rem;
  margin-bottom: 3rem;
}

.finding-measure strong {
  color: #f0c661;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2.8rem, 5vw, 4.4rem);
  font-weight: 500;
}

.finding-measure span {
  color: #bcc9c4;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.finding-card p {
  color: #bcc9c4;
}

.finding-caveat {
  max-width: 850px;
  margin: 2rem 0 0;
  color: #9fb0aa;
  font-size: 0.9rem;
  line-height: 1.6;
}

.method-intro {
  max-width: 740px;
  margin-bottom: 3.5rem;
}

.method-intro > p:last-child {
  margin-top: 1.5rem;
  font-size: 1.1rem;
}

.source-card {
  display: flex;
  flex-direction: column;
  min-height: 310px;
  padding: 2rem;
  background: white;
  border-top: 4px solid var(--leaf);
}

.source-tag {
  margin-bottom: 3rem;
  color: var(--leaf);
}

.source-card a,
.plain-link {
  margin-top: auto;
}

.limitations-card {
  border-color: var(--corn);
  background: var(--paper-deep);
}

.plain-link {
  font-weight: 750;
}

.landing-footer {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  padding-top: 2.5rem;
  padding-bottom: 2.5rem;
  border-top: 1px solid #b8b5a9;
  color: var(--muted);
  font-size: 0.85rem;
}

.landing-footer p {
  margin-bottom: 0;
}

@media (max-width: 850px) {
  .hero-nav {
    padding-bottom: 3rem;
  }

  .case-study-label {
    display: none;
  }

  .hero-grid,
  .section-heading,
  .light-heading {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .hero-evidence {
    max-width: 520px;
  }

  .stats-row,
  .question-grid,
  .finding-grid,
  .source-grid {
    grid-template-columns: 1fr;
  }

  .stat-item {
    border-right: 0;
    border-bottom: 1px solid #b8b5a9;
  }

  .stat-item:last-child {
    border-bottom: 0;
  }

  .question-card {
    min-height: auto;
  }

  .question-number {
    margin-bottom: 2rem;
  }

  .landing-footer {
    flex-direction: column;
  }
}

@media (max-width: 560px) {
  .hero,
  .questions-section,
  .method-section,
  .landing-footer {
    padding-left: 1.1rem;
    padding-right: 1.1rem;
  }

  .findings-section {
    padding-left: 1.1rem;
    padding-right: 1.1rem;
  }

  .hero-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .primary-action {
    justify-content: space-between;
  }
}

@media (prefers-reduced-motion: reduce) {
  :global(html) {
    scroll-behavior: auto;
  }

  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
  }
}
</style>
