import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

from openai import OpenAI
import openai
from dotenv import load_dotenv


def find_db_path() -> Path:
    here = Path(__file__).resolve().parent
    return here / "names_corpus.db"


def ensure_dynasty_column(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ancient_names)")
    cols = [row[1] for row in cur.fetchall()]
    if "dynasty" not in cols:
        cur.execute("ALTER TABLE ancient_names ADD COLUMN dynasty TEXT")
        conn.commit()


def fetch_unclassified_names(conn: sqlite3.Connection, limit: int, offset: int = 0) -> List[str]:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ancient_names)")
    cols = [row[1] for row in cur.fetchall()]
    base = "SELECT name FROM ancient_names WHERE (dynasty IS NULL OR dynasty = '')"
    if "density" in cols:
        base += " AND (density IS NULL OR density = '')"
    base += " ORDER BY ROWID LIMIT ?"
    cur.execute(base, (limit,))
    rows = cur.fetchall()
    return [r[0] for r in rows]


def normalize_dynasty(s: str) -> Optional[str]:
    if not s:
        return None
    t = str(s).strip().lower()
    mapping = {
        "pre_qin": "先秦", "prehistoric": "先秦", "xianqin": "先秦", "先秦": "先秦", "春秋": "先秦", "战国": "先秦",
        "qin": "秦", "秦": "秦", "秦代": "秦",
        "han": "汉", "汉": "汉", "漢": "汉", "汉代": "汉",
        "jin": "晋", "晋": "晋", "晉": "晋", "魏晋": "晋", "魏晋南北朝": "南北朝",
        "southern_and_northern_dynasties": "南北朝", "nanbeichao": "南北朝", "南北朝": "南北朝",
        "sui": "隋", "隋": "隋", "隋代": "隋",
        "tang": "唐", "唐": "唐", "唐代": "唐",
        "five_dynasties": "五代十国", "five_dynasties_and_ten_kingdoms": "五代十国", "五代十国": "五代十国", "五代十國": "五代十国", "五代": "五代十国",
        "song": "宋", "宋": "宋", "宋代": "宋",
        "liao": "辽", "辽": "辽", "遼": "辽", "辽代": "辽", "遼代": "辽",
        "jin_dynasty_later": "金", "jurchen_jin": "金", "jin_later": "金", "金": "金",
        "yuan": "元", "元": "元", "元代": "元",
        "ming": "明", "明": "明", "明代": "明",
        "qing": "清", "清": "清", "清代": "清",
        "modern": "近现代", "contemporary": "近现代", "republic": "近现代", "民国": "近现代", "近現代": "近现代", "現代": "近现代",
    }
    if t in mapping:
        return mapping[t]
    if s in ["先秦", "秦", "汉", "晋", "南北朝", "隋", "唐", "五代十国", "宋", "辽", "金", "元", "明", "清", "近现代"]:
        return s
    return None


