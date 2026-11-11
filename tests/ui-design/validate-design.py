#!/usr/bin/env python3
"""validate-design.py — ui-design 设计文档完整性检查（Phase 1 / T4）

用途：
    对 ui-design 工作流生成的 design.md（及配套 design-session.md）做四维完整性检查，
    输出 Design Validation Report。检查通过（READY_FOR_REVIEW）不代表自动冻结，
    最终冻结仍需用户确认（S7）。

用法：
    python tests/ui-design/validate-design.py <design.md> [--session <design-session.md>]
    python tests/ui-design/validate-design.py --selftest

    --session 缺省时，在 design.md 同目录及同级 .ui-design/ 下自动查找。
    exit code：READY_FOR_REVIEW 为 0，FAILED 为 1。

检查维度（对应 skills/ui-design/references/design-review.md）：
    结构完整性  13 章齐全、状态标记齐全且不为 pending、已确认段非占位
    决策完整性  session 解析、pending 清空、confirmed 必须 source=user、
                superseded 链有效、ID 唯一、frozen 一致性、第 13 章对账
    数据完整性  第 9 章已确认非空（来源/字段/口径语义由人工与 AI 复核）
    交互完整性  第 8 章已确认非空（异常态语义由人工与 AI 复核）

依赖：仅 Python 标准库；若环境装有 PyYAML 则优先使用（更稳），否则用内置
YAML 子集解析器（覆盖本项目 frontmatter 所用语法：嵌套映射、对象序列、
内联列表、引号、注释）。
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- YAML 解析

try:
    import yaml as _pyyaml  # type: ignore
except ImportError:
    _pyyaml = None


class YamlParseError(Exception):
    pass


def _strip_inline_comment(value: str) -> str:
    """剥离行内注释：未被引号包裹且前缀为空白的 # 之后的内容全部丢弃。"""
    in_s = in_d = False
    for i, ch in enumerate(value):
        if ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "'" and not in_d:
            in_s = not in_s
        elif ch == "#" and not in_s and not in_d:
            if i == 0 or value[i - 1] in " \t":
                return value[:i]
    return value


def _coerce(value: str):
    """标量值转换：剥离行内注释、去引号、布尔、整数、内联列表。"""
    value = _strip_inline_comment(value).strip()
    if value == "":
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _parse_block(items, pos, indent):
    """解析同一缩进级别的映射或序列，返回 (obj, 新下标)。"""
    seq = None
    mapping = {}
    while pos < len(items):
        ind, content = items[pos]
        if ind < indent:
            break
        if ind > indent:
            raise YamlParseError(f"意外缩进: {content!r}")
        if content.startswith("- "):
            if seq is None:
                seq = []
            item = content[2:].strip()
            pos += 1
            if ":" in item and not item.startswith("["):
                key, val = item.split(":", 1)
                entry = {}
                val = val.strip()
                if val == "":
                    entry[key.strip()] = _parse_block(items, pos, indent + 2)[0]
                else:
                    entry[key.strip()] = _coerce(val)
                # 该序列项的后续键（缩进 = indent + 2），无论首个键值是否为空都要消费
                while pos < len(items) and items[pos][0] == indent + 2 and not items[pos][1].startswith("- "):
                    k2, v2 = items[pos][1].split(":", 1)
                    v2 = v2.strip()
                    pos += 1
                    if v2 == "":
                        entry[k2.strip()] = _parse_block(items, pos, indent + 4)[0]
                    else:
                        entry[k2.strip()] = _coerce(v2)
                seq.append(entry)
            else:
                seq.append(_coerce(item))
            continue
        key, val = content.split(":", 1)
        key, val = key.strip(), val.strip()
        pos += 1
        if val == "":
            child, pos = _parse_block(items, pos, indent + 2)
            mapping[key] = child
        else:
            mapping[key] = _coerce(val)
    if seq is not None and mapping:
        raise YamlParseError("同一层级混用映射与序列")
    return (seq if seq is not None else mapping), pos


def parse_yaml_subset(text: str):
    """解析本项目 frontmatter 所用的 YAML 子集。"""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        items.append((indent, stripped))
    obj, pos = _parse_block(items, 0, 0)
    if pos != len(items):
        raise YamlParseError(f"存在未消费的行: {items[pos]!r}")
    return obj


def parse_frontmatter(fm_text: str):
    """解析 frontmatter，PyYAML 可用时优先使用。"""
    if _pyyaml is not None:
        return _pyyaml.safe_load(fm_text)
    return parse_yaml_subset(fm_text)


