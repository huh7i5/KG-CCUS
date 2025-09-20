<template>
  <div class="about">
    <div class="hero-banner">
      <div class="ccus-visual">
        <div class="process-flow">
          <div class="step capture">
            <div class="step-icon">🏭</div>
            <div class="step-label">碳捕集</div>
          </div>
          <div class="arrow">→</div>
          <div class="step utilization">
            <div class="step-icon">⚗️</div>
            <div class="step-label">碳利用</div>
          </div>
          <div class="arrow">→</div>
          <div class="step storage">
            <div class="step-icon">🌍</div>
            <div class="step-label">碳储存</div>
          </div>
        </div>
      </div>
      <h1 class="main-title">CCUS 智能知识图谱</h1>
      <p class="subtitle">Carbon Capture, Utilization and Storage</p>
    </div>

    <div class="intro-section">
      <h2>🌱 项目简介</h2>
      <p>
        欢迎使用CCUS智能知识图谱平台！本系统是专门针对<strong>碳捕集、利用与储存（CCUS）技术</strong>领域开发的专业知识问答系统。
        我们致力于为研究者、工程师、政策制定者和相关从业人员提供一个全面、准确、智能的CCUS技术知识查询平台。
      </p>
      <p>
        通过整合1408+个专业实体、2583+个关系链接，构建了涵盖CCUS全产业链的知识图谱，结合先进的自然语言处理技术，
        为用户提供精准的技术咨询、案例分析和决策支持。
      </p>
    </div>

    <div class="features-grid">
      <div class="feature-item">
        <div class="feature-header">
          <div class="feature-icon capture-bg">🔍</div>
          <h3>专业知识检索</h3>
        </div>
        <p>基于CCUS领域知识图谱的深度信息检索，涵盖碳捕集技术、设备选型、工艺流程等专业内容。</p>
      </div>

      <div class="feature-item">
        <div class="feature-header">
          <div class="feature-icon utilization-bg">🤖</div>
          <h3>智能问答系统</h3>
        </div>
        <p>基于ChatGLM大语言模型，结合CCUS专业知识库，提供准确、详细的技术问题解答。</p>
      </div>

      <div class="feature-item">
        <div class="feature-header">
          <div class="feature-icon storage-bg">📊</div>
          <h3>可视化图谱</h3>
        </div>
        <p>直观展示CCUS技术体系中的实体关系，帮助用户理解复杂的技术关联性。</p>
      </div>

      <div class="feature-item">
        <div class="feature-header">
          <div class="feature-icon capture-bg">🏗️</div>
          <h3>案例分析</h3>
        </div>
        <p>整合国内外CCUS示范项目信息，提供投资分析、技术路线等决策参考。</p>
      </div>
    </div>
    <div class="usage-section">
      <h2>💡 使用指南</h2>
      <div class="usage-grid">
        <div class="usage-item">
          <div class="usage-icon">💬</div>
          <h4>智能问答</h4>
          <p>在<strong>问答页面</strong>输入CCUS相关问题，如"什么是燃烧后捕集技术？"、"CCUS项目投资成本如何？"等，系统将基于知识图谱提供专业解答。</p>
        </div>

        <div class="usage-item">
          <div class="usage-icon">🕸️</div>
          <h4>图谱探索</h4>
          <p>在<strong>图谱页面</strong>可视化浏览CCUS技术体系，点击节点查看详细信息，缩放查看不同层次的技术关系。</p>
        </div>

        <div class="usage-item">
          <div class="usage-icon">🔎</div>
          <h4>多维检索</h4>
          <p>支持按技术类型、应用行业、地理位置等多个维度筛选和检索相关的CCUS信息。</p>
        </div>

        <div class="usage-item">
          <div class="usage-icon">📊</div>
          <h4>案例分析</h4>
          <p>查询具体的CCUS示范项目，了解技术路线、投资规模、运营情况等详细信息。</p>
        </div>
      </div>
    </div>
    <div class="tech-section">
      <h2>⚙️ 技术架构</h2>
      <div class="tech-grid">
        <div class="tech-item">
          <div class="tech-header">
            <div class="tech-icon">🧠</div>
            <h4>ChatGLM-6B 大语言模型</h4>
          </div>
          <p>采用62亿参数的ChatGLM预训练模型，专门针对CCUS领域进行微调，确保回答的专业性和准确性。</p>
        </div>

        <div class="tech-item">
          <div class="tech-header">
            <div class="tech-icon">🕸️</div>
            <h4>CCUS专业知识图谱</h4>
          </div>
          <p>构建包含1408+实体、2583+关系的CCUS领域知识图谱，覆盖技术、项目、政策、企业等多维度信息。</p>
        </div>

        <div class="tech-item">
          <div class="tech-header">
            <div class="tech-icon">🔍</div>
            <h4>UIE信息抽取模型</h4>
          </div>
          <p>基于PaddleNLP的统一信息抽取框架，从CCUS相关文献和报告中自动抽取实体关系。</p>
        </div>

        <div class="tech-item">
          <div class="tech-header">
            <div class="tech-icon">⚡</div>
            <h4>SPN4RE关系抽取</h4>
          </div>
          <p>采用先进的关系抽取模型，识别和补全CCUS技术体系中的潜在关系，提高知识图谱完整性。</p>
        </div>

        <div class="tech-item">
          <div class="tech-header">
            <div class="tech-icon">📊</div>
            <h4>ECharts可视化</h4>
          </div>
          <p>使用ECharts图表库实现知识图谱的交互式可视化，支持节点缩放、关系探索等功能。</p>
        </div>

        <div class="tech-item">
          <div class="tech-header">
            <div class="tech-icon">🌐</div>
            <h4>Vue3 + Flask架构</h4>
          </div>
          <p>前后端分离架构，Vue3响应式前端 + Flask高性能后端，确保系统的稳定性和可扩展性。</p>
        </div>
      </div>
    </div>

    <div class="data-section">
      <h2>📈 数据规模</h2>
      <div class="data-stats">
        <div class="stat-card">
          <div class="stat-value">1408+</div>
          <div class="stat-desc">CCUS实体</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">2583+</div>
          <div class="stat-desc">关系链接</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">10</div>
          <div class="stat-desc">主要分类</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">801</div>
          <div class="stat-desc">数据句子</div>
        </div>
      </div>
    </div>
    <footer>
      <p>© 2023 <a href="http://iat.jiangnan.edu.cn/" target="_blank">A27 团队编号：2203574</a></p>
    </footer>
  </div>
