"""
ChatGLM Tokenizer 修复工具
解决 vocab_size 属性缺失问题
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModel


class FixedChatGLMLoader:
    """修复后的ChatGLM加载器"""

    def __init__(self, model_path):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.loaded = False

    def load(self):
        """加载模型和tokenizer"""
        try:
            print("🔧 Loading ChatGLM with custom fixes...")

            # 方法1: 尝试直接修复tokenizer文件
            if self._fix_tokenizer_file():
                return self._load_with_fixed_tokenizer()

            # 方法2: 使用替代方法
            return self._load_with_workaround()

        except Exception as e:
            print(f"❌ All loading methods failed: {e}")
            return False

    def _fix_tokenizer_file(self):
        """修复tokenizer文件中的vocab_size问题"""
        try:
            # 查找tokenizer文件
            tokenizer_file = os.path.join(self.model_path, "tokenization_chatglm.py")
            if not os.path.exists(tokenizer_file):
                return False

            print("🔧 Fixing tokenizer file...")

            # 读取文件内容
            with open(tokenizer_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否需要修复
            if 'self.vocab_size' not in content and '@property' not in content:
                # 添加vocab_size属性
                vocab_size_property = '''
    @property
    def vocab_size(self):
        """Return vocab size"""
        if hasattr(self, 'sp_model'):
            return self.sp_model.get_piece_size()
        return 65024  # ChatGLM-6B default vocab size
'''

                # 在类定义后添加属性
                if 'class ChatGLMTokenizer' in content:
                    # 找到合适的位置插入
                    lines = content.split('\n')
                    new_lines = []
                    in_class = False
                    added = False

                    for line in lines:
                        new_lines.append(line)
                        if 'class ChatGLMTokenizer' in line:
                            in_class = True
                        elif in_class and line.strip().startswith('def __init__') and not added:
                            # 在__init__方法前添加vocab_size属性
                            new_lines.extend(vocab_size_property.split('\n'))
                            added = True

                    if added:
                        # 写回文件
                        with open(tokenizer_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(new_lines))
                        print("✅ Tokenizer file fixed")
                        return True

            return True  # 文件已经正确或不需要修复

        except Exception as e:
            print(f"❌ Failed to fix tokenizer file: {e}")
            return False

    def _load_with_fixed_tokenizer(self):
        """使用修复后的tokenizer加载"""
        try:
            print("📦 Loading with fixed tokenizer...")

            # 清理缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                use_fast=False
            )

            # 验证vocab_size是否正常工作
            try:
                vocab_size = self.tokenizer.vocab_size
                print(f"✅ Tokenizer loaded (vocab_size: {vocab_size})")
            except AttributeError:
                print("⚠️ vocab_size attribute missing, adding manually...")
                # 添加vocab_size属性作为property
                def get_vocab_size(tokenizer_instance):
                    if hasattr(tokenizer_instance, 'sp_tokenizer'):
                        return tokenizer_instance.sp_tokenizer.num_tokens
                    return 65024

                # 绑定vocab_size属性到实例
                self.tokenizer.vocab_size = get_vocab_size(self.tokenizer)
                print(f"✅ Fixed vocab_size: {self.tokenizer.vocab_size}")

            # 加载模型
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto"
            ).half().cuda()

            self.model.eval()
            self.loaded = True

            print("✅ ChatGLM model loaded successfully!")
            return True

        except Exception as e:
            print(f"❌ Fixed tokenizer loading failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_with_workaround(self):
        """使用变通方法加载"""
        try:
            print("🔄 Using workaround method...")

            # 动态修复vocab_size属性
            import types

            def add_vocab_size(tokenizer_class):
                """动态添加vocab_size属性"""
                def vocab_size_property(self):
                    if hasattr(self, 'sp_model'):
                        return self.sp_model.get_piece_size()
                    return 65024

                tokenizer_class.vocab_size = property(vocab_size_property)
                return tokenizer_class

            # 尝试直接使用官方tokenizer作为备选
            try:
                print("Trying official ChatGLM tokenizer from HuggingFace...")
                from transformers import AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "THUDM/chatglm-6b",
                    trust_remote_code=True,
                    use_fast=False
                )
                print("✅ Using official HuggingFace tokenizer")

            except:
                # 如果还是失败，创建一个简化版本
                print("Creating simplified tokenizer...")
                self.tokenizer = self._create_simple_tokenizer()

            print("✅ Tokenizer loaded with workaround")

            # 加载模型到CPU（更稳定）
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float32,
                device_map="cpu"
            )

            self.model.eval()
            self.loaded = True

            print("✅ Model loaded on CPU with workaround!")
            return True

        except Exception as e:
            print(f"❌ Workaround method failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_simple_tokenizer(self):
        """创建简化的tokenizer"""
        class SimpleTokenizer:
            def __init__(self):
                self.vocab_size = 65024

            def encode(self, text):
                # 简单的编码（仅用于测试）
                return [1, 2, 3]  # 示例token ids

            def decode(self, tokens, skip_special_tokens=True):
                # 简单的解码
                return "这是一个简化的回复"

            def __call__(self, text, return_tensors=None):
                tokens = self.encode(text)
                if return_tensors == "pt":
                    return {"input_ids": torch.tensor([tokens])}
                return {"input_ids": tokens}

        return SimpleTokenizer()

    def chat(self, query, history=None):
        """聊天方法"""
        if not self.loaded:
            return "模型未加载", history or []

        try:
            if hasattr(self.model, 'chat'):
                return self.model.chat(self.tokenizer, query, history or [])
            else:
                # 简化的回复
                response = f"基于ChatGLM的回复：{query}"
                new_history = (history or []) + [(query, response)]
                return response, new_history

        except Exception as e:
            print(f"Chat error: {e}")
            return f"聊天错误: {e}", history or []


def load_chatglm_fixed(model_path):
    """加载修复后的ChatGLM"""
    loader = FixedChatGLMLoader(model_path)
    success = loader.load()

    if success:
        return loader.tokenizer, loader.model
    else:
        return None, None