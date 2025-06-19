"""批量导入书籍的脚本"""
# -*- coding: utf-8 -*-
import os
import csv
import json
import warnings
from datetime import datetime
from typing import List, Dict, Optional, Union

import pymysql
from service.Utils import queryConfig


class BookImporter:
    """书籍批量导入工具类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_info = queryConfig("Database")
        self.conn = None
        self.cursor = None
        
        # 图书分类法支持的类型
        self.supported_types = [
            "马列主义、毛泽东思想、邓小平理论", "哲学、宗教", "社会科学总论", "政治、法律", "军事", "经济",
            "文化、科学、教育、体育", "语言、文字", "文学", "艺术", "历史、地理", "自然科学总论",
            "数理科学和化学", "天文学、地球科学", "生物科学", "医药、卫生", "农业科学", "工业技术",
            "交通运输", "航空、航天", "环境科学、安全科学", "综合性图书"
        ]
    
    def connect_database(self) -> bool:
        """连接数据库"""
        try:
            self.conn = pymysql.connect(
                host=self.db_info["Host"],
                port=self.db_info["Port"],
                user=self.db_info["Account"],
                password=self.db_info["Password"],
                database=self.db_info["Database"],
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
            print("数据库连接成功")
            return True
        except pymysql.err.OperationalError as e:
            warnings.warn(f"数据库连接失败：{e}")
            return False
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("数据库连接已关闭")
    
    def validate_book_data(self, book_data: Dict) -> bool:
        """验证书籍数据的有效性"""
        # 必填字段检查
        required_fields = ['isbn', 'title', 'author']
        for field in required_fields:
            if not book_data.get(field):
                print(f"错误：书籍数据缺少必填字段 '{field}': {book_data}")
                return False
        
        # 类型检查
        if book_data.get('type') and book_data['type'] not in self.supported_types:
            print(f"警告：不支持的书籍类型 '{book_data['type']}'，将设置为空")
            book_data['type'] = None
        
        # 页数检查
        if book_data.get('page'):
            try:
                book_data['page'] = int(book_data['page'])
            except (ValueError, TypeError):
                print(f"警告：页数格式错误，将设置为空: {book_data.get('page')}")
                book_data['page'] = None
        
        # 评分检查
        for score_field in ['douban_score', 'bangumi_score']:
            if book_data.get(score_field):
                try:
                    book_data[score_field] = float(book_data[score_field])
                    if not (0 <= book_data[score_field] <= 10):
                        print(f"警告：{score_field} 超出有效范围(0-10)，将设置为空")
                        book_data[score_field] = None
                except (ValueError, TypeError):
                    print(f"警告：{score_field} 格式错误，将设置为空: {book_data.get(score_field)}")
                    book_data[score_field] = None
        
        # 日期格式检查
        if book_data.get('publish_date'):
            try:
                if isinstance(book_data['publish_date'], str):
                    datetime.strptime(book_data['publish_date'], '%Y-%m-%d')
            except ValueError:
                print(f"警告：出版日期格式错误，将设置为空: {book_data.get('publish_date')}")
                book_data['publish_date'] = None
        
        return True
    
    def check_book_exists(self, isbn: str, title: str, author: str) -> bool:
        """检查书籍是否已存在"""
        try:
            # 检查ISBN是否存在
            self.cursor.execute("SELECT id FROM book WHERE isbn = %s", (isbn,))
            if self.cursor.fetchone():
                return True
            
            # 检查标题和作者组合是否存在
            self.cursor.execute("SELECT id FROM book WHERE title = %s AND author = %s", (title, author))
            if self.cursor.fetchone():
                return True
            
            return False
        except Exception as e:
            print(f"检查书籍是否存在时发生错误：{e}")
            return True  # 出错时假设存在，避免重复插入
    
    def insert_book(self, book_data: Dict) -> bool:
        """插入单本书籍"""
        try:
            if self.check_book_exists(book_data['isbn'], book_data['title'], book_data['author']):
                print(f"书籍已存在，跳过：{book_data['title']} - {book_data['author']}")
                return False
            
            sql = """
            INSERT INTO book (isbn, title, origin_title, subtitle, author, page, publish_date, 
                            publisher, description, douban_score, douban_id, bangumi_score, 
                            bangumi_id, type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                book_data.get('isbn'),
                book_data.get('title'),
                book_data.get('origin_title'),
                book_data.get('subtitle'),
                book_data.get('author'),
                book_data.get('page'),
                book_data.get('publish_date'),
                book_data.get('publisher'),
                book_data.get('description'),
                book_data.get('douban_score'),
                book_data.get('douban_id'),
                book_data.get('bangumi_score'),
                book_data.get('bangumi_id'),
                book_data.get('type')
            )
            
            self.cursor.execute(sql, values)
            self.conn.commit()
            print(f"成功导入：{book_data['title']} - {book_data['author']}")
            return True
            
        except Exception as e:
            print(f"插入书籍失败：{e}")
            print(f"书籍数据：{book_data}")
            self.conn.rollback()
            return False
    
    def import_from_csv(self, csv_file_path: str) -> Dict[str, int]:
        """从CSV文件导入书籍"""
        print(f">>---------------------------------------从CSV导入书籍---------------------------------------<<")
        print(f"开始从 {csv_file_path} 导入书籍数据")
        
        if not os.path.exists(csv_file_path):
            print(f"错误：CSV文件不存在 - {csv_file_path}")
            return {"success": 0, "failed": 0, "skipped": 0}
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # 尝试自动检测CSV方言，如果失败则使用默认分隔符
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','  # 默认使用逗号分隔符
                try:
                    sniffer = csv.Sniffer()
                    detected_delimiter = sniffer.sniff(sample).delimiter
                    # 验证检测到的分隔符是否合理
                    if detected_delimiter in [',', ';', '\t', '|']:
                        delimiter = detected_delimiter
                        print(f"检测到分隔符: '{delimiter}'")
                    else:
                        print(f"使用默认分隔符: ','")
                except Exception as e:
                    print(f"无法自动检测分隔符，使用默认分隔符 ','：{e}")
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是标题）
                    try:
                        # 清理数据，移除空字符串和None值
                        book_data = {}
                        for k, v in row.items():
                            if k and v:  # 确保键和值都存在
                                cleaned_value = str(v).strip()
                                if cleaned_value:  # 只保留非空值
                                    book_data[k] = cleaned_value
                        
                        if not book_data:  # 跳过完全为空的行
                            continue
                            
                        if not self.validate_book_data(book_data):
                            failed_count += 1 
                            continue
                        
                        if self.insert_book(book_data):
                            success_count += 1
                        else:
                            skipped_count += 1
                            
                    except Exception as e:
                        print(f"处理第{row_num}行数据时发生错误：{e}")
                        failed_count += 1
                        continue
                        
        except Exception as e:
            print(f"读取CSV文件时发生错误：{e}")
            failed_count += 1
        
        print(f"CSV导入完成：成功 {success_count} 本，跳过 {skipped_count} 本，失败 {failed_count} 本")
        return {"success": success_count, "failed": failed_count, "skipped": skipped_count}
    
    def import_from_json(self, json_file_path: str) -> Dict[str, int]:
        """从JSON文件导入书籍"""
        print(f">>---------------------------------------从JSON导入书籍---------------------------------------<<")
        print(f"开始从 {json_file_path} 导入书籍数据")
        
        if not os.path.exists(json_file_path):
            print(f"错误：JSON文件不存在 - {json_file_path}")
            return {"success": 0, "failed": 0, "skipped": 0}
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # 支持两种JSON格式：书籍列表或包含books字段的对象
                if isinstance(data, list):
                    books = data
                elif isinstance(data, dict) and 'books' in data:
                    books = data['books']
                else:
                    print("错误：JSON格式不正确，应该是书籍列表或包含'books'字段的对象")
                    return {"success": 0, "failed": 0, "skipped": 1}
                
                for book_data in books:
                    if not self.validate_book_data(book_data):
                        failed_count += 1
                        continue
                    
                    if self.insert_book(book_data):
                        success_count += 1
                    else:
                        skipped_count += 1
                        
        except json.JSONDecodeError as e:
            print(f"JSON文件格式错误：{e}")
            failed_count += 1
        except Exception as e:
            print(f"读取JSON文件时发生错误：{e}")
            failed_count += 1
        
        print(f"JSON导入完成：成功 {success_count} 本，跳过 {skipped_count} 本，失败 {failed_count} 本")
        return {"success": success_count, "failed": failed_count, "skipped": skipped_count}
    
    def import_sample_books(self) -> Dict[str, int]:
        """导入示例书籍数据"""
        print(f">>---------------------------------------导入示例书籍---------------------------------------<<")
        
        sample_books = [
            {
                "isbn": "9787020002207",
                "title": "红楼梦",
                "author": "曹雪芹",
                "page": 1024,
                "publish_date": "1996-12-01",
                "publisher": "人民文学出版社",
                "description": "中国古典四大名著之一，描写了贾、史、王、薛四大家族的兴衰史。",
                "douban_score": 9.6,
                "douban_id": "1007305",
                "type": "文学"
            },
            {
                "isbn": "9787020008735",
                "title": "三国演义",
                "author": "罗贯中",
                "page": 800,
                "publish_date": "1998-05-01",
                "publisher": "人民文学出版社",
                "description": "以三国时期历史为背景的长篇历史小说。",
                "douban_score": 9.3,
                "douban_id": "1019568",
                "type": "文学"
            },
            {
                "isbn": "9787020056453",
                "title": "西游记",
                "author": "吴承恩",
                "page": 640,
                "publish_date": "2000-06-01",
                "publisher": "人民文学出版社",
                "description": "中国古典神话小说，讲述唐僧师徒四人取经的故事。",
                "douban_score": 9.2,
                "douban_id": "1029553",
                "type": "文学"
            },
            {
                "isbn": "9787020015009",
                "title": "水浒传",
                "author": "施耐庵",
                "page": 896,
                "publish_date": "1997-01-01",
                "publisher": "人民文学出版社",
                "description": "描写108位梁山好汉的英雄传奇故事。",
                "douban_score": 9.1,
                "douban_id": "1052357",
                "type": "文学"
            },
            {
                "isbn": "9787508693019",
                "title": "活着",
                "author": "余华",
                "page": 191,
                "publish_date": "2012-08-01",
                "publisher": "中信出版社",
                "description": "讲述了一个人和他命运之间的友情，这是最为感人的友情。",
                "douban_score": 9.4,
                "douban_id": "4913064",
                "type": "文学"
            }
        ]
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for book_data in sample_books:
            if not self.validate_book_data(book_data):
                failed_count += 1
                continue
            
            if self.insert_book(book_data):
                success_count += 1
            else:
                skipped_count += 1
        
        print(f"示例书籍导入完成：成功 {success_count} 本，跳过 {skipped_count} 本，失败 {failed_count} 本")
        return {"success": success_count, "failed": failed_count, "skipped": skipped_count}
    
    def delete_all_books(self) -> Dict[str, int]:
        """删除所有书籍 - 危险操作！"""
        print(f">>---------------------------------------删除所有书籍---------------------------------------<<")
        print("⚠️  警告：此操作将删除数据库中的所有书籍数据！")
        print("⚠️  此操作不可逆，请确保你已经备份了重要数据！")
        
        try:
            # 首先查询当前书籍总数
            self.cursor.execute("SELECT COUNT(*) FROM book")
            total_books = self.cursor.fetchone()[0]
            
            if total_books == 0:
                print("数据库中没有书籍数据，无需删除。")
                return {"deleted": 0, "failed": 0}
            
            print(f"数据库中当前有 {total_books} 本书籍")
            
            # 三重确认机制
            confirm1 = input(f"\n第一次确认：确定要删除所有 {total_books} 本书籍吗？(yes/no): ").strip().lower()
            if confirm1 not in ['yes', 'y']:
                print("操作已取消。")
                return {"deleted": 0, "failed": 0}
            
            confirm2 = input(f"\n第二次确认：删除后将无法恢复，请再次确认删除所有书籍？(DELETE/cancel): ").strip()
            if confirm2 != 'DELETE':
                print("操作已取消。")
                return {"deleted": 0, "failed": 0}
            
            # 让用户输入一个随机验证码
            import random
            verification_code = str(random.randint(1000, 9999))
            user_input = input(f"\n最终确认：请输入验证码 {verification_code} 以确认删除操作: ").strip()
            if user_input != verification_code:
                print("验证码错误，操作已取消。")
                return {"deleted": 0, "failed": 0}
            
            print("\n开始删除所有书籍...")
            
            # 执行删除操作
            # 由于可能存在外键约束，我们需要按顺序删除
            
            # 1. 先删除与书籍相关的journal数据（如果存在）
            try:
                self.cursor.execute("DELETE FROM journal WHERE book_id IS NOT NULL")
                journal_deleted = self.cursor.rowcount
                if journal_deleted > 0:
                    print(f"删除了 {journal_deleted} 条相关的书评数据")
            except Exception as e:
                print(f"删除书评数据时出现警告：{e}")
            
            # 2. 删除所有书籍
            self.cursor.execute("DELETE FROM book")
            books_deleted = self.cursor.rowcount
            
            # 3. 重置自增ID（可选）
            try:
                self.cursor.execute("ALTER TABLE book AUTO_INCREMENT = 1")
                print("重置了书籍表的自增ID")
            except Exception as e:
                print(f"重置自增ID时出现警告：{e}")
            
            # 提交事务
            self.conn.commit()
            
            print(f"✅ 成功删除了 {books_deleted} 本书籍")
            print("数据库已清空，可以重新导入新的书籍数据。")
            
            return {"deleted": books_deleted, "failed": 0}
            
        except Exception as e:
            # 回滚事务
            self.conn.rollback()
            print(f"❌ 删除操作失败：{e}")
            print("数据库状态已回滚，没有数据丢失。")
            return {"deleted": 0, "failed": 1}
    
    def get_book_statistics(self) -> Dict[str, int]:
        """获取书籍统计信息"""
        try:
            # 总书籍数
            self.cursor.execute("SELECT COUNT(*) FROM book")
            total_books = self.cursor.fetchone()[0]
            
            # 按类型统计
            self.cursor.execute("""
                SELECT type, COUNT(*) 
                FROM book 
                WHERE type IS NOT NULL AND type != '' 
                GROUP BY type 
                ORDER BY COUNT(*) DESC
            """)
            type_stats = self.cursor.fetchall()
            
            print(f"\n📊 当前数据库书籍统计：")
            print(f"总书籍数：{total_books} 本")
            
            if type_stats:
                print(f"\n按类型分布：")
                for book_type, count in type_stats:
                    print(f"  {book_type}: {count} 本")
            
            return {"total": total_books, "by_type": dict(type_stats)}
            
        except Exception as e:
            print(f"获取统计信息失败：{e}")
            return {"total": 0, "by_type": {}}


