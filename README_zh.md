# MAGMA：面向智能体的多图记忆架构

[English](README.md) | **简体中文**

MAGMA（Multi-Graph based Agentic Memory Architecture）是一种面向长程对话记忆与多跳推理的记忆架构。它将同一记忆事件组织为多个关系视图，并根据问题意图检索相关事件，帮助系统利用跨轮次、跨会话的信息回答问题。

论文发表于 ACL 2026 主会：[论文页面](https://aclanthology.org/2026.acl-long.1709/) · [arXiv](https://arxiv.org/abs/2601.03236)。本仓库提供记忆构建、检索和 LoCoMo、LongMemEval 评测脚本。论文中的实验结果不代表本地环境已经完成复现。

## 方法概览

MAGMA 将事件作为记忆节点，并从不同关系视角组织节点：

- **语义关系**：连接内容相近的事件。
- **时间关系**：表示事件的先后或时间联系。
- **因果关系**：表示事件之间的原因与结果。
- **实体关系**：连接涉及相同人物、地点或事物的事件。

回答问题时，系统先检索候选事件，再依据问题所需的关系扩展相关上下文，最后生成答案。不同问题可以侧重不同关系，例如“后来发生了什么”需要时间信息，“为什么改变计划”则需要因果线索。

## 环境要求

- Python 3.9 或更高版本
- 使用 OpenAI 时设置 `OPENAI_API_KEY`；使用 vLLM 等兼容服务时设置 `OPENAI_BASE_URL` 和服务提供的模型名
- 默认的 `minilm` 嵌入模型使用 Sentence Transformers；首次运行可能需要下载模型

## 安装

```bash
git clone https://github.com/FredJiang0324/MAGMA.git
cd MAGMA
python -m venv .venv
```

激活虚拟环境：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

将 `.env.example` 复制为 `.env`，按使用的服务修改配置。使用 OpenAI 时填写 API 密钥：

```dotenv
OPENAI_API_KEY=你的密钥
DEFAULT_MODEL=gpt-4o-mini
```

使用本地 vLLM 等 OpenAI 兼容服务时，设置服务地址、接口密钥（未启用鉴权时可使用 `EMPTY`）和 vLLM 提供的模型 ID：

```dotenv
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
OPENAI_API_KEY=EMPTY
DEFAULT_MODEL=qwen3-8b
```

未在 `.env` 设置 `DEFAULT_MODEL` 时默认使用 `gpt-4o-mini`；命令行的 `--model` 参数可以覆盖该值。请勿提交含真实密钥的 `.env` 文件。

请勿将包含真实密钥的 `.env` 文件提交到版本控制。

## 快速开始

### LoCoMo 评测

仓库包含 `data/locomo10.json`。以下命令运行第 0 个样本的前 10 个问题，并评测类别 1 至 4：

```bash
python test_fixed_memory.py --sample 0 --max-questions 10 --category-to-test 1,2,3,4
```

指定单个类别或多个样本：

```bash
# 只测类别 1
python test_fixed_memory.py --sample 0 --category-to-test 1

# 测试第 0、1 个样本
python test_fixed_memory.py --sample 0 1 --max-questions 50
```

测试脚本默认使用 `.env` 中的模型配置（未设置时为 `gpt-4o-mini`）、`minilm` 嵌入，并启用并行运行和 best-of-3 答案选择。使用 OpenAI 或兼容模型服务器进行答案生成与评测时，需正确配置相应接口。常用选项包括：

```bash
python test_fixed_memory.py --help
```

### LongMemEval 评测

完整数据集需单独获取。仓库提供小型示例 `examples/longmemeval_sample.json`，可先用它运行少量问题：

```bash
python test_longmemeval_chunked.py --dataset examples/longmemeval_sample.json --max-questions 5
```

完整数据集路径和下载说明见 [`data/README.md`](data/README.md)。取得数据后，将 `--dataset` 指向对应 JSON 文件：

```bash
python test_longmemeval_chunked.py --dataset data/longmemeval_s_cleaned.json --max-questions 5
```

评测结果、缓存及模型输出会写入运行目录；完整评测的耗时和 API 用量取决于数据规模、模型和参数。

### 通用命令行入口

`main.py` 提供 `build`、`query` 和 `test` 模式。具体数据格式和行为以脚本实现为准：

```bash
python main.py --help
python main.py --mode build --input <对话JSON路径>
python main.py --mode query --question "之前提到的计划是什么？"
```

## 目录结构

```text
.
├── main.py                      # 通用命令行入口
├── memory/
│   ├── trg_memory.py            # 记忆系统及图、向量存取
│   ├── graph_db.py              # 图结构与关系操作
│   ├── vector_db.py             # 向量存储和嵌入
│   ├── memory_builder.py        # 从对话构建记忆
│   ├── query_engine.py          # 候选检索与问题处理
│   ├── temporal_parser.py       # 时间解析
│   └── episode_segmenter.py     # 事件片段处理
├── utils/                       # LLM 控制器、数据加载等工具
├── test_fixed_memory.py         # LoCoMo 评测脚本
├── test_longmemeval_chunked.py  # LongMemEval 分块评测脚本
├── data/                        # LoCoMo 数据及数据说明
├── examples/                    # 小型示例数据
└── requirements.txt             # Python 依赖
```

## 数据集

- **LoCoMo**：仓库包含 `data/locomo10.json`。测试代码的类别编号和参数说明可通过 `python test_fixed_memory.py --help` 查看。
- **LongMemEval**：完整文件不包含在仓库中；使用 `examples/longmemeval_sample.json` 试跑，或按 [`data/README.md`](data/README.md) 获取完整数据。

请遵循数据集来源和许可方对数据的使用要求。

## 论文引用

```bibtex
@inproceedings{jiang-etal-2026-magma,
  title     = "{MAGMA}: A Multi-Graph based Agentic Memory Architecture for {AI} Agents",
  author    = "Jiang, Dongming and Li, Yi and Li, Guanpeng and Li, Bingzhe",
  booktitle = "Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
  year      = "2026",
  pages     = "36848--36865",
  url       = "https://aclanthology.org/2026.acl-long.1709/",
  doi       = "10.18653/v1/2026.acl-long.1709"
}
```

## 许可证

本项目使用 MIT License，详见 [`LICENSE`](LICENSE)。
