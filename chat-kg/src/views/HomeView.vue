<template>
  <div class="welcome">
    <div class="hero-section">
      <div class="hero-content">
        <div class="logo-section">
          <div class="ccus-logo">
            <div class="co2-icon">CO₂</div>
            <div class="arrow">→</div>
            <div class="clean-icon">🌱</div>
          </div>
        </div>
        <h1 class="hero-title">{{ title }}</h1>
        <p class="hero-description">{{ description }}</p>
        <div class="feature-tags">
          <span class="tag capture">碳捕集</span>
          <span class="tag utilization">碳利用</span>
          <span class="tag storage">碳储存</span>
        </div>
      </div>
      <div class="hero-image">
        <img src="/homegraph.png" alt="CCUS知识图谱" />
        <div class="image-overlay">
          <div class="stats">
            <div class="stat-item">
              <div class="stat-number">1408+</div>
              <div class="stat-label">实体</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">2583+</div>
              <div class="stat-label">关系</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">10</div>
              <div class="stat-label">分类</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="features-section">
      <div class="feature-card">
        <div class="feature-icon capture-bg">🏭</div>
        <h3>智能问答</h3>
        <p>基于CCUS知识图谱的专业问答系统</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon utilization-bg">📊</div>
        <h3>图谱可视化</h3>
        <p>直观展示碳捕集技术关系网络</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon storage-bg">🔬</div>
        <h3>技术分析</h3>
        <p>深度解析CCUS技术发展趋势</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('CCUS 智能知识图谱')
const description = ref('基于人工智能的碳捕集、利用与储存技术知识问答平台')
const image = ref('chat-kg/src/assets/homegraph.png')
</script>

<style scoped>
.welcome {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  margin: 80px 0;
  min-height: 500px;
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.logo-section {
  margin-bottom: 30px;
}

.ccus-logo {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 24px;
  font-weight: bold;
}

.co2-icon {
  background: linear-gradient(135deg, #666, #424242);
  color: white;
  padding: 15px 20px;
  border-radius: 15px;
  font-size: 20px;
  box-shadow: 0 4px 15px rgba(66, 66, 66, 0.3);
}

.arrow {
  font-size: 30px;
  color: #2E7D32;
  font-weight: bold;
}

.clean-icon {
  font-size: 30px;
  filter: drop-shadow(0 4px 8px rgba(46, 125, 50, 0.3));
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #2E7D32, #1976D2, #388E3C);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 20px 0;
  line-height: 1.2;
}

.hero-description {
  font-size: 1.4rem;
  color: #555;
  margin-bottom: 30px;
  line-height: 1.6;
  max-width: 500px;
}

.feature-tags {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
}

.tag {
  padding: 10px 20px;
  border-radius: 25px;
  font-weight: 600;
  color: white;
  font-size: 14px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.tag:hover {
  transform: translateY(-2px);
}

.tag.capture {
  background: linear-gradient(135deg, #2E7D32, #388E3C);
}

.tag.utilization {
  background: linear-gradient(135deg, #1976D2, #42A5F5);
}

.tag.storage {
  background: linear-gradient(135deg, #388E3C, #66BB6A);
}

.hero-image {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-image img {
  width: 100%;
  max-width: 600px;
  height: auto;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(46, 125, 50, 0.1);
  transition: transform 0.3s ease;
}

.hero-image img:hover {
  transform: scale(1.02);
}

.image-overlay {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  background: linear-gradient(135deg, #2E7D32, #1976D2);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  margin-top: 5px;
}

.features-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin: 80px 0;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid rgba(46, 125, 50, 0.1);
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(46, 125, 50, 0.15);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.capture-bg {
  background: linear-gradient(135deg, #2E7D32, #388E3C);
}

.utilization-bg {
  background: linear-gradient(135deg, #1976D2, #42A5F5);
}

.storage-bg {
  background: linear-gradient(135deg, #388E3C, #66BB6A);
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 15px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 40px;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-description {
    font-size: 1.1rem;
  }

  .feature-tags {
    justify-content: center;
  }

  .stats {
    gap: 20px;
  }
}
</style>
