<template>
  <div class="chat-container">
    <div class="chat">
      <div ref="chatBox" class="chat-box">
        <div
          v-for="message in state.messages"
          :key="message.id"
          class="message-box"
          :class="message.type"
        >
          <img v-if="message.filetype === 'image'" :src="message.url" class="message-image" alt="">
          <p v-else style="white-space: pre-line" class="message-text">{{ message.text }}</p>
        </div>
      </div>
      <div class="input-box">
        <a-button size="large" @click="clearChat">
          <template #icon> <ClearOutlined /> </template>
        </a-button>
        <a-input
          type="text"
          class="user-input"
          v-model:value="state.inputText"
          @keydown.enter="sendMessage"
          placeholder="输入问题……"
        />
        <a-button size="large" @click="sendMessage" :disabled="!state.inputText">
          <template #icon> <SendOutlined /> </template>
        </a-button>
      </div>
    </div>
    <div class="info">
      <h1>{{ info.title }}</h1>

      <p class="description" v-if="info.description && typeof info.description === 'string'">{{ info.description }}</p>
      <div v-else-if="info.description && Array.isArray(info.description)">
        <p class="description" v-for="(desc, index) in info.description" :key="index">{{ desc }}</p>
      </div>
      <!-- 判断 info.image 是不是空，然后判断是不是数组，如果是数组则使用 v-for -->

      <img v-if="info.image && typeof info.image === 'string'" :src="info.image" class="info-image" alt="">
      <div v-else-if="info.image && Array.isArray(info.image)">
        <img v-for="(img, index) in info.image" :key="index" :src="img" class="info-image" alt="">
      </div>

      <!-- 关联图谱可视化 -->
      <p v-show="info.graph?.nodes?.length > 0"><b>关联图谱</b></p>
      <div id="lite_graph" v-show="info.graph?.nodes?.length > 0" @click="handleGraphClick"></div>

      <!-- 实体详细信息 -->
      <div v-if="selectedEntity" class="entity-details">
        <h3>{{ selectedEntity.name }}</h3>
        <p><strong>关系数量:</strong> {{ selectedEntity.total_connections }}</p>
        <div v-if="selectedEntity.relationships.length > 0">
          <h4>相关关系:</h4>
          <ul>
            <li v-for="(rel, index) in selectedEntity.relationships.slice(0, 5)" :key="index">
              <span v-if="rel.type === 'outgoing'">{{ selectedEntity.name }} → {{ rel.relation }} → {{ rel.target }}</span>
              <span v-else>{{ rel.source }} → {{ rel.relation }} → {{ selectedEntity.name }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- 建议问题 -->
      <div v-if="suggestions && suggestions.length > 0" class="suggestions">
        <h4>💡 相关问题推荐:</h4>
        <div v-for="(suggestion, index) in suggestions" :key="index" class="suggestion-item" @click="askSuggestion(suggestion)">
          {{ suggestion }}
        </div>
      </div>

      <!-- 对话摘要 -->
      <div v-if="conversationSummary" class="conversation-summary">
        <h4>📊 对话摘要:</h4>
        <p>已讨论 {{ conversationSummary.total_entities }} 个实体</p>
        <div v-if="conversationSummary.most_discussed && conversationSummary.most_discussed.length > 0">
          <strong>热门话题:</strong>
          <span v-for="(item, index) in conversationSummary.most_discussed" :key="index" class="topic-tag">
            {{ item[0] }} ({{ item[1] }}次)
          </span>
        </div>
      </div>

      <!-- 相关描述 -->
      <a-collapse v-model:activeKey="state.activeKey" v-if="info.graph?.sents?.length > 0" accordion>
        <a-collapse-panel
          v-for="(sent, index) in info.graph.sents"
          :key="index"
          :header="'相关描述 ' + (index + 1)"
          :show-arrow="false"
          ghost
        >
          <p>{{ sent }}</p>
        </a-collapse-panel>
      </a-collapse>
    </div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts';
import { reactive, ref, onMounted } from 'vue'
import { SendOutlined, ClearOutlined } from '@ant-design/icons-vue'

let myChart = null;
const chatBox = ref(null)
const state = reactive({
  history: [],
  messages: [],
  activeKey: [],
  inputText: ''
})

const default_info = {
  title: '你好，我是 ChatKG',
  description: [
    '基于特定领域知识图谱的问答系统，支持多轮对话，支持外部信息检索，你可以：',
    '1. 图谱问答：输入问题，获取相关的答案',
    '2. 多轮筛选：在对话页面，可以通过多轮对话筛选来缩小搜索范围。例如，可以根据实体、具体类别、类型等进行筛选，以快速找到所需的专业知识。',
    '3. 知识图谱可视化：在知识图谱页面，用户可以通过可视化界面直观地了解实体之间的关系。可以缩放、平移和旋转图谱以查看不同层次的关系，还可以点击实体节点查看更多详细信息。',
    '4. 实体相关信息查看：可以通过右侧知识图谱下方的相关信息查看实体所有出现的地方，帮助全面查询理解，更清晰全面。',
  ],
  image: [],
  graph: null,
}

const info = reactive({
  ...default_info
})

// 新增响应式数据
const selectedEntity = ref(null)
const suggestions = ref([])
const conversationSummary = ref(null)

const scrollToBottom = () => {
  setTimeout(() => {
    chatBox.value.scrollTop = chatBox.value.scrollHeight - chatBox.value.clientHeight
  }, 10) // 10ms 后滚动到底部
}

const appendMessage = (message, type) => {
  state.messages.push({
    id: state.messages.length + 1,
    type,
    text: message
  })
  scrollToBottom()
}


// const appendPicMessage = (pic, type) => {
//   state.messages.push({
//     id: state.messages.length + 1,
//     type,
//     filetype: "image",
//     url: pic
//   })
//   scrollToBottom()
// }

const updateLastReceivedMessage = (message, id) => {
  const lastReceivedMessage = state.messages.find((message) => message.id === id)
  if (lastReceivedMessage) {
    lastReceivedMessage.text = message
  } else {
    state.messages.push({
      id,
      type: 'received',
      text: message
    })
  }
  scrollToBottom()
}

const sendMessage = () => {
  if (state.inputText.trim()) {
    console.log('🚀 [FRONTEND] 开始发送消息:', state.inputText)
    console.log('🚀 [FRONTEND] 当前历史记录长度:', state.history.length)

    appendMessage(state.inputText, 'sent')
    appendMessage('检索中……', 'received')
    const user_input = state.inputText
    const cur_res_id = state.messages[state.messages.length - 1].id
    state.inputText = ''

    console.log('📡 [FRONTEND] 向后端发送请求 - URL: /api/chat/')
    console.log('📡 [FRONTEND] 请求数据:', {
      prompt: user_input,
      history: state.history
    })

    fetch('/api/chat/', {
      method: 'POST',
      body: JSON.stringify({
        prompt: user_input,
        history: state.history
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    }).then((response) => {
      console.log('📨 [FRONTEND] 收到响应状态:', response.status)
      console.log('📨 [FRONTEND] 响应头:', response.headers)

      if (!response.ok) {
        console.error('❌ [FRONTEND] 响应状态不正常:', response.statusText)
        updateLastReceivedMessage('服务器响应错误：' + response.statusText, cur_res_id)
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let pic
      let wiki
      let graph
      let chunkCount = 0

      console.log('🔄 [FRONTEND] 开始读取流式响应')

      // 逐步读取响应文本
      const readChunk = () => {
        return reader.read().then(({ done, value }) => {
          if (done) {
            console.log('✅ [FRONTEND] 流式读取完成')
            console.log('✅ [FRONTEND] 最终数据 - pic:', !!pic, 'wiki:', !!wiki, 'graph:', !!graph)

            // 处理完成时的最终更新
            if (pic) {
              info.image = pic
              console.log('🖼️ [FRONTEND] 更新图片数据')
            }
            if (graph) {
              info.graph = graph
              console.log('📊 [FRONTEND] 更新图谱数据，节点数:', graph.nodes?.length || 0)
            }
            if (wiki?.title) {
              info.title = wiki.title
              console.log('📰 [FRONTEND] 更新标题:', wiki.title)
            }
            if (wiki?.summary) {
              info.description = wiki.summary
              console.log('📝 [FRONTEND] 更新描述长度:', wiki.summary.length)
            }

            // 渲染图表
            renderGraphIfReady()
            return
          }

          chunkCount++
          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk

          console.log(`📦 [FRONTEND] 接收到第${chunkCount}个数据块，大小:`, chunk.length)
          console.log(`📦 [FRONTEND] 数据块内容:`, chunk.substring(0, 100) + (chunk.length > 100 ? '...' : ''))
          console.log(`📦 [FRONTEND] 当前缓冲区大小:`, buffer.length)

          const message = buffer.trim().split('\n').pop()
          console.log('🔍 [FRONTEND] 尝试解析最后一行消息:', message?.substring(0, 200) + (message?.length > 200 ? '...' : ''))

          // 尝试解析 message
          try {
            const parsedData = JSON.parse(message)
            console.log('✅ [FRONTEND] JSON解析成功')
            console.log('✅ [FRONTEND] 响应数据结构:', {
              hasUpdates: !!parsedData.updates,
              hasResponse: !!parsedData.updates?.response,
              hasHistory: !!parsedData.history,
              hasImage: !!parsedData.image,
              hasGraph: !!parsedData.graph,
              hasWiki: !!parsedData.wiki,
              hasEntityDetails: !!parsedData.entity_details,
              hasSuggestions: !!parsedData.suggestions,
              hasConversationSummary: !!parsedData.conversation_summary
            })

            if (parsedData.updates?.response) {
              console.log('💬 [FRONTEND] 更新消息内容:', parsedData.updates.response.substring(0, 100) + (parsedData.updates.response.length > 100 ? '...' : ''))
              updateLastReceivedMessage(parsedData.updates.response, cur_res_id)
            } else {
              console.warn('⚠️ [FRONTEND] 没有找到response字段')
            }

            if (parsedData.history) {
              state.history = parsedData.history
              console.log('📚 [FRONTEND] 更新历史记录，新长度:', parsedData.history.length)
            }

            pic = parsedData.image
            wiki = parsedData.wiki
            graph = parsedData.graph

            // 更新新增数据
            if (parsedData.entity_details) {
              selectedEntity.value = parsedData.entity_details[0] || null
              console.log('🏷️ [FRONTEND] 更新实体详情:', parsedData.entity_details.length, '个实体')
            }
            if (parsedData.suggestions) {
              suggestions.value = parsedData.suggestions
              console.log('💡 [FRONTEND] 更新建议问题:', parsedData.suggestions.length, '个建议')
            }
            if (parsedData.conversation_summary) {
              conversationSummary.value = parsedData.conversation_summary
              console.log('📊 [FRONTEND] 更新对话摘要')
            }

            // 每次接收到新数据时尝试渲染图表
            if (graph && graph.nodes && graph.nodes.length > 0) {
              info.graph = graph;
              console.log('📈 [FRONTEND] 尝试渲染图表，节点数:', graph.nodes.length)
              renderGraphIfReady();
            }

            buffer = ''
          } catch (e) {
            console.error('❌ [FRONTEND] JSON解析错误:', e)
            console.error('❌ [FRONTEND] 原始消息:', message)
            console.error('❌ [FRONTEND] 当前缓冲区:', buffer)
          }

          return readChunk()
        })
      }
      return readChunk()
    }).catch((error) => {
      console.error('❌ [FRONTEND] 网络请求失败:', error)
      updateLastReceivedMessage('网络连接错误：' + error.message, cur_res_id)
    })
  } else {
    console.log('⚠️ [FRONTEND] 消息为空，不发送')
  }
}

const graphOption = (graph) => {
  console.log(graph)
  graph.nodes.forEach(node => {
    node.symbolSize = 8;
    node.label = {
      show: true,
      fontSize: 10
    }
  });
  let option = {
    tooltip: {
      show: true,
      showContent: true,
      trigger: 'item',
      triggerOn: 'mousemove',
      alwaysShowContent: false,
      showDelay: 0,
      hideDelay: 200,
      enterable: false,
      position: 'right',
      confine: false,
      formatter: (params) => {
        if (params.dataType === 'node') {
          return `<strong>${params.data.name}</strong><br/>点击查看详细信息`
        } else if (params.dataType === 'edge') {
          const sourceNode = graph.nodes[params.data.source]
          const targetNode = graph.nodes[params.data.target]
          return `${sourceNode.name} → ${params.data.name} → ${targetNode.name}`
        }
        return params.data.name
      }
    },
    series: [
      {
        type: 'graph',
        draggable: true,
        layout: 'force',
        data: graph.nodes.map(function (node, idx) {
          node.id = idx;
          return node;
        }),
        links: graph.links,
        categories: graph.categories,
        roam: true,
        label: {
          position: 'right',
          fontSize: 10
        },
        force: {
          repulsion: 120,
          gravity: 0.1,
          edgeLength: 30
        },
        lineStyle: {
          color: 'source',
          curveness: 0.2,
          width: 1
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 3
          },
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          }
        }
      }
    ]
  };

  return option
}

// 处理图谱点击事件
const handleGraphClick = (event) => {
  if (myChart) {
    myChart.on('click', (params) => {
      if (params.dataType === 'node') {
        console.log('点击节点:', params.data.name)
        // 查找对应的实体详情
        const entityName = params.data.name
        fetchEntityDetails(entityName)
      }
    })
  }
}

// 获取实体详细信息
const fetchEntityDetails = async (entityName) => {
  try {
    // 这里可以发送请求获取实体详情，或从现有数据中查找
    console.log('获取实体详情:', entityName)
    // 暂时模拟数据
    selectedEntity.value = {
      name: entityName,
      total_connections: 5,
      relationships: [
        { type: 'outgoing', relation: '包含', target: '相关实体1' },
        { type: 'incoming', relation: '属于', source: '相关实体2' }
      ]
    }
  } catch (error) {
    console.error('获取实体详情失败:', error)
  }
}

// 处理建议问题点击
const askSuggestion = (suggestion) => {
  state.inputText = suggestion
  sendMessage()
}

// 动态初始化图表
const initializeChart = (callback) => {
  console.log('Attempting to initialize chart...');
  const chartDom = document.getElementById('lite_graph');

  if (!chartDom) {
    console.error('Chart container not found');
    return;
  }

  if (chartDom.clientWidth === 0 || chartDom.clientHeight === 0) {
    console.log('Chart container not ready, retrying...');
    setTimeout(() => initializeChart(callback), 100);
    return;
  }

  try {
    myChart = echarts.init(chartDom);
    handleGraphClick(); // 绑定点击事件
    console.log('Chart initialized successfully');

    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      if (myChart) {
        myChart.resize();
      }
    });

    if (callback) callback();
  } catch (e) {
    console.error('Chart initialization failed:', e);
  }
}