def print_help():
    """打印使用帮助"""
    print("="*60)
    print("              书籍批量导入工具使用说明")
    print("="*60)
    print("支持的功能：")
    print("1. CSV文件导入 - 从CSV文件批量导入书籍")
    print("2. JSON文件导入 - 从JSON文件批量导入书籍")
    print("3. 导入示例数据 - 导入内置的示例书籍")
    print("4. 查看书籍统计 - 显示当前数据库中的书籍统计信息")
    print("5. 删除所有书籍 - ⚠️ 危险操作！清空所有书籍数据")
    print("")
    print("CSV文件格式要求：")
    print("- 第一行为字段名（标题行）")
    print("- 必填字段：isbn, title, author")
    print("- 可选字段：origin_title, subtitle, page, publish_date, publisher,")
    print("           description, douban_score, douban_id, bangumi_score,")
    print("           bangumi_id, type")
    print("- 日期格式：YYYY-MM-DD")
    print("- 评分范围：0-10")
    print("")
    print("JSON文件格式要求：")
    print("- 支持书籍对象数组：[{book1}, {book2}, ...]")
    print("- 或包含books字段：{\"books\": [{book1}, {book2}, ...]}")
    print("- 字段要求同CSV")
    print("")
    print("⚠️ 安全提示：")
    print("- 删除操作不可逆，请在操作前备份数据库")
    print("- 建议先查看统计信息了解当前数据状况")
    print("="*60)


