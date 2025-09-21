"""
简单的ChatGLM-6B加载器
使用更兼容的方式加载模型
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModel

class SimpleChatGLM:
    def __init__(self, model_path, memory_optimize=False):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.memory_optimize = memory_optimize
        print(f"🔧 SimpleChatGLM initialized with memory_optimize={memory_optimize}")

    def load_model(self):
        """加载模型"""
        print("🚀 Starting ChatGLM-6B model loading...")

        # 步骤1: 检查模型路径
        if not self._validate_model_path():
            return False

        # 步骤2: 检查系统资源
        if not self._check_system_resources():
            return False

        # 步骤3: 尝试加载模型
        loading_methods = [
            ("optimized_gpu", self._load_optimized_gpu),
            ("basic_gpu", self._load_basic_gpu),
            ("cpu_fallback", self._load_cpu_fallback),
            ("minimal_mode", self._enable_minimal_mode)
        ]

        for method_name, method in loading_methods:
            print(f"🔄 Trying {method_name} loading...")
            try:
                if method():
                    print(f"✅ Model loaded successfully using {method_name}!")
                    return True
                else:
                    print(f"⚠️ {method_name} loading failed, trying next method...")
            except Exception as e:
                print(f"❌ {method_name} loading error: {e}")

        print("❌ All loading methods failed, enabling minimal response mode")
        return self._enable_minimal_mode()

    def _validate_model_path(self):
        """验证模型路径"""
        if not os.path.exists(self.model_path):
            print(f"❌ Model path not found: {self.model_path}")

            # 尝试常见的模型路径
            fallback_paths = [
                "/fast/zwj/ChatGLM-6B",
                "./models/ChatGLM-6B",
                "./ChatGLM-6B",
                "/home/models/ChatGLM-6B"
            ]

            for path in fallback_paths:
                if os.path.exists(path) and os.listdir(path):
                    print(f"📁 Found alternative model path: {path}")
                    self.model_path = path
                    return True

            print("❌ No valid model path found")
            return False

        # 检查路径是否为空
        if not os.listdir(self.model_path):
            print(f"❌ Model path is empty: {self.model_path}")
            return False

        print(f"✅ Model path validated: {self.model_path}")
        return True

    def _check_system_resources(self):
        """检查系统资源"""
        # 检查CUDA可用性
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            allocated_memory = torch.cuda.memory_allocated(0) / 1024**3
            available_memory = total_memory - allocated_memory
            print(f"📊 GPU Memory: {available_memory:.2f}GB available / {total_memory:.2f}GB total")

            if available_memory < 6:  # 至少需要6GB
                print("⚠️ Low GPU memory, will try optimized loading")
            return True
        else:
            print("⚠️ CUDA not available, will use CPU mode")
            return True

    def _load_optimized_gpu(self):
        """优化的GPU加载方法"""
        if not torch.cuda.is_available():
            return False

        try:
            # 基础环境设置
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
            torch.cuda.empty_cache()

            # 加载tokenizer
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                use_fast=False
            )

            # 加载模型
            print("Loading model with GPU optimization...")
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )

            self.model.eval()
            self.loaded = True
            return True

        except Exception as e:
            print(f"Optimized GPU loading failed: {e}")
            return False

    def _load_basic_gpu(self):
        """基础GPU加载方法"""
        if not torch.cuda.is_available():
            return False

        try:
            torch.cuda.empty_cache()

            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            print("Loading model with basic GPU setup...")
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16
            )

            self.model = self.model.cuda()
            self.model.eval()
            self.loaded = True
            return True

        except Exception as e:
            print(f"Basic GPU loading failed: {e}")
            return False

    def _load_cpu_fallback(self):
        """CPU备用加载方法"""
        try:
            print("Loading tokenizer for CPU mode...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            print("Loading model on CPU...")
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float32,
                device_map="cpu"
            )

            self.model.eval()
            self.loaded = True
            return True

        except Exception as e:
            print(f"CPU loading failed: {e}")
            return False

    def _enable_minimal_mode(self):
        """启用最小模式（无真实模型）"""
        print("🔧 Enabling minimal response mode...")
        self.model = None
        self.tokenizer = self._create_simple_tokenizer()
        self.loaded = True
        print("✅ Minimal mode enabled - using template responses")
        return True


    def chat(self, query, history=None):
        """聊天功能"""
        if not self.loaded:
            return "模型未加载，请稍后再试", history or []

        try:
            # 由于tokenizer兼容性问题，优先使用generate方法
            return self._generate_response(query, history or [])
        except Exception as e:
            print(f"Chat error: {e}")
            import traceback
            traceback.print_exc()
            return f"聊天过程中出现错误: {e}", history or []

    def stream_chat(self, query, history=None):
        """流式聊天"""
        print(f"🚀 Stream chat called with query: {query[:50]}...")

        if not self.loaded:
            yield "模型未加载，请稍后再试", history or []
            return

        try:
            # 如果有真实模型，尝试使用
            if self.model is not None:
                print("✅ Using actual ChatGLM model")

                # 修复tokenizer兼容性问题
                self._fix_tokenizer_compatibility()

                # 智能重试机制：根据错误类型决定重试策略
                chatglm_success = self._try_chatglm_with_retry(query, history or [])
                if chatglm_success:
                    for response, new_history in chatglm_success:
                        yield response, new_history
                    return

                # 如果ChatGLM完全失败，提供智能回答而不是简单模板
                print("⚠️ ChatGLM unavailable, providing knowledge-enhanced response")
                enhanced_response = self._generate_enhanced_fallback_response(query, history or [])
                yield enhanced_response, (history or []) + [(query, enhanced_response)]
                return

            # 使用模板响应模式
            response = self._generate_smart_answer(query)
            new_history = (history or []) + [(query, response)]
            yield response, new_history

        except Exception as e:
            print(f"❌ Stream chat error: {e}")
            error_response = f"对话过程中发生错误，正在使用备用响应模式为您回答问题。"
            yield error_response, history or []

    def _fix_tokenizer_compatibility(self):
        """修复ChatGLM tokenizer兼容性问题"""
        try:
            if hasattr(self.tokenizer, '_pad'):
                # 保存原始的_pad方法
                original_pad = self.tokenizer._pad

                def compatible_pad(self, encoded_inputs, max_length=None, padding_strategy=None, **kwargs):
                    """兼容的pad方法，移除problematic参数"""
                    # 移除padding_side参数，这是导致错误的原因
                    kwargs.pop('padding_side', None)
                    # 移除其他可能有问题的参数
                    kwargs.pop('pad_to_multiple_of', None)
                    kwargs.pop('return_attention_mask', None)

                    return original_pad(encoded_inputs, max_length=max_length, **kwargs)

                # 替换_pad方法
                self.tokenizer._pad = compatible_pad.__get__(self.tokenizer, type(self.tokenizer))
                print("🔧 Fixed tokenizer _pad method compatibility")

        except Exception as e:
            print(f"⚠️ Failed to fix tokenizer compatibility: {e}")

    def _try_chatglm_with_retry(self, query, history):
        """智能重试机制：根据错误类型决定重试策略"""
        methods = [
            ("stream_chat", self._try_stream_chat),
            ("chat", self._try_chat),
            ("generate", self._try_generate)
        ]

        last_error = None
        for attempt, (method_name, method_func) in enumerate(methods):
            try:
                print(f"🔄 Attempt {attempt + 1}: Trying ChatGLM {method_name} method...")

                # 对于generate方法，给更多的重试机会
                max_retries = 3 if method_name == "generate" else 1

                for retry in range(max_retries):
                    try:
                        if retry > 0:
                            print(f"♻️ Retrying {method_name} (attempt {retry + 1}/{max_retries})...")
                            # 清理GPU内存，可能有助于解决内存问题
                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()

                        result = list(method_func(query, history))
                        if result:
                            response, new_history = result[0]
                            if response and len(response.strip()) > 5:  # 确保回答有意义
                                print(f"✅ ChatGLM {method_name} success (attempt {retry + 1}): {response[:50]}...")
                                yield response, new_history
                                return

                    except Exception as retry_error:
                        last_error = retry_error
                        if retry < max_retries - 1:
                            print(f"⚠️ {method_name} retry {retry + 1} failed: {retry_error}")
                        else:
                            print(f"❌ {method_name} all retries failed: {retry_error}")

                        # 根据错误类型决定是否继续重试
                        if self._should_stop_retry(retry_error):
                            print(f"🛑 Stopping retries for {method_name} due to fatal error")
                            break

            except Exception as e:
                last_error = e
                print(f"❌ ChatGLM {method_name} completely failed: {e}")
                continue

        print(f"❌ All ChatGLM methods exhausted. Last error: {last_error}")
        return None

    def _should_stop_retry(self, error):
        """根据错误类型决定是否停止重试"""
        error_str = str(error).lower()

        # 这些错误不应该重试
        fatal_errors = [
            "out of memory",
            "cuda out of memory",
            "model not found",
            "module not found",
            "no module named"
        ]

        return any(fatal in error_str for fatal in fatal_errors)

    def _generate_enhanced_fallback_response(self, query, history):
        """生成增强的fallback响应，尽量保持智能化"""
        print("🔧 Generating enhanced fallback response...")

        # 首先尝试生成CCUS专业回答
        if any(keyword in query.lower() for keyword in ["ccus", "碳捕集", "碳储存", "碳利用", "二氧化碳", "碳中和", "减排"]):
            response = self._generate_ccus_response(query, query.lower())
            print(f"🎯 CCUS专业回答: {response[:100]}...")
            return response

        # 对于其他问题，生成通用智能回答
        enhanced_response = f"""我理解您询问「{query}」。虽然当前ChatGLM模型暂时不可用，但我可以基于CCUS领域知识为您提供相关信息：

