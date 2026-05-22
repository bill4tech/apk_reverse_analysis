---
name: apk-reverse-analysis
description: "对指定文件夹下所有 APK 文件进行自动化反编译技术分析，输出可对比的风格化 HTML 报告。触发词：'分析APK'、'技术对标'、'竞品分析'、'benchmark分析'、'技术评估'、'拆解app'、'app对标'。"
---

# APK 反编译技术分析

对指定文件夹下所有 APK 文件进行自动化逆向分析，输出风格化 HTML 技术分析报告。

## 工作流

### Step 1：发现 APK

用户提供文件夹路径后，用 `find` 查找所有 `.apk` 和 `.xapk` 文件：

```bash
find <folder_path> -maxdepth 3 -type f \( -iname "*.apk" -o -iname "*.xapk" \)
```

如果没有找到 APK，告知用户并结束。

找到后，列出文件名和大小给用户确认。

### Step 2：提取数据

对**每个** APK 并行执行提取脚本：

```bash
python3 {skill_dir}/extract_apk.py "<apk_path>"
```

脚本输出 JSON 到 stdout，包含：包名、版本、targetSdk、权限、组件数、类数量、Native 库列表、包名前缀统计、框架标记等。

将每个 APK 的 JSON 结果保存到临时文件，方便后续分析。

### Step 3：AI 分析

阅读所有 JSON，执行以下维度的分析：

#### 3.1 框架识别

| 信号 | 结论 |
|---|---|
| `framework_markers.react_native == true` | React Native |
| `package_prefixes` 有 `com.facebook.react` | React Native |
| `framework_markers.fluter == true` | Flutter |
| `package_prefixes` 有 `io.flutter` | Flutter |
| `has_kotlin == true` + 无跨平台标志 | Kotlin 原生 |
| `framework_markers.unity == true` | Unity 游戏 |
| `framework_markers.cordova == true` | Cordova/混合 |
| 有 `index.android.bundle` 在 assets | React Native (Hermes JS bundle) |

#### 3.2 SDK / 第三方服务识别

以 `package_prefixes` 为核心线索，识别知名 SDK：

| 包名前缀 | 服务 |
|---|---|
| `com.google.firebase` | Firebase |
| `com.google.android.gms` | Google Play Services |
| `com.appsflyer` | AppsFlyer（归因） |
| `com.adjust` | Adjust（归因） |
| `cn.thinkingdata` / `cn.data` | ThinkingData 数数科技 |
| `com.tencent.mmkv` | 腾讯 MMKV |
| `com.tencent.pag` / `libpag` | 腾讯 PAG 动画 |
| `com.dianping.logan` / `com.meituan.android.common` | 美团 Logan 日志 |
| `com.aliyun` / `com.alibaba.sdk.android.oss` | 阿里云 OSS |
| `com.facebook` (非 react) | Facebook SDK |
| `com.bytedance` | 字节跳动 SDK |
| `com.squareup.okhttp` / `okhttp3` | OkHttp |
| `com.squareup.retrofit` | Retrofit |
| `com.bumptech.glide` | Glide |
| `com.github.bumptech` | Glide (新) |
| `com.facebook.fresco` | Fresco |
| `com.google.android.exoplayer` / `androidx.media3` | ExoPlayer / Media3 |
| `com.google.protobuf` | Protobuf |
| `com.google.gson` | Gson |
| `com.hihonor` | 荣耀 SDK |
| `com.huawei` / `com.huawei.hms` | 华为 HMS |
| `com.samsung` | 三星 SDK |
| `com.android.billingclient` | Google Play Billing |

识别所有命中项，生成每个 APK 的第三方服务清单。

#### 3.3 产品形态推理

综合以下信号推理产品类型：

- **AI 聊天/陪伴**：包名含 chat/ai/companion + SSE/WebSocket 网络 + 角色扮演相关类名
- **社交媒体**：大量图片处理 SDK + UGC 相关类
- **工具应用**：权限少 + 功能集中
- **游戏**：Unity/Cocos + so 库多
- **视频/直播**：ExoPlayer/Media3 + 推流 SDK

#### 3.4 Native 库分析

- 提取 `native_libs` 中的关键 so 文件名（忽略系统库）
- 统计支持的 CPU 架构（armeabi-v7a、arm64-v8a、x86、x86_64）

#### 3.5 技术亮点与差异性

- 对比各 APK 的技术选型差异
- 识别值得关注的技术方案（如自研模块、特殊 SDK）
- 评估技术成熟度（versionCode 大小、类数量）
- 识别可能的共同团队（包名模式相同）

### Step 4：生成 HTML

根据 APK 数量生成自适应 HTML 报告，写入当前工作目录。

**文件命名**：`<YYYYMMDD>-<HHmm>-tech-analysis.html`

## HTML 生成规范

### 样式

采用内联 CSS，参考以下风格：
- 背景 `#f8f9fa`，字体 `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- 主色调 `#4a90d9` 蓝色
- 表格 `border-collapse: collapse` + 斑马纹
- 标签 `.tag` 带圆角背景色：
  - `.tag-blue` → React Native/TypeScript
  - `.tag-orange` → Kotlin/原生
  - `.tag-green` → Flutter
  - `.tag-red` → 高风险/注意
  - `.tag-purple` → 自研/特殊
- `.summary-box` → 左侧蓝色边框总结框
- `.check` → 绿色 ✅
- `.cross` → 红色 ❌

### 结构（自适应 APK 数量）

**1 个 APK**：单列展示
```
标题 + 日期
一、基本信息（表格，属性→值）
二、技术方案（表格，层面→技术选型）
三、第三方服务（表格，服务名+用途）
四、权限分析（表格，权限→用途推理）
五、业务特征（列表）
六、总结
```

**2+ APK**：对比格式
```
标题 + 日期
一、基本信息（对比表格：表头=维度 | APK1 | APK2 | ...）
二、技术方案对比（对比表格：表头=层面 | APK1 | APK2 | ...）
三、第三方服务对比（对比表格，✅❌ 标注）
四、核心业务特征（每个 APK 单独小标题+列表）
五、总结（对比性总结，总结框）
```

### 内容要求

- 使用中文
- 技术名称保持原文（如 React Native、Firebase）
- 对于不确定的判断，用「疑似」「可能」等措辞
- 总结部分要有对比性结论，而非复述前面内容
- 每个表格下方如有重要补充可用 `<p>` 标注

## 注意事项

1. 如果 APK 已加固（DEX 解析失败），JSON 中 `class_count` 为 0，在报告中标注「已加固」
2. 如遇 `.xapk` 文件，先解压再取其中的 `.apk` 分析
3. 大型 APK 分析耗时较长，注意给用户进度反馈
4. 生成的 HTML 文件路径在最后明确告知用户
