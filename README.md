# APK 反编译技术分析 · APK Reverse Analysis

> 一个 Claude Code Agent Skill，对指定文件夹下所有 APK 文件进行**自动化反编译技术分析**，输出可对比的风格化 HTML 报告。适合竞品技术评估、技术对标、安全研究等场景。

[English Summary](#english-summary) | [快速开始](#快速开始) | [它能做什么](#它能做什么) | [反馈](#反馈与贡献)

---

## 这是什么

本 Skill 是一个 Claude Code 的自定义 Agent 能力，激活后能够自动完成以下流程：

1. 扫描指定目录发现所有 `.apk` / `.xapk` 文件
2. 对每个 APK 进行逆向提取（基于 androguard）—— 包括包名、版本、权限、组件、类、Native 库等纯事实数据
3. 结合 AI 分析引擎对提取数据进行深度解读 —— 框架识别、SDK 清单、产品形态推理
4. 生成风格化的多维度 HTML 技术分析报告

**核心理念**：将「人工逆向分析」的专家经验（看包名识 SDK、看权限猜业务、看框架定技术栈）编码为结构化的分析流程，让机器来执行重复劳动，人只做最终判断。

## 它能做什么

### 6 大分析工作流

| 工作流 | 说明 |
|---|---|
| **APK 发现与校验** | 自动扫描目录，识别 APK/XAPK，文件大小校验，用户确认 |
| **数据提取** | 基于 androguard 提取包名、版本、权限、四大组件、类数量、Native 库、assets 清单等 20+ 维度 |
| **框架识别** | 自动判断 React Native / Flutter / Kotlin 原生 / Unity / Cordova / Xamarin |
| **SDK 第三方服务清单** | 从包名前缀反向识别 Firebase、声网、网易云信、字节特效 SDK、Facebook 等 30+ 常见 SDK |
| **产品形态推理** | 综合 SDK 组合、权限模式、组件结构推断产品类型（社交/工具/游戏/视频等） |
| **HTML 报告生成** | 自适应单 APK / 多 APK 对比模式，内联 CSS，中文输出 |

### 3 大全局协议

| 协议 | 说明 |
|---|---|
| **进度反馈协议** | 每一步操作都向用户汇报进度，大型 APK 分析耗时较长时主动提示 |
| **不确定性标注协议** | 所有基于静态分析的推断必须使用「疑似」「可能」等措辞，不说绝对话 |
| **结果交付协议** | 明确告知 HTML 报告文件路径，并提供关键结论摘要 |

## 适用场景

| 场景 | 效果 |
|---|---|
| **竞品技术对标** | 批量对比多个竞品 APK 的技术选型差异，生成对照报告 |
| **技术尽职调查** | 评估目标应用的技术成熟度、使用了哪些第三方 SDK、是否有跨平台方案 |
| **安全研究** | 提取权限清单、Native 库分析、识别已知 SDK 版本漏洞 |
| **产品逆向还原** | 从权限 + 组件 + SDK 组合推断产品功能模块和业务逻辑 |
| **技术选型调研** | 分析同品类头部应用的技术栈，为自己的技术选型提供参考 |

## 快速开始

### 1. 安装

将本项目克隆到 Claude Code 的 skills 目录：

```bash
# macOS / Linux
cp -r apk-reverse-analysis ~/.claude/skills/

# 或者使用 Git 克隆
git clone <repo-url> ~/.claude/skills/apk-reverse-analysis
```

**依赖安装**：

```bash
pip install androguard loguru
```

### 2. 触发

在 Claude Code 对话中直接使用以下触发词：

> 「分析 APK」「技术对标」「竞品分析」「benchmark 分析」「技术评估」「拆解 app」「app 对标」

示例对话：

```
用户：帮我分析 ~/Downloads/apps/ 这个目录下的 APK
助手：扫描到 3 个 APK 文件：
  1. app-release.apk (42.3 MB)
  2. com.example-v1.2.3.apk (28.1 MB)
  3. game.xapk (156.8 MB)
是否开始分析？
```

### 3. 上传材料建议

| 材料类型 | 说明 |
|---|---|
| **单个 APK** | 直接给路径，生成单 APK 详细报告 |
| **多个 APK** | 放入同目录，自动生成横向对比报告 |
| **XAPK** | 兼容处理，自动解压后提取主 APK |

## 项目结构

```
apk-reverse-analysis/
├── skill.md              # 主控：6 步工作流 + 3 大全局协议
├── extract_apk.py        # 数据提取器：基于 androguard 提取纯事实 JSON
├── generate_report.py    # 报告生成器：生成风格化 HTML（单 APK / 对比模式）
├── README.md             # 本文档
```

## 分析维度详解

### 框架识别信号表

| 信号 | 结论 |
|---|---|
| `index.android.bundle` 或 `react-native` 在 assets 中 | React Native |
| `flutter_assets` 在 assets 中 | Flutter |
| `unity` 在文件清单中 | Unity 游戏 |
| `cordova` 在 assets 中 | Cordova / 混合 |
| `kotlin` 在类名或文件中 | 含 Kotlin 代码 |
| 无跨平台标志 + 有 Kotlin | Kotlin 原生 |

### 第三方 SDK 识别库（内置 30+ 条规则）

覆盖 Firebase、Google Play Services、声网 Agora、网易云信、字节跳动 Effects SDK、AppsFlyer、Adjust、阿里云 OSS、腾讯 MMKV/PAG、Facebook SDK、OkHttp、Retrofit、Glide、Fresco、ExoPlayer 等主流 SDK。

### 报告结构（自适应）

**1 个 APK** → 单列详细报告：
基本信息 → 技术方案 → 第三方服务 → 权限分析 → 业务特征 → 技术亮点 → 总结

**2+ APK** → 横向对比报告：
基本信息对比 → 技术方案对比 → 第三方服务矩阵（✅❌） → 各 APK 业务特征 → 对比性总结

## 设计原则

1. **事实与推断分离** — `extract_apk.py` 只输出纯事实数据，所有判断交由 AI 分析层
2. **从现象到本质** — 不罗列数据，而是解释「这个权限意味着什么」「这个 SDK 组合说明了什么」
3. **不确定性标注** — 静态分析有局限，所有推断必须用「疑似」「可能」措辞
4. **横向对比优先** — 多个 APK 时优先输出对比性结论而非各自独立描述
5. **渐进式反馈** — 长时间操作必须给用户阶段性进度提示

## 反馈与贡献

- Bug 报告 / 新 SDK 识别规则 → 提交 Issue
- PR 欢迎：
  - 新增 SDK 识别规则（包名 → 服务名称映射）
  - 新增分析维度（如网络请求分析、资源分析）
  - 改善报告样式和交互
  - 补充 XAPK / 分体 APK 兼容处理

## English Summary

**APK Reverse Analysis Skill** — A Claude Code custom skill for automated APK reverse engineering and technology analysis.

It scans a directory for APK/XAPK files, extracts structural data using androguard (package name, version, permissions, components, classes count, native libraries, assets), then applies AI-powered analysis to identify frameworks (React Native/Flutter/Kotlin/Unity/Cordova), third-party SDKs, and infer product characteristics.

The output is a styled Chinese-language HTML report that adapts between single-APK detail mode and multi-APK comparison mode. Designed for competitive tech benchmarking, technical due diligence, and security research.

**Key stats**: 6 analysis workflows, 3 global protocols, 30+ SDK recognition rules, dual-mode HTML report engine.

## License

MIT
