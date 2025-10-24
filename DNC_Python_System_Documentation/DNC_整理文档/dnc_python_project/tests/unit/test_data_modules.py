"""
数据模块单元测试
包含CSVProcessor、DataValidator、FileManager的测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import csv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.data.csv_processor import CSVProcessor
from dnc_python_project.src.data.data_validator import DataValidator
from dnc_python_project.src.data.file_manager import FileManager


class TestCSVProcessor(unittest.TestCase):
    """CSVProcessor类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = CSVProcessor()
        self.test_data = [
            ['Name', 'Age', 'City'],
            ['Alice', '25', 'Beijing'],
            ['Bob', '30', 'Shanghai'],
            ['Charlie', '35', 'Guangzhou']
        ]
        
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()
        
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.processor, CSVProcessor)
        
    def test_read_csv_success(self):
        """测试成功读取CSV文件"""
        # 写入测试数据
        with open(self.temp_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.test_data)
        
        # 读取CSV文件
        result = self.processor.read_csv(self.temp_file_path)
        
        # 验证结果
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], ['Name', 'Age', 'City'])
        self.assertEqual(result[1], ['Alice', '25', 'Beijing'])
        
    def test_read_csv_file_not_found(self):
        """测试读取不存在的CSV文件"""
        result = self.processor.read_csv('nonexistent.csv')
        self.assertIsNone(result)
        
    def test_write_csv_success(self):
        """测试成功写入CSV文件"""
        # 写入CSV文件
        result = self.processor.write_csv(self.temp_file_path, self.test_data)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证文件内容
        with open(self.temp_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            written_data = list(reader)
            
        self.assertEqual(written_data, self.test_data)
        
    def test_read_csv_as_dict_success(self):
        """测试成功读取CSV为字典列表"""
        # 写入测试数据
        with open(self.temp_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.test_data)
        
        # 读取CSV文件为字典
        result = self.processor.read_csv_as_dict(self.temp_file_path)
        
        # 验证结果
        self.assertEqual(len(result), 3)  # 3行数据（排除标题行）
        self.assertEqual(result[0]['Name'], 'Alice')
        self.assertEqual(result[0]['Age'], '25')
        self.assertEqual(result[0]['City'], 'Beijing')
        
    def test_write_dict_to_csv_success(self):
        """测试成功写入字典到CSV"""
        dict_data = [
            {'Name': 'Alice', 'Age': '25', 'City': 'Beijing'},
            {'Name': 'Bob', 'Age': '30', 'City': 'Shanghai'}
        ]
        
        # 写入字典到CSV
        result = self.processor.write_dict_to_csv(self.temp_file_path, dict_data)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证文件内容
        with open(self.temp_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            written_data = list(reader)
            
        self.assertEqual(len(written_data), 2)
        self.assertEqual(written_data[0]['Name'], 'Alice')
        
    def test_get_csv_info_success(self):
        """测试获取CSV文件信息"""
        # 写入测试数据
        with open(self.temp_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.test_data)
        
        # 获取CSV信息
        result = self.processor.get_csv_info(self.temp_file_path)
        
        # 验证结果
        self.assertEqual(result['row_count'], 4)
        self.assertEqual(result['column_count'], 3)
        self.assertEqual(result['headers'], ['Name', 'Age', 'City'])
        self.assertGreater(result['file_size'], 0)
        
    def test_get_csv_info_file_not_found(self):
        """测试获取不存在的CSV文件信息"""
        result = self.processor.get_csv_info('nonexistent.csv')
        self.assertIsNone(result)


class TestDataValidator(unittest.TestCase):
    """DataValidator类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = DataValidator()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.validator, DataValidator)
        
    def test_validate_value_numeric_range_success(self):
        """测试数值范围验证成功"""
        result = self.validator.validate_value(15, 'numeric_range', min_value=10, max_value=20)
        self.assertTrue(result['valid'])
        self.assertEqual(result['value'], 15)
        
    def test_validate_value_numeric_range_failure(self):
        """测试数值范围验证失败"""
        result = self.validator.validate_value(25, 'numeric_range', min_value=10, max_value=20)
        self.assertFalse(result['valid'])
        self.assertIn('超出范围', result['message'])
        
    def test_validate_string_length_success(self):
        """测试字符串长度验证成功"""
        result = self.validator.validate_value('hello', 'string_length', min_length=3, max_length=10)
        self.assertTrue(result['valid'])
        
    def test_validate_string_length_failure(self):
        """测试字符串长度验证失败"""
        result = self.validator.validate_value('hi', 'string_length', min_length=3, max_length=10)
        self.assertFalse(result['valid'])
        
    def test_validate_enum_success(self):
        """测试枚举验证成功"""
        result = self.validator.validate_value('red', 'enum', allowed_values=['red', 'green', 'blue'])
        self.assertTrue(result['valid'])
        
    def test_validate_enum_failure(self):
        """测试枚举验证失败"""
        result = self.validator.validate_value('yellow', 'enum', allowed_values=['red', 'green', 'blue'])
        self.assertFalse(result['valid'])
        
    def test_validate_date_format_success(self):
        """测试日期格式验证成功"""
        result = self.validator.validate_value('2023-12-25', 'date_format', date_format='%Y-%m-%d')
        self.assertTrue(result['valid'])
        
    def test_validate_date_format_failure(self):
        """测试日期格式验证失败"""
        result = self.validator.validate_value('25/12/2023', 'date_format', date_format='%Y-%m-%d')
        self.assertFalse(result['valid'])
        
    def test_validate_data_structure_success(self):
        """测试数据结构验证成功"""
        data = {
            'name': 'Alice',
            'age': 25,
            'email': 'alice@example.com'
        }
        schema = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'int', 'required': True},
            'email': {'type': 'string', 'required': False}
        }
        
        result = self.validator.validate_data_structure(data, schema)
        self.assertTrue(result['valid'])
        
    def test_validate_data_structure_failure(self):
        """测试数据结构验证失败"""
        data = {
            'name': 'Alice'
        }
        schema = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'int', 'required': True}
        }
        
        result = self.validator.validate_data_structure(data, schema)
        self.assertFalse(result['valid'])
        self.assertIn('缺少必填字段', result['message'])
        
    def test_add_custom_rule_success(self):
        """测试添加自定义规则成功"""
        result = self.validator.add_custom_rule('phone_number', r'^\d{11}$')
        self.assertTrue(result)
        
    def test_get_available_rules(self):
        """测试获取可用规则"""
        rules = self.validator.get_available_rules()
        self.assertIn('numeric_range', rules)
        self.assertIn('string_length', rules)
        self.assertIn('enum', rules)


class TestFileManager(unittest.TestCase):
    """FileManager类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = FileManager()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, 'test.txt')
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.manager, FileManager)
        
    def test_set_base_path_success(self):
        """测试设置基础路径成功"""
        result = self.manager.set_base_path(self.temp_dir)
        self.assertTrue(result)
        
    def test_set_base_path_invalid(self):
        """测试设置无效的基础路径"""
        result = self.manager.set_base_path('/invalid/path/that/does/not/exist')
        self.assertFalse(result)
        
    def test_ensure_directory_success(self):
        """测试确保目录存在成功"""
        test_dir = os.path.join(self.temp_dir, 'subdir')
        result = self.manager.ensure_directory(test_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dir))
        
    def test_file_exists_true(self):
        """测试文件存在"""
        with open(self.test_file_path, 'w') as f:
            f.write('test content')
            
        result = self.manager.file_exists(self.test_file_path)
        self.assertTrue(result)
        
    def test_file_exists_false(self):
        """测试文件不存在"""
        result = self.manager.file_exists(os.path.join(self.temp_dir, 'nonexistent.txt'))
        self.assertFalse(result)
        
    def test_read_file_success(self):
        """测试成功读取文件"""
        test_content = 'Hello, World!'
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
            
        result = self.manager.read_file(self.test_file_path)
        self.assertEqual(result, test_content)
        
    def test_read_file_not_found(self):
        """测试读取不存在的文件"""
        result = self.manager.read_file(os.path.join(self.temp_dir, 'nonexistent.txt'))
        self.assertIsNone(result)
        
    def test_write_file_success(self):
        """测试成功写入文件"""
        test_content = 'Test content for writing'
        result = self.manager.write_file(self.test_file_path, test_content)
        
        self.assertTrue(result)
        
        # 验证文件内容
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertEqual(content, test_content)
        
    def test_copy_file_success(self):
        """测试成功复制文件"""
        source_content = 'Source file content'
        source_path = os.path.join(self.temp_dir, 'source.txt')
        dest_path = os.path.join(self.temp_dir, 'dest.txt')
        
        with open(source_path, 'w') as f:
            f.write(source_content)
            
        result = self.manager.copy_file(source_path, dest_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(dest_path))
        
        with open(dest_path, 'r') as f:
            dest_content = f.read()
            
        self.assertEqual(dest_content, source_content)
        
    def test_delete_file_success(self):
        """测试成功删除文件"""
        with open(self.test_file_path, 'w') as f:
            f.write('test content')
            
        result = self.manager.delete_file(self.test_file_path)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.test_file_path))
        
    def test_list_files_success(self):
        """测试成功列出文件"""
        # 创建测试文件
        test_files = ['file1.txt', 'file2.csv', 'file3.py']
        for filename in test_files:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write('content')
                
        result = self.manager.list_files(self.temp_dir, '*.txt')
        self.assertEqual(len(result), 1)
        self.assertIn('file1.txt', result[0])
        
    def test_get_file_size_success(self):
        """测试成功获取文件大小"""
        test_content = 'Test content'
        with open(self.test_file_path, 'w') as f:
            f.write(test_content)
            
        result = self.manager.get_file_size(self.test_file_path)
        self.assertEqual(result, len(test_content))
        
    def test_get_file_info_success(self):
        """测试成功获取文件信息"""
        test_content = 'Test content'
        with open(self.test_file_path, 'w') as f:
            f.write(test_content)
            
        result = self.manager.get_file_info(self.test_file_path)
        self.assertIsNotNone(result)
        self.assertEqual(result['size'], len(test_content))
        self.assertTrue(result['exists'])
        
    def test_create_backup_success(self):
        """测试成功创建备份"""
        test_content = 'Original content'
        with open(self.test_file_path, 'w') as f:
            f.write(test_content)
            
        result = self.manager.create_backup(self.test_file_path)
        self.assertTrue(result)
        
        backup_path = self.test_file_path + '.bak'
        self.assertTrue(os.path.exists(backup_path))
        
        with open(backup_path, 'r') as f:
            backup_content = f.read()
            
        self.assertEqual(backup_content, test_content)


if __name__ == '__main__':
    unittest.main()
