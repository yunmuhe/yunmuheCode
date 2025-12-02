"""
中文人名语料库加载器（SQLite版本）
从SQLite数据库加载姓名语料库数据
"""
import os
import random
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path


class CorpusLoader:
    """语料库加载器（使用SQLite数据库）"""

    def __init__(self, db_path: str = None):
        """
        初始化语料库加载器

        Args:
            db_path: 数据库文件路径，默认为 data/names_corpus.db
        """
        if db_path is None:
            # 默认路径：项目根目录的data目录
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / 'data' / 'names_corpus.db'

        self.db_path = Path(db_path)

        # 检查数据库是否存在
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"语料库数据库不存在: {self.db_path}\n"
                f"请运行 python data/convert_csv_to_sqlite.py 生成数据库"
            )

        # 缓存连接（每次查询时创建新连接以避免线程安全问题）
        self._connection = None

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 使结果可以用列名访问
        return conn

    def load_names(self, with_gender: bool = False, limit: int = None) -> List[str] | List[Dict[str, str]]:
        """
        加载中文人名语料库

        Args:
            with_gender: 是否包含性别信息
            limit: 限制加载数量，None表示全部加载

        Returns:
            人名列表，如果with_gender=True则返回字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT name, gender FROM chinese_names"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()

            if with_gender:
                return [{'name': row['name'], 'gender': row['gender']} for row in rows]
            else:
                return [row['name'] for row in rows]
        finally:
            conn.close()

    def load_ancient_names(self, limit: int = None) -> List[str]:
        """
        加载古代人名语料库

        Args:
            limit: 限制加载数量

        Returns:
            古代人名列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT name FROM ancient_names"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            return [row['name'] for row in cursor.fetchall()]
        finally:
            conn.close()

    def load_chengyu(self, limit: int = None) -> List[str]:
        """
        加载成语词典

        Args:
            limit: 限制加载数量

        Returns:
            成语列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT idiom FROM idioms"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            return [row['idiom'] for row in cursor.fetchall()]
        finally:
            conn.close()

    def load_family_names(self, limit: int = None, origin: str = 'Chinese') -> List[Dict[str, any]]:
        """
        加载姓氏库

        Args:
            limit: 限制加载数量
            origin: 姓氏来源 ('Chinese', 'Japanese')

        Returns:
            姓氏字典列表 [{'name': '王', 'frequency': 9520, 'origin': 'Chinese'}, ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT name, frequency, origin FROM family_names WHERE origin = ?"
            params = [origin]

            if limit:
                query += f" ORDER BY frequency DESC LIMIT {limit}"
            else:
                query += " ORDER BY frequency DESC"

            cursor.execute(query, params)
            return [
                {'name': row['name'], 'frequency': row['frequency'], 'origin': row['origin']}
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def load_english_names(self, gender: str = None, limit: int = None) -> List[Dict[str, str]]:
        """
        加载英文人名

        Args:
            gender: 性别过滤 ('男性', '女性', None表示不过滤)
            limit: 限制加载数量

        Returns:
            英文人名字典列表 [{'chinese': '约翰', 'english': 'John', 'gender': '男性'}, ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT chinese_name, english_name, gender FROM english_names"
            params = []

            if gender:
                query += " WHERE gender = ?"
                params.append(gender)

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, params)
            return [
                {'chinese': row['chinese_name'], 'english': row['english_name'], 'gender': row['gender']}
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_random_names(self, count: int = 10, gender: str = None, style: str = 'modern') -> List[Dict[str, str]]:
        """
        随机获取人名

        Args:
            count: 数量
            gender: 性别过滤 ('男', '女', None表示不过滤)
            style: 风格 ('modern'现代, 'ancient'古代)

        Returns:
            人名字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if style == 'ancient':
                # 古代人名没有性别标注
                query = f"SELECT name FROM ancient_names ORDER BY RANDOM() LIMIT {count}"
                cursor.execute(query)
                return [{'name': row['name'], 'gender': '未知', 'style': 'ancient'} for row in cursor.fetchall()]
            else:
                # 现代人名
                query = "SELECT name, gender FROM chinese_names"
                params = []

                if gender:
                    query += " WHERE gender = ?"
                    params.append(gender)

                query += f" ORDER BY RANDOM() LIMIT {count}"

                cursor.execute(query, params)
                return [
                    {'name': row['name'], 'gender': row['gender'], 'style': 'modern'}
                    for row in cursor.fetchall()
                ]
        finally:
            conn.close()

    def search_names_by_char(self, char: str, gender: str = None, limit: int = 20) -> List[Dict[str, str]]:
        """
        根据字符搜索人名

        Args:
            char: 搜索的字符
            gender: 性别过滤 ('男', '女')
            limit: 返回数量限制

        Returns:
            匹配的人名列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT name, gender FROM chinese_names WHERE name LIKE ?"
            params = [f'%{char}%']

            if gender:
                query += " AND gender = ?"
                params.append(gender)

            query += f" LIMIT {limit}"

            cursor.execute(query, params)
            return [{'name': row['name'], 'gender': row['gender']} for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_chengyu_for_naming(self, count: int = 10, category: str = None) -> List[Dict[str, str]]:
        """
        获取适合取名的成语

        Args:
            count: 数量
            category: 类别过滤 ('男孩', '女孩', '通用', None表示不过滤)

        Returns:
            成语列表，包含成语和可提取的字
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT idiom, category FROM idioms"
            params = []

            if category:
                query += " WHERE category = ?"
                params.append(category)

            query += f" ORDER BY RANDOM() LIMIT {count}"

            cursor.execute(query, params)

            result = []
            for row in cursor.fetchall():
                chengyu = row['idiom']
                if len(chengyu) == 4:  # 标准四字成语
                    # 提取可用于取名的字（通常是后两个字）
                    name_chars = chengyu[2:4]
                    result.append({
                        'chengyu': chengyu,
                        'category': row['category'],
                        'suggested_chars': name_chars,
                        'full_chars': list(chengyu)
                    })

            return result
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, int]:
        """
        获取语料库统计信息

        Returns:
            统计字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            # 各表记录数
            tables = [
                ('chinese_names', '中文人名总数'),
                ('ancient_names', '古代人名总数'),
                ('family_names', '姓氏总数'),
                ('idioms', '成语总数'),
                ('japanese_names', '日文人名总数'),
                ('english_names', '英文人名总数'),
                ('relationships', '称呼关系总数')
            ]

            for table, label in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[label] = cursor.fetchone()[0]

            # 中文人名性别分布
            cursor.execute("SELECT gender, COUNT(*) FROM chinese_names GROUP BY gender")
            for row in cursor.fetchall():
                gender = row[0] or '未知'
                stats[f'中文人名-{gender}'] = row[1]

            # 英文人名性别分布
            cursor.execute("SELECT gender, COUNT(*) FROM english_names GROUP BY gender")
            for row in cursor.fetchall():
                gender = row[0] or '未知'
                stats[f'英文人名-{gender}'] = row[1]

            # 数据库文件大小
            db_size_mb = self.db_path.stat().st_size / (1024 * 1024)
            stats['数据库大小(MB)'] = round(db_size_mb, 2)

            return stats
        finally:
            conn.close()


# 全局单例
_corpus_loader = None


def get_corpus_loader(db_path: str = None) -> CorpusLoader:
    """获取全局语料库加载器实例"""
    global _corpus_loader
    if _corpus_loader is None:
        _corpus_loader = CorpusLoader(db_path)
    return _corpus_loader