</template>

<style lang="less" scoped>
.about {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  color: #333;
  font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}

// Hero Banner样式
.hero-banner {
  text-align: center;
  padding: 60px 0;
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.05), rgba(25, 118, 210, 0.05));
  border-radius: 20px;
  margin-bottom: 60px;
}

.ccus-visual {
  margin-bottom: 40px;
}

.process-flow {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
  margin-bottom: 40px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.step-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.step.capture .step-icon {
  background: linear-gradient(135deg, #2E7D32, #388E3C);
}

.step.utilization .step-icon {
  background: linear-gradient(135deg, #1976D2, #42A5F5);
}

.step.storage .step-icon {
  background: linear-gradient(135deg, #388E3C, #66BB6A);
}

.step-label {
  font-weight: 600;
  color: #555;
}

.arrow {
  font-size: 2rem;
  color: #2E7D32;
  font-weight: bold;
}

.main-title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #2E7D32, #1976D2, #388E3C);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 20px 0;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
  font-style: italic;
}

// 介绍部分
.intro-section {
  margin-bottom: 60px;
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

// 功能网格
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  margin-bottom: 60px;
}

.feature-item {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid rgba(46, 125, 50, 0.1);
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(46, 125, 50, 0.1);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.feature-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
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

// 使用指南
.usage-section {
  margin-bottom: 60px;
}

.usage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.usage-item {
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.03), rgba(25, 118, 210, 0.03));
  padding: 25px;
  border-radius: 15px;
  border: 1px solid rgba(46, 125, 50, 0.1);
}

.usage-icon {
  font-size: 2rem;
  margin-bottom: 15px;
}

// 技术架构
.tech-section {
  margin-bottom: 60px;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.tech-item {
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #2E7D32;
}

.tech-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.tech-icon {
  font-size: 1.5rem;
}

// 数据统计
.data-section {
  margin-bottom: 60px;
  text-align: center;
}

.data-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.stat-card {
  background: linear-gradient(135deg, #2E7D32, #1976D2);
  color: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(46, 125, 50, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-desc {
  font-size: 1.1rem;
  opacity: 0.9;
}

// 通用样式
h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 40px 0 30px 0;
  color: #333;
  border-left: 5px solid #2E7D32;
  padding-left: 20px;
}

h3 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

h4 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

p {
  font-size: 1rem;
  line-height: 1.7;
  color: #555;
  margin-bottom: 15px;
}

strong {
  color: #2E7D32;
  font-weight: 600;
}

footer {
  margin-top: 80px;
  padding: 40px 0;
  text-align: center;
  border-top: 1px solid rgba(46, 125, 50, 0.1);
  background: linear-gradient(135deg, rgba(46, 125, 50, 0.03), rgba(25, 118, 210, 0.03));

  p {
    color: #666;
    margin: 0;
  }

  a {
    color: #2E7D32;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .process-flow {
    flex-direction: column;
    gap: 20px;
  }

  .arrow {
    transform: rotate(90deg);
  }

  .main-title {
    font-size: 2.2rem;
  }

  .features-grid,
  .usage-grid,
  .tech-grid,
  .data-stats {
    grid-template-columns: 1fr;
  }

  .intro-section {
    padding: 25px;
  }
}
</style>
