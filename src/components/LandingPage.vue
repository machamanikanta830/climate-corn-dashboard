<script setup>
import { ref } from "vue";

const emit = defineEmits(["explore-dashboard"]);

const stats = [
  { value: "41", label: "U.S. States" },
  { value: "25", label: "Years of Data" },
  { value: "1,025", label: "Data Points" },
  { value: "2", label: "Climate Factors" },
];

const features = [
  {
    icon: "📊",
    title: "Statistical Analysis",
    description:
      "Correlation analysis, trend detection, and p-values for scientific rigor",
  },
  {
    icon: "🗺️",
    title: "Geographic Insights",
    description:
      "Interactive choropleth maps showing regional patterns across America",
  },
  {
    icon: "🔗",
    title: "Cross-Chart Interactions",
    description:
      "Hover and click to explore connections across multiple visualizations",
  },
  {
    icon: "📈",
    title: "Multiple Views",
    description:
      "8+ visualization types including treemaps, parallel coordinates, and more",
  },
  {
    icon: "🌡️",
    title: "Climate Tracking",
    description:
      "Temperature and precipitation data from NOAA spanning 2000-2024",
  },
  {
    icon: "🌽",
    title: "Agricultural Impact",
    description:
      "USDA corn yield data showing real-world effects of climate change",
  },
];
</script>

<template>
  <div class="landing-page">
    <!-- Animated Background -->
    <div class="animated-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <!-- Main Content -->
    <div class="content-wrapper">
      <!-- Hero Section -->
      <section class="hero">
        <div class="hero-badge">
          <span class="badge-icon">🎓</span>
          CS:4980 Interactive Data Visualization • University of Iowa
        </div>

        <h1 class="hero-title">
          Climate Impact on<br />
          <span class="highlight">U.S. Corn Production</span>
        </h1>

        <p class="hero-subtitle">
          An interactive exploration of how temperature and precipitation
          patterns affect agricultural yields across America from 2000 to 2024
        </p>

        <!-- Stats Row -->
        <div class="stats-row">
          <div v-for="stat in stats" :key="stat.label" class="stat-card">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>

        <!-- CTA Buttons -->
        <div class="cta-buttons">
          <button class="btn-primary" @click="emit('explore-dashboard')">
            <span class="btn-icon">📊</span>
            Explore Dashboard
            <span class="btn-arrow">→</span>
          </button>
          <a href="#features" class="btn-secondary">
            Learn More
            <span class="btn-arrow">↓</span>
          </a>
        </div>
      </section>

      <!-- Features Section -->
      <section id="features" class="features">
        <h2 class="section-title">What You'll Discover</h2>

        <div class="features-grid">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="feature-card"
          >
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
      </section>

      <!-- Data Sources Section -->
      <section class="data-sources">
        <h2 class="section-title">Powered by Trusted Data</h2>

        <div class="sources-grid">
          <div class="source-card">
            <div class="source-logo">
              <div class="logo-placeholder noaa">NOAA</div>
            </div>
            <h3 class="source-name">
              National Oceanic and Atmospheric Administration
            </h3>
            <p class="source-description">
              Climate data from the Global Summary of the Year (GSOY) dataset,
              providing state-level temperature and precipitation measurements
            </p>
          </div>

          <div class="source-card">
            <div class="source-logo">
              <div class="logo-placeholder usda">USDA</div>
            </div>
            <h3 class="source-name">U.S. Department of Agriculture</h3>
            <p class="source-description">
              Corn yield statistics from NASS Quick Stats, tracking agricultural
              productivity across all major corn-producing states
            </p>
          </div>
        </div>
      </section>

      <!-- Key Findings Preview -->
      <section class="findings-preview">
        <h2 class="section-title">Preliminary Findings</h2>

        <div class="findings-container">
          <div class="finding-item">
            <div class="finding-icon">🌡️</div>
            <div class="finding-content">
              <h3>Temperature Trends</h3>
              <p>
                Average temperatures have
                <strong>increased by ~2°F</strong> over the 25-year period, with
                significant regional variation
              </p>
            </div>
          </div>

          <div class="finding-item">
            <div class="finding-icon">🌽</div>
            <div class="finding-content">
              <h3>Yield Improvements</h3>
              <p>
                Despite climate pressures, corn yields have
                <strong>improved by ~30 bu/acre</strong> through technological
                advances
              </p>
            </div>
          </div>

          <div class="finding-item">
            <div class="finding-icon">📉</div>
            <div class="finding-content">
              <h3>Negative Correlation</h3>
              <p>
                Higher temperatures show
                <strong>negative correlation (r ≈ -0.3)</strong> with yield,
                indicating heat stress effects
              </p>
            </div>
          </div>

          <div class="finding-item">
            <div class="finding-icon">💧</div>
            <div class="finding-content">
              <h3>Precipitation Benefits</h3>
              <p>
                Adequate rainfall shows
                <strong>positive correlation (r ≈ +0.2)</strong> with higher
                crop productivity
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="landing-footer">
        <p class="footer-text">
          Created by Manikanta Macha & Yashwanth Kumar Mogili
        </p>
        <p class="footer-text">Interactive Data Visualization • Fall 2025</p>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  color: white;
  overflow-x: hidden;
  position: relative;
}