def classify_batch(client: OpenAI, model: str, names: List[str]) -> Dict[str, str]:
    sys_prompt = (
        "你是历史学者。任务：将输入的古代中文人名划分到以下之一："
        "先秦、秦、汉、晋、南北朝、隋、唐、五代十国、宋、辽、金、元、明、清。"
        "只输出JSON，键为name，值为朝代，值必须严格使用上述中文标签之一。"
        "若不确定，也必须选择最可能的一个，不要输出任何非JSON文本。"
    )
    user_payload = {"names": names}
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]
    attempts = 0
    backoff = 5
    while True:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                max_tokens=2048,
                temperature=0.2,
                top_p=0.8,
                response_format={"type": "json_object"},
            )
            break
        except openai.RateLimitError:
            attempts += 1
            if attempts > 6:
                return {}
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
        except Exception as e:
            # 某些SDK实现用一般异常承载429
            if 'RATE_LIMIT' in repr(e) or getattr(e, 'status_code', None) == 429:
                attempts += 1
                if attempts > 6:
                    return {}
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
            else:
                raise
    content = resp.choices[0].message.content if resp.choices else ""
    result = {}
    def _sanitize(text: str) -> str:
        s = text.strip()
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("`").strip()
            if s.lower().startswith("json"):
                s = s[4:].strip()
        import re
        s = re.sub(r',\s*([}\]])', r'\1', s)
        s = re.sub(r'(?<=\{|,)\s*([A-Za-z0-9_\u4e00-\u9fff]+)\s*:', lambda m: f'"{m.group(1)}":', s)
        s = re.sub(r'“([^”]+)”', r'"\1"', s)
        s = re.sub(r'‘([^’]+)’', r'"\1"', s)
        s = re.sub(r'：', ':', s)
        s = re.sub(r'，', ',', s)
        return s
    def _extract_pairs(text: str) -> Dict[str, str]:
        import re
        pairs = {}
        pat = re.findall(r'["“”]?([\u4e00-\u9fff]{2,})["“”]?\s*[:：]\s*["“”]?([先秦秦汉晋南北朝隋唐五代十国宋辽金元明清近现代])["“”]?', text)
        for n, d in pat:
            dn = normalize_dynasty(d)
            if dn:
                pairs[str(n)] = dn
        return pairs
    try:
        cleaned = _sanitize(content)
        data = json.loads(cleaned)
        if isinstance(data, dict):
            for k, v in data.items():
                dn = normalize_dynasty(v)
                if dn:
                    result[str(k)] = dn
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    n = item.get("name")
                    dyn = item.get("dynasty") or item.get("value") or item.get("era")
                    d = normalize_dynasty(dyn)
                    if n and d:
                        result[str(n)] = d
    except Exception:
        import re
        try:
            objs = re.findall(r'\{[\s\S]*?\}', _sanitize(content))
            for obj in objs:
                try:
                    item = json.loads(obj)
                except Exception:
                    continue
                if isinstance(item, dict):
                    n = item.get("name")
                    dyn = item.get("dynasty") or item.get("value") or item.get("era")
                    d = normalize_dynasty(dyn)
                    if n and d:
                        result[str(n)] = d
        except Exception:
            pass
    if not result:
        pairs = _extract_pairs(content)
        if pairs:
            result.update(pairs)
    if not result and content:
        try:
            preview = content[:200].replace("\n", " ")
            print(f"模型返回预览: {preview}")
        except Exception:
            pass
    return result


def update_dynasty(conn: sqlite3.Connection, mapping: Dict[str, str]) -> int:
    cur = conn.cursor()
    count = 0
    for name, dynasty in mapping.items():
        cur.execute(
            "UPDATE ancient_names SET dynasty = ? WHERE name = ? AND (dynasty IS NULL OR dynasty = '')",
            (dynasty, name),
        )
        count += cur.rowcount
    conn.commit()
    return count


def main():
    # 加载项目根目录的 .env
    try:
        project_root = Path(__file__).resolve().parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path))
    except Exception:
        pass

    api_key = os.getenv("PAIOU_API_KEY")
    base_url = os.getenv("PAIOU_BASE_URL", "https://api.ppinfra.com/openai")
    model = os.getenv("PAIOU_MODEL", "deepseek/deepseek-v3-0324")
    batch_size = int(os.getenv("DYNASTY_BATCH_SIZE", "50"))
    max_rows = int(os.getenv("DYNASTY_MAX_ROWS", "1000"))

    if not api_key:
        print("PAIOU_API_KEY 未设置")
        sys.exit(1)

    client = OpenAI(base_url=base_url, api_key=api_key)

    db_path = find_db_path()
    if not db_path.exists():
        print(f"数据库不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    try:
        ensure_dynasty_column(conn)
        processed = 0
        while processed < max_rows:
            names = fetch_unclassified_names(conn, limit=batch_size, offset=0)
            if not names:
                break
            mapping = classify_batch(client, model, names)
            if mapping:
                updated = update_dynasty(conn, mapping)
            else:
                updated = 0
            processed += len(names)
            print(
                f"批次完成: 输入 {len(names)} 个, 成功更新 {updated} 个, 总处理 {processed}"
            )
            time.sleep(0.2)
        print("完成")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