def main():
    """主函数"""
    print_help()
    
    importer = BookImporter()
    
    if not importer.connect_database():
        return
    
    try:
        while True:
            print("\n请选择功能：")
            print("1. 从CSV文件导入")
            print("2. 从JSON文件导入")  
            print("3. 导入示例书籍数据")
            print("4. 查看书籍统计")
            print("5. 删除所有书籍 ⚠️")
            print("6. 显示帮助信息")
            print("0. 退出")
            
            choice = input("请输入选项 (0-6): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                file_path = input("请输入CSV文件路径: ").strip()
                if file_path:
                    importer.import_from_csv(file_path)
            elif choice == "2":
                file_path = input("请输入JSON文件路径: ").strip()
                if file_path:
                    importer.import_from_json(file_path)
            elif choice == "3":
                confirm = input("确认导入示例书籍数据吗？(y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    importer.import_sample_books()
            elif choice == "4":
                importer.get_book_statistics()
            elif choice == "5":
                print("\n⚠️ ⚠️ ⚠️  危险操作警告  ⚠️ ⚠️ ⚠️")
                print("你即将删除数据库中的所有书籍！")
                print("建议先选择选项4查看当前书籍统计")
                confirm = input("\n确定要继续吗？(continue/cancel): ").strip().lower()
                if confirm == 'continue':
                    importer.delete_all_books()
                else:
                    print("操作已取消。")
            elif choice == "6":
                print_help()
            else:
                print("无效选项，请重新选择")
    
    finally:
        importer.close_connection()


if __name__ == "__main__":
    main()