def split_frontmatter(path: Path):
    """读取 Markdown 文件，返回 (frontmatter dict, 正文)。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise YamlParseError(f"{path.name} 缺少 YAML frontmatter")
    return parse_frontmatter(m.group(1)), text[m.end():]


# ---------------------------------------------------------------- design.md 结构

EXPECTED_CHAPTERS = [
    "项目背景", "页面目标", "用户与使用场景", "信息架构", "页面布局",
    "内容与组件定义", "视觉设计规范", "交互设计", "数据结构与数据来源",
    "响应式设计", "技术约束", "页面验收标准", "设计决策记录",
]

CHAPTER_HEADING = re.compile(r"^## (\d+)\. (.+)$", re.M)
CHAPTER_STATUS = re.compile(r"> 章节状态：(\w+)")
DECISION_ROW = re.compile(r"^\| (D-\d{3}) \|", re.M)
SUPERSEDED_ROW = re.compile(
    r"^\| (D-\d{3}) \|[^|]+\|[^|]+\|[^|]+\| superseded \|[^|]+\| (D-\d{3}) \|", re.M
)


def strip_comments(block: str) -> str:
    """去掉 HTML 注释（模板占位提示），只留真实内容。"""
    return re.sub(r"<!--.*?-->", "", block, flags=re.S)


def section_between(chapter_text: str, start_pattern: str, end_title: str) -> str:
    r"""截取 **start** 之后到 **end**（或章末）之间的内容。
    start_pattern 为正则（如 r"\*\*已确认\*\*"），end_title 为纯文本标题。"""
    pattern = start_pattern + r"\n(.*?)(?=\n\*\*" + re.escape(end_title) + r"\*\*|\Z)"
    m = re.search(pattern, chapter_text, re.S)
    return m.group(1) if m else ""


def content_bullets(block: str):
    """提取真实内容条目（排除注释占位与空行）。"""
    bullets = []
    for line in strip_comments(block).split("\n"):
        line = line.strip()
        if line.startswith("- ") and len(line) > 2:
            bullets.append(line[2:].strip())
    return bullets


def extract_chapters(body: str):
    """按标题切分章节，返回 [(编号, 标题, 状态, 已确认条目, 待确认条目)]。"""
    matches = list(CHAPTER_HEADING.finditer(body))
    chapters = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[m.end():end]
        status_m = CHAPTER_STATUS.search(chunk)
        chapters.append({
            "num": int(m.group(1)),
            "title": m.group(2).strip(),
            "status": status_m.group(1) if status_m else None,
            "confirmed": content_bullets(section_between(chunk, r"\*\*已确认\*\*", "待确认")),
            "open": content_bullets(section_between(chunk, r"\*\*待确认\*\*", "约束")),
        })
    return chapters


# ---------------------------------------------------------------- 检查逻辑

class Report:
    def __init__(self):
        self.dimensions = {}
        self.details = {}
        self.unconfirmed = 0
        self.manual_items = []

    def fail(self, dim, reasons):
        self.dimensions[dim] = "FAIL"
        self.details.setdefault(dim, []).extend(reasons)


def find_session(design_path: Path, explicit):
    if explicit:
        return Path(explicit)
    for candidate in (design_path.parent / "design-session.md",
                      design_path.parent / ".ui-design" / "design-session.md"):
        if candidate.exists():
            return candidate
    return None


def validate(design_path: Path, session_path):
    report = Report()
    fm, body = split_frontmatter(design_path)
    chapters = extract_chapters(body)

    # ---- 结构完整性
    reasons = []
    nums = [c["num"] for c in chapters]
    if nums != list(range(1, 14)):
        missing = sorted(set(range(1, 14)) - set(nums))
        reasons.append(f"章节缺失或顺序错误，缺失编号: {missing}")
    for c in chapters:
        if c["num"] <= len(EXPECTED_CHAPTERS) and c["title"] != EXPECTED_CHAPTERS[c["num"] - 1]:
            report.manual_items.append(
                f"第 {c['num']} 章标题「{c['title']}」与标准章节「{EXPECTED_CHAPTERS[c['num'] - 1]}」不一致，请确认是否有意调整")
    for c in chapters:
        if c["status"] is None:
            reasons.append(f"第 {c['num']} 章缺少「章节状态」标记")
        elif c["status"] == "pending":
            reasons.append(f"第 {c['num']} 章（{c['title']}）状态为 pending")
        # 第 13 章的内容是决策表而非已确认段，表行也计入有效内容
        if c["num"] == 13:
            chunk_text = ""
            has_table = False
            if "## 13." in body:
                chunk_text = body[body.index("## 13."):]
                has_table = bool(DECISION_ROW.search(chunk_text))
            if not c["confirmed"] and not has_table:
                reasons.append("第 13 章（设计决策记录）无决策表也无已确认内容")
        elif not c["confirmed"]:
            reasons.append(f"第 {c['num']} 章（{c['title']}）已确认段无真实内容（仅占位注释）")
    fm_status = fm.get("status")
    fm_frozen = fm.get("frozen")
    if "schema_version" not in fm:
        reasons.append("frontmatter 缺少 schema_version")
    if fm_status not in ("draft", "review", "frozen"):
        reasons.append(f"frontmatter status 非法: {fm_status!r}")
    if fm_frozen and fm_status != "frozen":
        reasons.append("frontmatter frozen=true 但 status 不是 frozen")
    if reasons:
        report.fail("结构完整性", reasons)
    else:
        report.dimensions["结构完整性"] = "PASS"

    # ---- 决策完整性（需要 session）
    session = None
    if session_path is None or not session_path.exists():
        report.fail("决策完整性", ["未找到 design-session.md（用 --session 指定或置于 .ui-design/ 下）"])
    else:
        sfm, _ = split_frontmatter(session_path)
        session = sfm
        reasons = []
        decisions = sfm.get("decisions") or []
        pending = sfm.get("pending") or []
        if pending:
            reasons.append(f"待确认问题池未清空: {[q.get('id') for q in pending]}")
        ids = [d.get("id") for d in decisions]
        if len(ids) != len(set(ids)):
            reasons.append("存在重复的决策 ID")
        by_id = {}
        for d in decisions:
            did = d.get("id", "")
            if not re.fullmatch(r"D-\d{3}", str(did)):
                reasons.append(f"决策 ID 格式非法: {did!r}")
                continue
            by_id[did] = d
            if d.get("status") == "confirmed" and d.get("source") != "user":
                reasons.append(f"{did} 标记为 confirmed 但 source 不是 user（AI 建议不得自动确认）")
            if d.get("status") == "superseded":
                target = d.get("superseded_by")
                if target is None:
                    reasons.append(f"{did} 状态为 superseded 但缺少 superseded_by")
                elif target not in by_id and target not in ids:
                    pass  # 占位，统一在收集完 ids 后检查
        for did, d in by_id.items():
            if d.get("status") == "superseded":
                target = by_id.get(d.get("superseded_by"))
                if target is None:
                    reasons.append(f"{did} 的替代决策 {d.get('superseded_by')} 不存在")
                elif target.get("status") != "confirmed":
                    reasons.append(f"{did} 的替代决策 {d.get('superseded_by')} 状态不是 confirmed")
        # 冻结一致性
        s = sfm.get("session", {})
        if s.get("frozen"):
            if s.get("stage") != "FROZEN":
                reasons.append("session frozen=true 但 stage 不是 FROZEN")
            if s.get("status") != "completed":
                reasons.append("session frozen=true 但 status 不是 completed")
        if fm_frozen and not s.get("frozen"):
            reasons.append("design.md 已冻结但 session 未标记冻结")
        # 第 13 章对账
        ch13 = next((c for c in chapters if c["num"] == 13), None)
        if ch13 is not None:
            body_end = body[body.index("## 13."):] if "## 13." in body else ""
            table_ids = set(DECISION_ROW.findall(body_end))
            if table_ids != set(ids):
                only_md = sorted(table_ids - set(ids))
                only_ses = sorted(set(ids) - table_ids)
                reasons.append(f"第 13 章决策表与 session 不一致（仅文档有: {only_md}，仅 session 有: {only_ses}）")
            sup_md = dict(SUPERSEDED_ROW.findall(body_end))
            sup_ses = {d["id"]: d["superseded_by"] for d in decisions
                       if d.get("status") == "superseded"}
            if sup_md != sup_ses:
                reasons.append(f"第 13 章 superseded 标注与 session 不一致: 文档 {sup_md} vs session {sup_ses}")
        if reasons:
            report.fail("决策完整性", reasons)
        else:
            report.dimensions["决策完整性"] = "PASS"

    # ---- 数据完整性（第 9 章）
    ch9 = next((c for c in chapters if c["num"] == 9), None)
    data_reasons = []
    if ch9 is None:
        data_reasons.append("第 9 章不存在")
    elif ch9["status"] != "confirmed" or not ch9["confirmed"]:
        data_reasons.append("第 9 章（数据结构与数据来源）未确认或无内容")
    else:
        report.manual_items.append("第 9 章数据口径与字段语义需人工/AI 复核（脚本只查结构）")
    if data_reasons:
        report.fail("数据完整性", data_reasons)
    else:
        report.dimensions["数据完整性"] = "PASS"

    # ---- 交互完整性（第 8 章）
    ch8 = next((c for c in chapters if c["num"] == 8), None)
    inter_reasons = []
    if ch8 is None:
        inter_reasons.append("第 8 章不存在")
    elif ch8["status"] != "confirmed" or not ch8["confirmed"]:
        inter_reasons.append("第 8 章（交互设计）未确认或无内容")
    else:
        report.manual_items.append("交互异常态（加载失败/空态）是否覆盖需人工/AI 复核（脚本只查结构）")
    if inter_reasons:
        report.fail("交互完整性", inter_reasons)
    else:
        report.dimensions["交互完整性"] = "PASS"

    # ---- 未确认事项统计
    partial = [c["num"] for c in chapters if c["status"] == "partial"]
    open_bullets = sum(len(c["open"]) for c in chapters)
    session_pending = len((session or {}).get("pending") or [])
    report.unconfirmed = len(partial) + open_bullets + session_pending
    if partial:
        report.manual_items.append(f"部分确认（partial）章节: {partial}")

    return report


def format_report(design_path, session_path, report):
    lines = ["Design Validation Report", ""]
    lines.append(f"目标: {design_path}"
                 + (f"（session: {session_path}）" if session_path else "（无 session）"))
    lines.append("")
    for dim in ("结构完整性", "决策完整性", "数据完整性", "交互完整性"):
        status = report.dimensions.get(dim, "FAIL")
        lines.append(f"{dim}：{status}")
        for reason in report.details.get(dim, []):
            lines.append(f"  - {reason}")
    lines.append("")
    lines.append(f"未确认事项：{report.unconfirmed}")
    if report.manual_items:
        lines.append("")
        lines.append("人工复核项：")
        for item in report.manual_items:
            lines.append(f"  - {item}")
    final = "READY_FOR_REVIEW" if (
        all(v == "PASS" for v in report.dimensions.values())
        and report.unconfirmed == 0
    ) else "FAILED"
    lines.append("")
    lines.append(f"最终状态：{final}")
    return final, "\n".join(lines)


def main(argv):
    if "--selftest" in argv:
        return selftest()
    parser = argparse.ArgumentParser(description="ui-design 设计文档完整性检查")
    parser.add_argument("design", help="design.md 路径")
    parser.add_argument("--session", help="design-session.md 路径（缺省自动查找）")
    args = parser.parse_args(argv)
    design_path = Path(args.design)
    if not design_path.exists():
        print(f"文件不存在: {design_path}", file=sys.stderr)
        return 1
    session_path = find_session(design_path, args.session)
    report = validate(design_path, session_path)
    final, text = format_report(design_path, session_path, report)
    print(text)
    return 0 if final == "READY_FOR_REVIEW" else 1


# ---------------------------------------------------------------- 自检

def selftest():
    """对内置正反用例跑断言，任何一条失败即 exit 1。"""
    root = Path(__file__).resolve().parents[2]
    failures = []

    def expect(name, cond, extra=""):
        print(f"  [{'通过' if cond else '失败'}] {name}" + (f" {extra}" if extra and not cond else ""))
        if not cond:
            failures.append(name)

    # 正向：Dashboard 冻结案例必须 READY_FOR_REVIEW
    example = root / "examples" / "dashboard" / "design.md"
    report = validate(example, example.parent / "design-session.md")
    final, text = format_report(example, example.parent / "design-session.md", report)
    expect("Dashboard 案例为 READY_FOR_REVIEW", final == "READY_FOR_REVIEW", f"\n{text}")

    # 回退解析器回归：不依赖 PyYAML 的结构断言
    ses_fm = parse_frontmatter(re.match(r"^---\n(.*?)\n---\n",
        (example.parent / "design-session.md").read_text(encoding="utf-8"), re.S).group(1))
    expect("回退解析器读出 14 个决策", len(ses_fm.get("decisions", [])) == 14,
           str(len(ses_fm.get("decisions", []))))
    expect("回退解析器读出项目名",
           ses_fm.get("project", {}).get("name") == "prd-quality-dashboard",
           str(ses_fm.get("project", {}).get("name")))

    # 反向：坏文档必须 FAILED 且给出对应原因
    broken = root / "tests" / "ui-design" / "cases" / "broken-dashboard-design.md"
    if not broken.exists():
        expect("反向用例文件存在", False, f"缺少 {broken}")
    else:
        report = validate(broken, broken.parent / "broken-dashboard-design-session.md")
        final, text = format_report(broken, broken.parent / "broken-dashboard-design-session.md", report)
        expect("坏文档为 FAILED", final == "FAILED")
        joined = "".join(sum(report.details.values(), []))
        for keyword in ("章节缺失", "状态为 pending", "source 不是 user",
                        "替代决策", "待确认问题池未清空", "不一致"):
            expect(f"检测到问题: {keyword}", keyword in joined)
        expect("坏文档未确认事项 > 0", report.unconfirmed > 0)

    print()
    if failures:
        print(f"自检失败 {len(failures)} 项")
        return 1
    print("自检全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
