#!/usr/bin/env python3
"""
APK 信息提取器 — 仅提取纯事实数据，不做任何分析判断。
用法: python3 extract_apk.py <apk_path>
输出: JSON 到 stdout
"""

import sys
import json
import os
from collections import Counter

# 抑制 androguard 的 DEBUG/INFO 日志（使用 loguru）
from loguru import logger
logger.disable("androguard")

from androguard.misc import AnalyzeAPK


def extract_prefixes(class_names):
    """从类名中提取包名前缀并统计频次。

    例: com.google.firebase.analytics.FirebaseAnalytics
      → {"com.google": 1, "com.google.firebase": 1, "com.google.firebase.analytics": 1}
    """
    prefixes = Counter()
    for cls in class_names:
        # 类名格式: Lpak/age/name/ClassName; → 转换成 pak.age.name.ClassName
        cls = cls.lstrip("L").rstrip(";").replace("/", ".")
        parts = cls.split(".")
        for depth in range(2, len(parts)):
            prefix = ".".join(parts[:depth])
            prefixes[prefix] += 1
    return prefixes


def extract_apk_info(apk_path):
    result = {
        "file_name": os.path.basename(apk_path),
        "file_size_mb": round(os.path.getsize(apk_path) / (1024 * 1024), 2),
    }

    try:
        apk, dex_list, _ = AnalyzeAPK(apk_path)

        # — 基本信息 —
        result["package_name"] = apk.get_package()
        result["version_name"] = apk.get_androidversion_name()
        result["version_code"] = apk.get_androidversion_code()
        result["target_sdk"] = apk.get_target_sdk_version()
        result["min_sdk"] = apk.get_min_sdk_version()
        result["max_sdk"] = apk.get_max_sdk_version()

        # — 权限 —
        result["permissions"] = sorted(apk.get_permissions())

        # — 四大组件计数 —
        result["component_counts"] = {
            "activities": len(apk.get_activities()),
            "services": len(apk.get_services()),
            "receivers": len(apk.get_receivers()),
            "providers": len(apk.get_providers()),
        }

        # — 文件清单 —
        all_files = apk.get_files()
        result["native_libs"] = sorted(
            [f for f in all_files if f.startswith("lib/") and f.endswith(".so")]
        )
        result["assets_files"] = sorted(
            [f for f in all_files if f.startswith("assets/")]
        )

        # — 框架标记 —
        assets_text = " ".join(result["assets_files"]).lower()
        all_files_text = " ".join(all_files).lower()
        result["framework_markers"] = {
            "react_native": any(
                k in assets_text for k in ["index.android.bundle", "react-native"]
            ),
            "fluter": "flutter_assets" in assets_text,
            "unity": "unity" in all_files_text,
            "cordova": "cordova" in assets_text,
            "xamarin": "mono" in all_files_text,
        }

        # — DEX 解析 —
        class_count = 0
        all_classes = []

        for dex in dex_list:
            try:
                classes = dex.get_classes_names()
                class_count += len(classes)
                all_classes.extend(classes)
            except Exception:
                pass

        result["class_count"] = class_count

        if all_classes:
            prefixes = extract_prefixes(all_classes)
            # 保留出现 >= 3 次的前缀，按频次降序
            significant = {k: v for k, v in prefixes.items() if v >= 3}
            result["package_prefixes"] = dict(
                sorted(significant.items(), key=lambda x: -x[1])
            )
        else:
            result["package_prefixes"] = {}

        # Kotlin 检测
        result["has_kotlin"] = any(
            "kotlin" in cls.lower() for cls in all_classes
        ) or any("kotlin" in f.lower() for f in all_files)

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_apk.py <apk_path>", file=sys.stderr)
        sys.exit(1)

    apk_path = sys.argv[1]
    if not os.path.exists(apk_path):
        print(f"Error: file not found: {apk_path}", file=sys.stderr)
        sys.exit(1)

    result = extract_apk_info(apk_path)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