// 检查并渲染图表
const renderGraphIfReady = () => {
  console.log('Checking if ready to render graph...');

  if (!info.graph || !info.graph.nodes || info.graph.nodes.length === 0) {
    console.log('No graph data available');
    return;
  }

  console.log('Graph data available with', info.graph.nodes.length, 'nodes');

  // 如果图表还未初始化，先初始化
  if (!myChart) {
    console.log('Chart not initialized, initializing first...');
    initializeChart(() => {
      if (myChart && info.graph) {
        console.log('Rendering graph after initialization');
        try {
          myChart.setOption(graphOption(info.graph));
        } catch (e) {
          console.error('Graph rendering error:', e);
        }
      }
    });
  } else {
    console.log('Chart ready, rendering graph');
    try {
      myChart.setOption(graphOption(info.graph));
    } catch (e) {
      console.error('Graph rendering error:', e);
    }
  }
}


const sendDeafultMessage = () => {
  setTimeout(() => {
    appendMessage('你好？我是 ChatKG，有什么可以帮你？😊', 'received')
  }, 1000);
}

const clearChat = () => {
  state.messages = []
  state.history = []
  info.title = default_info.title
  info.description = default_info.description
  info.image = default_info.image
  info.graph = default_info.graph
  info.sents = default_info.sents
  sendDeafultMessage()
}