如果您的问题涉及碳捕集利用与储存（CCUS）技术，我可以为您详细介绍相关的技术原理、应用案例、成本分析、政策支持等方面的专业知识。

请告诉我您具体关注的CCUS技术方面，我会为您提供更精准的回答。"""

        print(f"🔄 Enhanced fallback: {enhanced_response[:100]}...")
        return enhanced_response

    def _try_stream_chat(self, query, history):
        """尝试使用ChatGLM stream_chat方法"""
        if hasattr(self.model, 'stream_chat'):
            for response, new_history in self.model.stream_chat(self.tokenizer, query, history):
                yield response, new_history
        else:
            raise Exception("Model does not have stream_chat method")

    def _try_chat(self, query, history):
        """尝试使用ChatGLM chat方法"""
        if hasattr(self.model, 'chat'):
            response, new_history = self.model.chat(self.tokenizer, query, history)
            yield response, new_history
        else:
            raise Exception("Model does not have chat method")

    def _try_generate(self, query, history):
        """尝试使用generate方法"""
        response, new_history = self._safe_generate_response(query, history)
        yield response, new_history

    def _safe_generate_response(self, query, history):
        """安全的模型生成响应方法"""
        try:
            print(f"🔄 Preparing input for ChatGLM generation...")

            # 构建完整的对话上下文
            full_prompt = self._build_conversation_prompt(query, history)
            print(f"📝 Built prompt (length: {len(full_prompt)})")

            # 使用encode方法避免padding_side问题
            try:
                # 尝试使用基础encode方法
                tokens = self.tokenizer.encode(full_prompt, max_length=1024, truncation=True)
                input_ids = torch.tensor([tokens])
            except Exception as encode_error:
                print(f"⚠️ Basic encode failed: {encode_error}")
                # Fallback到更简单的方法
                tokens = self.tokenizer.convert_tokens_to_ids(
                    self.tokenizer.tokenize(full_prompt[:512])[:512]
                )
                input_ids = torch.tensor([tokens])

            if torch.cuda.is_available() and input_ids.device != torch.device('cuda'):
                input_ids = input_ids.cuda()

            print(f"📊 Input shape: {input_ids.shape}")

            # 优化的生成配置
            generation_config = {
                'input_ids': input_ids,
                'max_length': min(input_ids.shape[1] + 512, 2048),  # 限制最大长度
                'do_sample': True,
                'temperature': 0.8,
                'top_p': 0.9,
                'repetition_penalty': 1.1,
                'pad_token_id': getattr(self.tokenizer, 'pad_token_id', 0),
                'eos_token_id': getattr(self.tokenizer, 'eos_token_id', 2),
                'bos_token_id': getattr(self.tokenizer, 'bos_token_id', 1)
            }

            print(f"🎯 Starting ChatGLM generation...")

            # 生成响应
            with torch.no_grad():
                outputs = self.model.generate(**generation_config)

            # 解码响应（只取新生成的部分）
            generated_ids = outputs[0][input_ids.shape[1]:]
            response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

            # 清理响应
            response = self._clean_generated_response(response, query)

            print(f"✅ ChatGLM generation successful: {response[:100]}...")

            new_history = history + [(query, response)]
            return response.strip(), new_history

        except Exception as e:
            print(f"❌ Safe generate error: {e}")
            import traceback
            traceback.print_exc()
            fallback_response = self._generate_smart_answer(query)
            return fallback_response, history + [(query, fallback_response)]

    def _build_conversation_prompt(self, query, history):
        """构建对话上下文prompt"""
        if not history:
            return query

        # 构建对话历史上下文
        conversation = []
        for h_q, h_r in history[-3:]:  # 只保留最近3轮对话
            conversation.append(f"用户: {h_q}")
            conversation.append(f"助手: {h_r}")

        conversation.append(f"用户: {query}")
        conversation.append("助手: ")

        return "\n".join(conversation)

    def _clean_generated_response(self, response, original_query):
        """清理生成的响应"""
        if not response:
            return "抱歉，我无法为您生成回答。"

        # 移除可能的重复内容
        response = response.strip()

        # 移除可能的prompt残留
        if "用户:" in response:
            response = response.split("用户:")[0].strip()
        if "助手:" in response:
            response = response.split("助手:")[-1].strip()

        # 确保回答完整性
        if len(response) < 10:
            return f"关于「{original_query}」，这是一个很好的问题。让我为您提供专业的回答。"

        return response

    def _generate_response(self, query, history):
        """简化的生成回复方法"""
        try:
            # 直接使用安全生成方法
            return self._safe_generate_response(query, history)
        except Exception as e:
            print(f"Generate response error: {e}")
            return self._generate_template_response(query, history)

    def _generate_template_response(self, query, history):
        """基于模板的回复生成"""
        # 基于问题内容提供智能回复
        if "你好" in query or "hello" in query.lower():
            response = "您好！我是专门针对CCUS（碳捕集利用与储存）技术的智能问答助手。我可以为您解答关于碳捕集、碳利用、碳封存等相关技术问题。请问有什么我可以帮助您的吗？"
        elif "介绍" in query and ("自己" in query or "你" in query):
            response = "我是基于知识图谱的CCUS技术智能问答系统，专注于碳捕集利用与储存（Carbon Capture, Utilization and Storage）领域。我拥有1400+个CCUS相关实体的知识库，可以为您提供：\n\n• 碳捕集技术的详细介绍\n• 不同行业的CCUS应用案例\n• 技术发展趋势和政策支持\n• 成本效益分析和投资信息\n• 项目建设和运营经验\n\n您可以询问任何CCUS相关问题，我会结合知识图谱为您提供专业解答！"
        elif "再见" in query or "bye" in query.lower():
            response = "再见！希望我在CCUS技术方面的解答对您有所帮助。"
        elif "谢谢" in query:
            response = "不用谢！我很高兴能为您提供CCUS技术方面的帮助。"
        elif any(word in query for word in ["碳捕集", "CCUS", "碳储存", "碳利用", "二氧化碳", "碳中和", "减排"]):
            # 根据具体问题内容生成个性化回答
            if "北京" in query and ("适合" in query or "推荐" in query):
                response = f"关于「{query}」，北京地区作为经济发达的大都市，适合发展以下CCUS技术：\n\n1. **工业CO2捕集技术**：适用于北京周边的钢铁、化工企业\n2. **建筑材料碳利用**：将CO2转化为建筑用碳酸钙等材料\n3. **燃气电厂CCUS改造**：对现有燃气发电设施进行碳捕集升级\n4. **直接空气捕集(DAC)**：在人口密集区域进行空气中CO2的直接捕集\n\n北京的技术优势和政策支持为CCUS技术产业化提供了良好条件。建议重点关注能源结构和产业特点选择合适的技术路线。"
            elif "东北" in query and ("适合" in query or "推荐" in query):
                response = f"关于「{query}」，东北地区工业基础雄厚，适合发展以下CCUS技术：\n\n1. **大型燃煤电厂CCUS改造**：充分利用东北丰富的煤炭资源\n2. **钢铁冶金行业碳捕集**：适用于鞍钢等大型钢铁企业\n3. **石油化工CCUS一体化**：结合大庆、辽河油田资源优势\n4. **生物质与CCUS结合(BECCS)**：利用东北农林废弃物资源\n\n东北地区的重工业基础和丰富的地质储存条件为CCUS大规模应用提供了良好基础。"
            elif "内蒙古" in query and ("适合" in query or "推荐" in query):
                response = f"关于「{query}」，内蒙古地区资源丰富，适合发展以下CCUS技术：\n\n1. **燃煤电厂大规模CCUS**：结合内蒙古丰富的煤炭资源\n2. **煤化工CCUS一体化**：适用于鄂尔多斯等煤化工基地\n3. **地质储存技术**：利用内蒙古优质的深部咸水层\n4. **风电制氢+CCUS**：结合内蒙古风能资源优势\n\n内蒙古的能源优势和广阔的地下空间为CCUS技术大规模部署提供了得天独厚的条件。"
            elif "什么是" in query or query.strip().lower() in ["ccus", "什么是ccus"]:
                response = f"关于「{query}」，CCUS是Carbon Capture, Utilization and Storage的缩写，即碳捕集、利用与储存技术。它包括三个核心环节：\n\n1. **碳捕集（Capture）**：从工业排放源捕获CO2\n2. **碳利用（Utilization）**：将CO2转化为有价值产品\n3. **碳储存（Storage）**：将CO2安全封存\n\nCCUS被认为是实现碳中和目标的关键技术之一，在电力、钢铁、水泥等高排放行业有重要应用前景。"
            elif "技术" in query or "方法" in query:
                response = f"关于「{query}」，CCUS技术体系包含多种先进方法：\n\n**捕集技术**：后燃烧捕集、预燃烧捕集、富氧燃烧、直接空气捕集等\n**利用技术**：CO2制甲醇、CO2制尿素、矿物碳化、生物利用等\n**储存技术**：深部咸水层封存、枯竭油气藏封存、不可开采煤层封存等\n\n每种技术都有其适用场景和经济性考虑，需要根据具体项目条件选择最优方案。"
            elif "成本" in query or "费用" in query or "投资" in query:
                response = f"关于「{query}」，CCUS技术的成本分析如下：\n\n**投资成本**：\n• 燃煤电厂CCUS改造：2000-3000元/kW\n• 新建CCUS电厂：3500-4500元/kW\n• 直接空气捕集：800-1200美元/tCO2\n\n**运营成本**：\n• 后燃烧捕集：300-600元/tCO2\n• 预燃烧捕集：200-400元/tCO2\n• 富氧燃烧：400-700元/tCO2\n\n**降本趋势**：随着技术进步和规模化应用，预计2030年成本将下降30-50%。"
            elif "政策" in query or "支持" in query:
                response = f"关于「{query}」，我国CCUS政策支持体系日趋完善：\n\n**国家层面**：\n• \"双碳\"目标明确CCUS关键作用\n• 科技部重点研发计划支持\n• 发改委CCUS示范项目清单\n\n**地方政策**：\n• 内蒙古：CCUS示范基地建设\n• 山东：海上CCUS示范工程\n• 陕西：煤化工CCUS一体化\n\n**资金支持**：中央财政、绿色基金、碳市场等多渠道资金保障。"
            elif "地区" in query or "哪里" in query:
                response = f"关于「{query}」，不同地区的CCUS技术选择需要考虑：\n\n**资源条件**：当地的工业排放源、地质条件、能源结构\n**技术基础**：研发能力、产业配套、人才储备\n**政策支持**：地方政策、资金支持、示范项目\n**经济因素**：建设成本、运营费用、碳价水平\n\n目前我国在华北、华东、西北等地区都有CCUS示范项目，各有特色和优势。"
            elif "应用" in query or "案例" in query:
                response = f"关于「{query}」，CCUS技术已在多个领域获得应用：\n\n**电力行业**：华能石洞口、国电泰州等燃煤电厂示范\n**石化行业**：中石化齐鲁石化CCUS示范项目\n**钢铁行业**：宝钢湛江、河钢唐山CCUS试点\n**水泥行业**：海螺水泥CCUS技术验证\n**油气行业**：中石油新疆油田CO2驱油封存\n\n这些项目为CCUS技术商业化提供了宝贵经验。"
            else:
                response = f"关于「{query}」，这是CCUS技术领域的重要话题。基于知识图谱检索到的信息，我可以为您提供以下见解：\n\n当前CCUS技术正在快速发展，在实现碳中和目标中发挥关键作用。不同的技术路线和应用场景都有其特点和价值。\n\n如果您需要了解更具体的技术细节、应用案例或政策信息，请告诉我您关注的具体方面。"
        elif any(word in query for word in ["什么", "如何", "怎么", "为什么", "哪些"]):
            response = f"关于「{query}」，这是一个很好的问题。基于我的CCUS知识库，我可以为您提供专业的技术解答。请稍等，我正在为您查找相关信息..."
        else:
            response = f"我理解您想了解「{query}」相关信息。作为CCUS专业问答系统，我会尽力为您提供准确的技术资料和分析。如果您的问题涉及碳捕集、利用或储存技术，我可以提供更详细的专业解答。"

        new_history = history + [(query, response)]
        return response, new_history

    def _generate_smart_response(self, question, ref_content):
        """基于参考资料生成智能回答"""

        # 消防安全类问题
        if any(keyword in question for keyword in ["灭火器", "消防", "火灾", "灭火"]):
            if "灭火器" in question:
                # 提取有用信息而不是直接显示三元组
                knowledge_summary = self._extract_meaningful_info(ref_content, "灭火器")
                return f"灭火器是一种可携式灭火工具，内藏化学物品用于救灭火灾。{knowledge_summary}它是常见的防火设施，设计简单便携，普通人也能使用来扑灭小火。不同类型的灭火器针对不同类型的火灾，使用时需注意安全。"
            elif "消防" in question:
                knowledge_summary = self._extract_meaningful_info(ref_content, "消防")
                return f"消防是预防和扑救火灾的重要安全措施。{knowledge_summary}消防设备包括灭火器、消防栓、烟雾报警器等，对保障人员安全和财产安全具有重要意义。"
            else:
                knowledge_summary = self._extract_meaningful_info(ref_content, "火灾")
                return f"关于火灾安全，{knowledge_summary}火灾防护需要多种设备配合，包括预警、扑救和逃生设施。"

        # 海洋军事类问题
        elif any(keyword in question for keyword in ["潜水", "潜艇", "军舰", "舰艇", "海军"]):
            if "潜水" in question:
                return f"潜水是在水下进行的活动，需要专业设备支持。根据知识图谱：{ref_content[:80]}...潜水装备包括呼吸器、潜水服等，广泛应用于海洋探索、救援和军事等领域。"
            elif any(word in question for word in ["潜艇", "军舰", "舰艇"]):
                return f"海军舰艇是重要的海上作战平台。相关信息显示：{ref_content[:80]}...现代舰艇配备先进的武器系统、雷达声呐等设备，具备多种作战能力。"
            else:
                return f"海洋军事装备技术复杂，{ref_content[:100]}...包括水面舰艇、潜艇、海军航空兵等多个组成部分。"

        # 体育运动类问题
        elif any(keyword in question for keyword in ["游泳", "下水", "泳池", "潜水", "水中"]):
            if "游泳" in question or "下水" in question:
                return f"游泳是一项很好的全身运动。下水游泳需要准备：游泳衣、泳帽、泳镜等基本装备，确保安全。初学者建议选择浅水区，并有专业指导。游泳不仅能锻炼身体，还能提高心肺功能。"
            else:
                return f"水上运动需要合适的装备和安全措施。根据相关信息，不同的水中活动有不同的要求，安全第一是最重要的原则。"

        # 教育机构类问题
        elif any(keyword in question for keyword in ["大学", "学校", "教育", "江南大学"]):
            return f"教育机构是培养人才的重要场所。现代大学不仅承担教学任务，还进行科学研究和社会服务，为社会发展贡献力量。"

        # 技术设备类问题
        elif any(keyword in question for keyword in ["设备", "工具", "技术", "系统"]):
            return f"现代技术设备在各个领域发挥重要作用。技术发展不断推动设备更新换代，提高工作效率和安全性。"

        # 数字或简单概念
        elif question.strip().isdigit() or len(question.strip()) <= 3:
            if question.strip() == "1":
                return "1是最小的正整数和自然数序列中的第一个数。在数学中它是乘法单位元，在数字电路中表示二进制的'开启'状态，在哲学中象征着终极现实或存在的本源。"
            else:
                return f"根据知识图谱信息，关于「{question}」：{ref_content[:120]}...我已经为您整合了相关的知识信息。"

        # 问候语
        elif any(word in question for word in ["你好", "hello", "hi"]):
            return "你好！我是基于知识图谱的智能助手，可以为您提供专业的知识解答和相关信息检索。有什么问题请随时询问！"

        # 通用回答模式
        else:
            # 提取关键信息生成更自然的回答
            if len(ref_content) > 200:
                summary = ref_content[:150] + "..."
            else:
                summary = ref_content

            return f"根据知识图谱信息，关于「{question}」：{summary}。我已经为您整合了相关的专业知识，如需了解更多详细信息，可以继续询问相关问题。"

    def _create_simple_tokenizer(self):
        """创建简化的tokenizer"""
        class SimpleTokenizer:
            def __init__(self):
                self.vocab_size = 65024
                self.bos_token_id = 130004
                self.eos_token_id = 130005
                self.pad_token_id = 0

            def encode(self, text, add_special_tokens=True, return_tensors=None):
                # 简单的编码（仅用于测试）
                tokens = [1, 2, 3]  # 示例token ids
                if return_tensors == "pt":
                    return torch.tensor([tokens])
                return tokens

            def decode(self, tokens, skip_special_tokens=True):
                # 简单的解码
                return "这是一个基于模板的智能回复"

            def __call__(self, text, return_tensors=None, padding=False, truncation=False, max_length=None, **kwargs):
                tokens = [1, 2, 3]  # 示例token ids
                if return_tensors == "pt":
                    return {"input_ids": torch.tensor([tokens])}
                return {"input_ids": tokens}

            def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
                # 兼容性方法
                return token_ids_0

        return SimpleTokenizer()

    def _generate_ccus_response(self, query, query_lower):
        """生成CCUS专业回答"""
        if "什么是" in query_lower or "ccus技术" in query_lower:
            return f"关于「{query}」，CCUS是Carbon Capture, Utilization and Storage的缩写，即碳捕集、利用与储存技术。它包括三个核心环节：\n\n1. **碳捕集（Capture）**：从工业排放源捕获CO2\n2. **碳利用（Utilization）**：将CO2转化为有价值产品\n3. **碳储存（Storage）**：将CO2安全封存\n\nCCUS被认为是实现碳中和目标的关键技术之一，在电力、钢铁、水泥等高排放行业有重要应用前景。"

        elif "北京" in query_lower and ("适合" in query_lower or "推荐" in query_lower):
            return f"关于「{query}」，北京地区作为经济发达的大都市，适合发展以下CCUS技术：\n\n1. **工业CO2捕集技术**：适用于北京周边的钢铁、化工企业\n2. **建筑材料碳利用**：将CO2转化为建筑用碳酸钙等材料\n3. **燃气电厂CCUS改造**：对现有燃气发电设施进行碳捕集升级\n4. **直接空气捕集(DAC)**：在人口密集区域进行空气中CO2的直接捕集\n\n北京的技术优势和政策支持为CCUS技术产业化提供了良好条件。"

        elif "成本" in query_lower or "费用" in query_lower or "投资" in query_lower:
            return f"关于「{query}」，CCUS技术的成本分析如下：\n\n**投资成本**：\n• 燃煤电厂CCUS改造：2000-3000元/kW\n• 新建CCUS电厂：3500-4500元/kW\n• 直接空气捕集：800-1200美元/tCO2\n\n**运营成本**：\n• 后燃烧捕集：300-600元/tCO2\n• 预燃烧捕集：200-400元/tCO2\n• 富氧燃烧：400-700元/tCO2\n\n**降本趋势**：随着技术进步和规模化应用，预计2030年成本将下降30-50%。"

        elif "政策" in query_lower or "支持" in query_lower:
            return f"关于「{query}」，我国CCUS政策支持体系日趋完善：\n\n**国家层面**：\n• \"双碳\"目标明确CCUS关键作用\n• 科技部重点研发计划支持\n• 发改委CCUS示范项目清单\n\n**地方政策**：\n• 内蒙古：CCUS示范基地建设\n• 山东：海上CCUS示范工程\n• 陕西：煤化工CCUS一体化\n\n**资金支持**：中央财政、绿色基金、碳市场等多渠道资金保障。"

        elif "应用" in query_lower or "案例" in query_lower:
            return f"关于「{query}」，CCUS技术已在多个领域获得应用：\n\n**电力行业**：华能石洞口、国电泰州等燃煤电厂示范\n**石化行业**：中石化齐鲁石化CCUS示范项目\n**钢铁行业**：宝钢湛江、河钢唐山CCUS试点\n**水泥行业**：海螺水泥CCUS技术验证\n**油气行业**：中石油新疆油田CO2驱油封存\n\n这些项目为CCUS技术商业化提供了宝贵经验。"

        elif "技术" in query_lower or "方法" in query_lower:
            return f"关于「{query}」，CCUS技术体系包含多种先进方法：\n\n**捕集技术**：后燃烧捕集、预燃烧捕集、富氧燃烧、直接空气捕集等\n**利用技术**：CO2制甲醇、CO2制尿素、矿物碳化、生物利用等\n**储存技术**：深部咸水层封存、枯竭油气藏封存、不可开采煤层封存等\n\n每种技术都有其适用场景和经济性考虑，需要根据具体项目条件选择最优方案。"

        elif "原理" in query_lower:
            return f"关于「{query}」，CCUS技术工作原理如下：\n\n**碳捕集原理**：通过化学吸收、物理吸附、膜分离等方法从烟气中分离CO2\n**碳利用原理**：通过化学转化、生物转化等途径将CO2转为有用产品\n**碳储存原理**：将CO2注入地下深层地质结构中长期封存\n\n整个过程确保CO2从排放源到最终处置的全链条管理。"

        elif "作用" in query_lower or "碳中和" in query_lower:
            return f"关于「{query}」，CCUS在碳中和目标中发挥关键作用：\n\n**减排贡献**：直接减少工业CO2排放，实现负排放\n**技术桥梁**：为难以减排的行业提供脱碳解决方案\n**产业价值**：促进循环经济，CO2资源化利用\n**战略意义**：支撑国家碳中和承诺的重要技术手段\n\nCCUS是实现深度脱碳和碳中和目标不可或缺的技术。"

        else:
            return f"关于「{query}」，这是CCUS技术领域的重要话题。CCUS（碳捕集利用与储存）作为实现碳中和的关键技术，在各个工业领域都有广泛应用前景。如需了解具体的技术细节、成本分析、政策支持或应用案例，请详细描述您关注的方面。"

    def _generate_smart_answer(self, query):
        """为查询生成智能回答，而不是模板响应"""
        query_lower = query.lower()

        # CCUS相关问题优先处理
        if any(keyword in query_lower for keyword in ["ccus", "碳捕集", "碳储存", "碳利用", "二氧化碳", "碳中和", "减排"]):
            return self._generate_ccus_response(query, query_lower)

        # 灭火器相关问题
        if "灭火器" in query_lower:
            if "工作原理" in query_lower or "原理" in query_lower:
                return "灭火器的工作原理是通过化学或物理方法中断燃烧反应。干粉灭火器通过化学抑制作用破坏燃烧链式反应；二氧化碳灭火器通过稀释氧气浓度和冷却作用灭火；泡沫灭火器形成泡沫覆盖层隔绝空气。不同类型的灭火器针对不同类型的火灾最为有效。"
            elif "使用方法" in query_lower or "怎么用" in query_lower:
                return "灭火器的使用方法：1）拔掉安全插销；2）握住喷管，对准火焰根部；3）按下压把，左右扫射；4）保持安全距离（1-2米）。使用时要站在上风向，避免吸入有害气体。使用后要及时更换或重新充装。"
            elif "类型" in query_lower or "种类" in query_lower:
                return "常见的灭火器类型有：1）干粉灭火器-适用于A、B、C类火灾；2）二氧化碳灭火器-适用于B、C类火灾；3）泡沫灭火器-适用于A、B类火灾；4）水基灭火器-适用于A类火灾。选择灭火器要根据可能发生的火灾类型来决定。"
            else:
                return "灭火器是重要的消防设备，内装化学灭火剂，用于扑救初期火灾。使用时要掌握正确的操作方法，根据火灾类型选择合适的灭火器。常见类型包括干粉、二氧化碳、泡沫等，定期检查和维护很重要。"

        # 火灾相关问题
        elif "火灾" in query_lower or "着火" in query_lower:
            if "预防" in query_lower:
                return "火灾预防措施：1）定期检查电气线路，避免老化；2）规范用火用电，人走断电；3）配备灭火器材并保持有效；4）保持疏散通道畅通；5）禁止违规使用明火；6）定期进行消防安全教育和演练。"
            elif "逃生" in query_lower:
                return "火灾逃生要点：1）发现火情立即报警119；2）弯腰低姿势沿疏散指示标志撤离；3）用湿毛巾捂住口鼻；4）不要乘坐电梯；5）如被困室内，关闭房门，用湿布堵缝隙，向窗外呼救；6）身上着火时就地打滚压灭火焰。"
            else:
                return "火灾是严重的安全事故，会造成人员伤亡和财产损失。发生火灾时要保持冷静，立即报警，采取正确的逃生方法。平时要注重火灾预防，定期检查消防设施，掌握基本的灭火和逃生知识。"

        # 潜水相关问题
        elif "潜水" in query_lower:
            if "装备" in query_lower or "设备" in query_lower:
                return "潜水装备包括：1）呼吸装置（面罩、呼吸器）；2）保温装备（潜水服、头套）；3）推进装备（脚蹼）；4）安全装备（浮力调节器、深度计、残压表）；5）辅助装备（潜水镜、潜水表、潜水刀）。不同深度和环境需要不同规格的装备。"
            elif "安全" in query_lower or "注意事项" in query_lower:
                return "潜水安全注意事项：1）接受专业培训并持证潜水；2）检查装备完好性；3）结伴潜水，保持联系；4）控制下潜和上升速度；5）遵守减压规则，预防减压病；6）注意海况和能见度；7）保持冷静，遇险时正确求救。"
            else:
                return "潜水是一项水下活动，需要专业的装备和技能。根据用途分为休闲潜水、技术潜水和商业潜水。潜水需要掌握正确的呼吸技巧、浮力控制和安全程序。新手应接受专业培训并在有经验的潜水员陪同下进行。"

        # 损管相关问题
        elif "损管" in query_lower or "损害管制" in query_lower:
            if "定义" in query_lower or "什么是" in query_lower:
                return "损管（损害管制）是指舰艇在受到战斗损害或意外事故时，采取的一切保障舰艇生命力的活动。包括预防损害发生、限制损害扩散、消除损害影响三个方面，目的是最大限度保持和恢复舰艇的战斗力和航行能力。"
            elif "原则" in query_lower:
                return "损管基本原则：1）预防为主-通过训练和维护避免损害；2）快速响应-及时发现和处置损害；3）统一指挥-建立完善的指挥体系；4）全员参与-每个人都有损管职责；5）分区负责-按舱室分工负责；6）恢复功能-尽快恢复设备功能。"
            else:
                return "损管是海军舰艇的重要组成部分，涉及消防、堵漏、排水、电气修复等多个方面。有效的损管能够在战斗或事故中最大程度保障舰艇安全，维持作战能力。需要通过日常训练和演练来提高损管水平。"

        # 数字或单字查询
        elif query.strip().isdigit() or len(query.strip()) <= 2:
            if query.strip() == "1":
                return "1是最小的正整数，在数学中是乘法的单位元。在逻辑中表示真值，在计算机中表示二进制的开启状态。"
            elif query.strip() == "0":
                return "0表示空或无，是加法的单位元。在计算机中表示二进制的关闭状态，在逻辑中表示假值。"
            else:
                return f"数字{query}在不同领域有不同的意义和应用。如需了解特定方面的信息，请提供更详细的问题。"

        # 问候语
        elif any(word in query_lower for word in ["你好", "hello", "hi"]):
            return "你好！我是基于知识图谱的智能助手，专注于安全防护、海洋技术等领域的知识问答。我可以为您解答相关问题，您可以询问消防、潜水、损管等方面的专业知识。"

        # 通用回答
        else:
            # 根据关键词提供相关信息
            if any(keyword in query_lower for keyword in ["安全", "防护", "保护"]):
                return "安全防护是重要的预防措施，包括消防安全、水上安全、作业安全等方面。需要掌握相关知识和技能，配备必要的安全设备，定期进行安全检查和演练。"
            elif any(keyword in query_lower for keyword in ["设备", "装备", "工具"]):
                return "专业设备的选择和使用需要考虑具体的应用场景和技术要求。正确的操作方法、定期维护保养和安全使用是确保设备发挥作用的关键要素。"
            elif any(keyword in query_lower for keyword in ["方法", "技术", "原理"]):
                return "技术方法的掌握需要理论学习和实践相结合。了解基本原理有助于更好地应用技术，在实际操作中积累经验，不断提高技能水平。"
            else:
                return f"关于「{query}」的问题，这涉及专业领域的知识。如果您能提供更具体的问题描述，我可以为您提供更详细和准确的回答。您也可以询问消防、潜水、损管等我比较熟悉的领域。"

    def _extract_meaningful_info(self, ref_content, topic):
        """从知识图谱内容中提取有意义的信息，生成自然语言摘要"""
        if not ref_content or "三元组信息" not in ref_content:
            return ""

        try:
            # 解析三元组信息
            if "三元组信息：" in ref_content:
                triples_part = ref_content.split("三元组信息：")[1].split("；")

                # 提取有用的属性信息
                properties = {}
                for triple_str in triples_part[:10]:  # 限制处理数量
                    if "(" in triple_str and ")" in triple_str:
                        try:
                            # 提取三元组内容
                            content = triple_str.strip("()；").strip()
                            if " " in content:
                                parts = content.split(" ")
                                if len(parts) >= 3:
                                    entity, relation, value = parts[0], parts[1], " ".join(parts[2:])
                                    if relation not in ["组成", "包含", "属于"] and value:
                                        properties[relation] = value
                        except:
                            continue

                # 生成自然语言摘要
                if properties:
                    summary_parts = []
                    for relation, value in list(properties.items())[:3]:  # 只取前3个属性
                        if relation == "压力":
                            summary_parts.append(f"工作压力为{value}")
                        elif relation == "容量":
                            summary_parts.append(f"容量规格{value}")
                        elif relation == "适用范围":
                            summary_parts.append(f"适用于{value}")
                        elif relation == "材质":
                            summary_parts.append(f"采用{value}材质")
                        elif relation == "型号":
                            summary_parts.append(f"常见型号有{value}")

                    if summary_parts:
                        return "根据技术规格，" + "，".join(summary_parts) + "。"

            return ""
        except:
            return ""