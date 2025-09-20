<script setup>
import { KeepAlive } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

// 打印当前页面的路由信息，使用 vue3 的 setup composition API
const route = useRoute()
console.log(route)



</script>

<template>
  <header class="header">
    <nav class="nav">
      <RouterLink to="/" class="nav-item" active-class="active">主页</RouterLink>
      <RouterLink to="/chat" class="nav-item" active-class="active">问答</RouterLink>
      <RouterLink to="/kg" class="nav-item" active-class="active">图谱</RouterLink>
      <RouterLink to="/about" class="nav-item" active-class="active">关于</RouterLink>
    </nav>
  </header>

    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
</template>

<style lang="less" scoped>
// CCUS主题色彩变量
:root {
  --ccus-primary: #2E7D32;      // 深绿色 - 环保主色
  --ccus-secondary: #1976D2;    // 蓝色 - 科技感
  --ccus-accent: #388E3C;       // 亮绿色 - 清洁能源
  --ccus-dark: #424242;         // 深灰色 - 工业感
  --ccus-light: #F1F8E9;        // 浅绿色背景
  --ccus-hover: #E8F5E8;        // 悬停色
  --ccus-gradient: linear-gradient(135deg, #2E7D32 0%, #1976D2 50%, #388E3C 100%);
}

.header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 40px 0;
  background: var(--ccus-gradient);
  padding: 20px 0;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(46, 125, 50, 0.1);
  margin: 20px auto;
  width: 90%;
  max-width: 1200px;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  height: 45px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 25px;
  padding: 0 20px;
  backdrop-filter: blur(10px);
}

.nav-item {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  background-color: transparent;
  color: var(--ccus-dark);
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin: 0 8px;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--ccus-gradient);
  transition: left 0.3s ease;
  z-index: -1;
  border-radius: 20px;
}

.nav-item:hover {
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(46, 125, 50, 0.3);
}

.nav-item:hover::before {
  left: 0;
}

.nav-item.active {
  font-weight: bold;
  color: white;
  background: var(--ccus-gradient);
  box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background-color: var(--ccus-accent);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--ccus-accent);
}

// 全局CCUS主题样式
:global(body) {
  background: linear-gradient(45deg, #F1F8E9 0%, #E8F5E8 50%, #F1F8E9 100%);
  min-height: 100vh;
  font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}

:global(#app) {
  background: transparent;
}
</style>