/* Animated Background */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s infinite ease-in-out;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  bottom: -100px;
  right: -100px;
  animation-delay: 5s;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 10s;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(50px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-50px, 50px) scale(0.9);
  }
}

/* Content */
.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Hero Section */
.hero {
  text-align: center;
  padding: 4rem 0 6rem;
  animation: fadeInUp 0.8s ease-out;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 2rem;
  animation: fadeInUp 0.8s ease-out 0.2s backwards;
}

.badge-icon {
  font-size: 1.2rem;
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 1.5rem 0;
  animation: fadeInUp 0.8s ease-out 0.4s backwards;
  letter-spacing: -1px;
}

.highlight {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #475569;
  max-width: 700px;
  margin: 0 auto 3rem;
  animation: fadeInUp 0.8s ease-out 0.6s backwards;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
  animation: fadeInUp 0.8s ease-out 0.8s backwards;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

/* CTA Buttons */
.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  animation: fadeInUp 0.8s ease-out 1s backwards;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-icon {
  font-size: 1.3rem;
}

.btn-arrow {
  transition: transform 0.3s ease;
}

.btn-primary:hover .btn-arrow {
  transform: translateX(5px);
}

.btn-secondary:hover .btn-arrow {
  transform: translateY(3px);
}

/* Features Section */
.features {
  padding: 6rem 0;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.feature-description {
  color: #64748b;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Data Sources */
.data-sources {
  padding: 6rem 0;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.source-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: center;
}

.source-logo {
  margin-bottom: 1.5rem;
}

.logo-placeholder {
  width: 100px;
  height: 100px;
  margin: 0 auto;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
}

.noaa {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
}

.usda {
  background: linear-gradient(135deg, #10b981, #059669);
}

.source-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1e293b;
}

.source-description {
  color: #64748b;
  line-height: 1.6;
}

/* Findings Preview */
.findings-preview {
  padding: 6rem 0;
}

.findings-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.finding-item {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  transition: all 0.3s ease;
}

.finding-item:hover {
  transform: translateX(5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

.finding-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.finding-content h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.finding-content p {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}

.finding-content strong {
  color: #60a5fa;
}

/* Footer */
.landing-footer {
  text-align: center;
  padding: 3rem 0 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 4rem;
}

.footer-text {
  color: #64748b;
  margin: 0.5rem 0;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .cta-buttons {
    flex-direction: column;
    width: 100%;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }

  .features-grid,
  .sources-grid,
  .findings-container {
    grid-template-columns: 1fr;
  }
}
</style>
