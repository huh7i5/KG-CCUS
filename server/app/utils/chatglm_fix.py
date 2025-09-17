"""
ChatGLM-6B兼容性修复
解决tokenizer的vocab_size属性问题
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModel
import sentencepiece as spm

def fix_chatglm_tokenizer(model_path):
    """修复ChatGLM tokenizer的兼容性问题"""

    # 确保sentencepiece模型文件存在
    spm_model_path = os.path.join(model_path, "ice_text.model")
    if not os.path.exists(spm_model_path):
        print(f"❌ SentencePiece model not found: {spm_model_path}")
        return None, None

    try:
        print("🔧 Loading ChatGLM with compatibility fixes...")

        # 1. 先尝试加载tokenizer，并修复vocab_size问题
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                use_fast=False,
                local_files_only=True
            )
        except AttributeError as e:
            if "vocab_size" in str(e):
                print("⚠️ Original tokenizer has vocab_size issue, using simple tokenizer")
                tokenizer = create_simple_tokenizer(model_path)
            else:
                raise e

        # 2. 手动修复sp_tokenizer属性
        if hasattr(tokenizer, 'sp_tokenizer') and tokenizer.sp_tokenizer is None:
            # 创建SentencePiece处理器
            sp_processor = spm.SentencePieceProcessor()
            sp_processor.Load(spm_model_path)
            tokenizer.sp_tokenizer = sp_processor
            print("✅ Fixed sp_tokenizer attribute")

        # 3. 确保num_tokens属性存在
        if hasattr(tokenizer, 'sp_tokenizer') and hasattr(tokenizer.sp_tokenizer, 'vocab_size'):
            tokenizer.sp_tokenizer.num_tokens = tokenizer.sp_tokenizer.vocab_size()

        print("✅ Tokenizer loaded and fixed")

        # 4. 加载模型
        print("Loading model...")
        model = AutoModel.from_pretrained(
            model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            local_files_only=True
        )

        # 5. 移动到GPU（如果可用）
        if torch.cuda.is_available():
            model = model.cuda()
            print("✅ Model loaded on GPU")
        else:
            print("⚠️ Model loaded on CPU")

        model.eval()
        print("✅ ChatGLM-6B loaded successfully with fixes!")

        return tokenizer, model

    except Exception as e:
        print(f"❌ Failed to load with fixes: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def load_chatglm_alternative(model_path):
    """备选加载方案：使用本地文件"""
    try:
        print("🔄 Trying alternative loading method...")

        # 使用本地文件加载
        from transformers import AutoConfig

        # 1. 加载配置
        config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)

        # 2. 手动创建tokenizer（跳过problematic初始化）
        import json
        tokenizer_config_path = os.path.join(model_path, "tokenizer_config.json")

        if os.path.exists(tokenizer_config_path):
            with open(tokenizer_config_path, 'r') as f:
                tokenizer_config = json.load(f)

        # 3. 直接加载模型
        model = AutoModel.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            local_files_only=True
        )

        # 4. 尝试从HuggingFace直接加载tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
            print("✅ Loaded tokenizer from HuggingFace")
        except:
            # 如果失败，创建简化的tokenizer
            tokenizer = create_simple_tokenizer(model_path)
            print("✅ Created simple tokenizer")

        if torch.cuda.is_available():
            model = model.cuda()

        model.eval()
        print("✅ Alternative loading successful!")

        return tokenizer, model

    except Exception as e:
        print(f"❌ Alternative loading failed: {e}")
        return None, None

def create_simple_tokenizer(model_path):
    """创建简化的tokenizer"""
    import sentencepiece as spm

    class TokenizedInputs(dict):
        """支持.to()方法的字典类，兼容ChatGLM模型需求"""
        def to(self, device):
            """将所有tensor移动到指定设备"""
            result = TokenizedInputs()
            for key, value in self.items():
                if hasattr(value, 'to'):
                    result[key] = value.to(device)
                else:
                    result[key] = value
            return result

    class SimpleTokenizer:
        def __init__(self, model_path):
            self.sp_model = spm.SentencePieceProcessor()
            spm_path = os.path.join(model_path, "ice_text.model")
            self.sp_model.Load(spm_path)
            self._vocab_size = self.sp_model.vocab_size()

            # 添加必要的属性
            self.eos_token = "</s>"
            self.eos_token_id = self.sp_model.PieceToId("</s>")
            self.pad_token = "<pad>"
            self.pad_token_id = 0

        @property
        def vocab_size(self):
            return self._vocab_size

        def encode(self, text, return_tensors=None, **kwargs):
            """编码文本为token ids"""
            if isinstance(text, str):
                ids = self.sp_model.EncodeAsIds(text)
            else:
                ids = text

            if return_tensors == "pt":
                import torch
                return torch.tensor([ids])
            elif return_tensors is not None:
                # 对于其他return_tensors值，返回列表格式
                return [ids]
            return ids

        def decode(self, ids, skip_special_tokens=True, **kwargs):
            """解码token ids为文本"""
            if hasattr(ids, 'tolist'):
                ids = ids.tolist()
            if isinstance(ids[0], list):
                ids = ids[0]
            return self.sp_model.DecodeIds(ids)

        def __call__(self, text, **kwargs):
            """使tokenizer可调用"""
            # 处理列表输入 (像 tokenizer([prompt], return_tensors="pt"))
            if isinstance(text, list):
                if len(text) == 1:
                    # 单个字符串的列表
                    result = self.encode(text[0], **kwargs)
                    # 返回TokenizedInputs字典，同时支持.to()方法
                    import torch
                    if isinstance(result, torch.Tensor):
                        return TokenizedInputs({"input_ids": result})
                    else:
                        return TokenizedInputs({"input_ids": torch.tensor([result])})
                else:
                    # 多个字符串的列表，批处理
                    results = []
                    for t in text:
                        results.append(self.encode(t, return_tensors=None))
                    if kwargs.get("return_tensors") == "pt":
                        import torch
                        return TokenizedInputs({"input_ids": torch.tensor(results)})
                    return TokenizedInputs({"input_ids": results})
            else:
                # 单个字符串
                return self.encode(text, **kwargs)

        def convert_tokens_to_ids(self, tokens):
            if isinstance(tokens, str):
                return self.sp_model.PieceToId(tokens)
            return [self.sp_model.PieceToId(token) for token in tokens]

        def convert_ids_to_tokens(self, ids):
            if isinstance(ids, int):
                return self.sp_model.IdToPiece(ids)
            return [self.sp_model.IdToPiece(id) for id in ids]

        def tokenize(self, text):
            """分词"""
            return self.sp_model.EncodeAsPieces(text)

        def convert_tokens_to_string(self, tokens):
            """将tokens转换为字符串"""
            return self.sp_model.DecodePieces(tokens)

        @property
        def bos_token_id(self):
            return self.sp_model.PieceToId("<sop>")

        @property
        def gmask_token_id(self):
            return self.sp_model.PieceToId("[gMASK]")

        def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
            """构建带特殊token的输入"""
            gmask_id = self.gmask_token_id
            bos_id = self.bos_token_id
            if gmask_id is None:
                gmask_id = 150001  # 默认值
            if bos_id is None:
                bos_id = 150004  # 默认值

            token_ids_0 = token_ids_0 + [gmask_id, bos_id]
            if token_ids_1 is not None:
                token_ids_0 = token_ids_0 + token_ids_1 + [self.eos_token_id]
            return token_ids_0

    return SimpleTokenizer(model_path)