onMounted(() => {
  sendDeafultMessage()

  // 等待DOM完全渲染后初始化ECharts
  setTimeout(() => {
    const chartDom = document.getElementById('lite_graph');
    if (chartDom && chartDom.clientWidth > 0 && chartDom.clientHeight > 0) {
      try {
        myChart = echarts.init(chartDom);
        // 绑定图谱点击事件
        handleGraphClick()
        console.log('ECharts initialized successfully');

        // 监听窗口大小变化
        window.addEventListener('resize', () => {
          if (myChart) {
            myChart.resize();
          }
        });
      } catch (e) {
        console.error('ECharts initialization error:', e);
      }
    } else {
      console.warn('Chart container not ready, retrying...');
      // 如果DOM还没准备好，再等待一下
      setTimeout(() => {
        const retryDom = document.getElementById('lite_graph');
        if (retryDom && retryDom.clientWidth > 0 && retryDom.clientHeight > 0) {
          myChart = echarts.init(retryDom);
          handleGraphClick()

          // 监听窗口大小变化
          window.addEventListener('resize', () => {
            if (myChart) {
              myChart.resize();
            }
          });
        }
      }, 500);
    }
  }, 200);
})
</script>

<style lang="less" scoped>
// CCUS主题色彩变量
:root {
  --ccus-primary: #2E7D32;
  --ccus-secondary: #1976D2;
  --ccus-accent: #388E3C;
  --ccus-light: #F1F8E9;
  --ccus-dark: #424242;
  --ccus-gradient: linear-gradient(135deg, #2E7D32 0%, #1976D2 50%, #388E3C 100%);
}

.chat-container {
  display: flex;
  gap: 2rem;
  padding: 20px;
  background: linear-gradient(135deg, rgba(241, 248, 233, 0.3), rgba(232, 245, 232, 0.3));
  border-radius: 20px;
  margin: 20px;
  box-shadow: 0 10px 30px rgba(46, 125, 50, 0.05);
}

.chat {
  display: flex;
  width: 100%;
  max-width: 900px;
  flex-grow: 1;
  margin: 0 auto;
  flex-direction: column;
  height: calc(100vh - 180px);
  background: white;
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(46, 125, 50, 0.1);
  border: 1px solid rgba(46, 125, 50, 0.1);
  overflow: hidden;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, rgba(241, 248, 233, 0.1), white);

  // 平滑滚动
  scroll-behavior: smooth;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(241, 248, 233, 0.3);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--ccus-primary);
    border-radius: 3px;
    opacity: 0.7;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: var(--ccus-accent);
  }
}

.message-box {
  width: fit-content;
  display: inline-block;
  padding: 12px 18px;
  border-radius: 18px;
  margin: 8px 0;
  box-sizing: border-box;
  user-select: text;
  word-break: break-word;
  font-size: 15px;
  line-height: 1.6;
  font-weight: 400;
  max-width: 85%;
  position: relative;
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-box.sent {
  color: white;
  background: var(--ccus-gradient);
  align-self: flex-end;
  box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
  border-bottom-right-radius: 6px;
}

.message-box.sent::before {
  content: '';
  position: absolute;
  bottom: 0;
  right: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-left-color: var(--ccus-accent);
  border-bottom: none;
}

.message-box.received {
  color: #333;
  background: white;
  text-align: left;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(46, 125, 50, 0.1);
  border-bottom-left-radius: 6px;
}

.message-box.received::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-right-color: white;
  border-bottom: none;
}

p.message-text {
  word-wrap: break-word;
  margin-bottom: 0;
}

img.message-image {
  max-width: 300px;
  max-height: 50vh;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.input-box {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(241, 248, 233, 0.5), rgba(232, 245, 232, 0.5));
  border-top: 1px solid rgba(46, 125, 50, 0.1);
  gap: 12px;
}

input.user-input {
  flex: 1;
  height: 48px;
  padding: 12px 18px;
  background: white;
  border: 2px solid rgba(46, 125, 50, 0.2);
  border-radius: 24px;
  box-shadow: 0 4px 15px rgba(46, 125, 50, 0.05);
  font-size: 16px;
  color: #333;
  transition: all 0.3s ease;
  font-family: inherit;
}

input.user-input:focus {
  outline: none;
  border-color: var(--ccus-primary);
  box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1);
}

input.user-input::placeholder {
  color: #999;
  font-style: italic;
}

.ant-btn {
  height: 48px;
  width: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--ccus-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
  transition: all 0.3s ease;
  cursor: pointer;
}

.ant-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(46, 125, 50, 0.4);
}

.ant-btn:disabled {
  background: #ccc;
  color: #666;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

.ant-btn-icon-only {
  font-size: 18px;
}

// button:disabled {
//   // background: #ccc;
//   cursor: not-allowed;
// }

div.info {
  width: 420px;
  min-width: 420px;
  height: calc(100vh - 180px);
  overflow-y: auto;
  flex-grow: 0;
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 15px 35px rgba(46, 125, 50, 0.1);
  border: 1px solid rgba(46, 125, 50, 0.1);

  // 平滑滚动
  scroll-behavior: smooth;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(241, 248, 233, 0.3);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--ccus-primary);
    border-radius: 3px;
    opacity: 0.7;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: var(--ccus-accent);
  }

  & > h1 {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0 0 16px 0;
    color: var(--ccus-dark);
    background: var(--ccus-gradient);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  p.description {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0 0 20px 0;
    color: #555;
    background: rgba(241, 248, 233, 0.3);
    padding: 16px;
    border-radius: 12px;
    border-left: 4px solid var(--ccus-primary);
  }

  img {
    width: 100%;
    height: fit-content;
    object-fit: contain;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 16px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
  }

  img:hover {
    transform: scale(1.02);
  }

  #lite_graph {
    width: 100% !important;
    height: 320px !important;
    background: linear-gradient(135deg, rgba(241, 248, 233, 0.1), white);
    border: 2px solid rgba(46, 125, 50, 0.1);
    border-radius: 16px;
    display: block;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(46, 125, 50, 0.1);
    transition: all 0.3s ease;
  }

  #lite_graph:hover {
    border-color: var(--ccus-primary);
    box-shadow: 0 12px 30px rgba(46, 125, 50, 0.15);
  }

  // CCUS主题样式组件
  .entity-details {
    background: linear-gradient(135deg, rgba(241, 248, 233, 0.5), rgba(232, 245, 232, 0.5));
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(46, 125, 50, 0.2);
    box-shadow: 0 8px 25px rgba(46, 125, 50, 0.05);

    h3 {
      margin: 0 0 12px 0;
      color: var(--ccus-dark);
      font-size: 18px;
      font-weight: 600;
      background: var(--ccus-gradient);
      background-clip: text;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    h4 {
      margin: 16px 0 8px 0;
      color: var(--ccus-primary);
      font-size: 15px;
      font-weight: 600;
    }

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        margin-bottom: 6px;
        font-size: 14px;
        color: #555;
        line-height: 1.5;
      }
    }
  }

  .suggestions {
    margin-bottom: 20px;
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(46, 125, 50, 0.1);
    box-shadow: 0 4px 15px rgba(46, 125, 50, 0.05);

    h4 {
      margin: 0 0 12px 0;
      color: var(--ccus-dark);
      font-size: 16px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    h4::before {
      content: '💡';
      font-size: 18px;
    }

    .suggestion-item {
      background: linear-gradient(135deg, rgba(46, 125, 50, 0.1), rgba(25, 118, 210, 0.1));
      padding: 12px 16px;
      margin-bottom: 8px;
      border-radius: 12px;
      cursor: pointer;
      font-size: 14px;
      color: var(--ccus-primary);
      border: 1px solid rgba(46, 125, 50, 0.2);
      transition: all 0.3s ease;
      font-weight: 500;

      &:hover {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.15), rgba(25, 118, 210, 0.15));
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
      }
    }
  }

  .conversation-summary {
    background: linear-gradient(135deg, rgba(56, 142, 60, 0.1), rgba(102, 187, 106, 0.1));
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(56, 142, 60, 0.2);
    box-shadow: 0 4px 15px rgba(56, 142, 60, 0.05);

    h4 {
      margin: 0 0 12px 0;
      color: var(--ccus-dark);
      font-size: 16px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    h4::before {
      content: '📋';
      font-size: 18px;
    }

    p {
      margin: 0 0 12px 0;
      font-size: 14px;
      color: #555;
      line-height: 1.5;
    }

    .topic-tag {
      display: inline-block;
      background: var(--ccus-gradient);
      color: white;
      padding: 6px 12px;
      margin: 4px 6px 4px 0;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      box-shadow: 0 2px 8px rgba(46, 125, 50, 0.2);
    }
  }
}
</style>
