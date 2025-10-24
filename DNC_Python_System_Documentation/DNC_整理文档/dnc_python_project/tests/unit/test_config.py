"""
Config模块单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from dnc_python_project.src.core.config import ConfigManager
from dnc_python_project.src.utils.constants import DEFAULT_CONFIG


class TestConfigManager(unittest.TestCase):
    """ConfigManager类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.config_manager)
        self.assertEqual(self.config_manager.config_path, "config/")
        self.assertIsInstance(self.config_manager.config_cache, dict)
        
    def test_set_config_path(self):
        """测试设置配置路径"""
        new_path = "/new/config/path/"
        self.config_manager.set_config_path(new_path)
        self.assertEqual(self.config_manager.config_path, new_path)
        
    @patch('dnc_python_project.src.core.config.pd.read_csv')
    def test_load_csv_success(self, mock_read_csv):
        """测试成功加载CSV文件"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'DEFINE': ['TEST1', 'TEST2'],
            'VALUE': ['VALUE1', 'VALUE2']
        })
        mock_read_csv.return_value = test_data
        
        # 执行加载
        result = self.config_manager._load_csv('test.csv')
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result['TEST1'], 'VALUE1')
        self.assertEqual(result['TEST2'], 'VALUE2')
        mock_read_csv.assert_called_once_with('test.csv', encoding='utf-8')
        
    @patch('dnc_python_project.src.core.config.pd.read_csv')
    def test_load_csv_with_encoding_fallback(self, mock_read_csv):
        """测试CSV加载编码回退"""
        # 第一次调用失败，第二次成功
        mock_read_csv.side_effect = [
            UnicodeDecodeError('utf-8', b'', 0, 1, 'test'),
            pd.DataFrame({'DEFINE': ['TEST'], 'VALUE': ['VALUE']})
        ]
        
        # 执行加载
        result = self.config_manager._load_csv('test.csv')
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result['TEST'], 'VALUE')
        # 验证调用了两次，第二次使用gbk编码
        self.assertEqual(mock_read_csv.call_count, 2)
        mock_read_csv.assert_called_with('test.csv', encoding='gbk')
        
    @patch('dnc_python_project.src.core.config.pd.read_csv')
    def test_load_csv_file_not_found(self, mock_read_csv):
        """测试CSV文件不存在"""
        mock_read_csv.side_effect = FileNotFoundError("File not found")
        
        # 执行加载
        result = self.config_manager._load_csv('nonexistent.csv')
        
        # 验证结果
        self.assertIsNone(result)
        
    def test_get_value_existing(self):
        """测试获取存在的配置值"""
        # 设置测试数据
        self.config_manager.config_cache['test_config'] = {
            'KEY1': 'VALUE1',
            'KEY2': 'VALUE2'
        }
        
        # 获取值
        value = self.config_manager.get_value('KEY1', config_name='test_config')
        
        # 验证结果
        self.assertEqual(value, 'VALUE1')
        
    def test_get_value_with_default(self):
        """测试获取不存在的配置值（使用默认值）"""
        # 设置测试数据
        self.config_manager.config_cache['test_config'] = {
            'KEY1': 'VALUE1'
        }
        
        # 获取不存在的键
        value = self.config_manager.get_value('NONEXISTENT', default='DEFAULT', config_name='test_config')
        
        # 验证结果
        self.assertEqual(value, 'DEFAULT')
        
    def test_get_value_no_config(self):
        """测试获取不存在的配置"""
        value = self.config_manager.get_value('KEY', config_name='nonexistent_config')
        
        # 验证结果
        self.assertIsNone(value)
        
    def test_set_value(self):
        """测试设置配置值"""
        # 设置配置
        self.config_manager.set_value('NEW_KEY', 'NEW_VALUE', config_name='test_config')
        
        # 验证设置
        self.assertEqual(self.config_manager.config_cache['test_config']['NEW_KEY'], 'NEW_VALUE')
        
    def test_clear_cache(self):
        """测试清空缓存"""
        # 设置测试数据
        self.config_manager.config_cache['test_config'] = {'KEY': 'VALUE'}
        
        # 清空缓存
        self.config_manager.clear_cache()
        
        # 验证缓存已清空
        self.assertEqual(self.config_manager.config_cache, {})
        
    @patch('dnc_python_project.src.core.config.ConfigManager._load_csv')
    def test_load_all_configs_success(self, mock_load_csv):
        """测试成功加载所有配置"""
        # 设置mock返回值
        mock_load_csv.side_effect = [
            {'DEFINE': 'TEST1', 'VALUE': 'VALUE1'},  # ini.csv
            {'HEADER': 'TEST2', 'VALUE': 'VALUE2'},  # header.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # type_define.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # type_prg.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # prg.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # load.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # cntrl.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # define.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # chngValue.csv
            {'NO': '1', 'TYPE': 'TYPE1'},            # calc.csv
            {'NO': '1', 'TYPE': 'TYPE1'}             # relation.csv
        ]
        
        # 执行加载
        result = self.config_manager.load_all_configs()
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(mock_load_csv.call_count, 11)
        
    @patch('dnc_python_project.src.core.config.ConfigManager._load_csv')
    def test_load_all_configs_partial_failure(self, mock_load_csv):
        """测试部分配置加载失败"""
        # 设置mock返回值，部分成功部分失败
        mock_load_csv.side_effect = [
            {'DEFINE': 'TEST1', 'VALUE': 'VALUE1'},  # ini.csv - 成功
            None,                                     # header.csv - 失败
            {'NO': '1', 'TYPE': 'TYPE1'},            # type_define.csv - 成功
            None,                                     # type_prg.csv - 失败
            {'NO': '1', 'TYPE': 'TYPE1'},            # prg.csv - 成功
            None,                                     # load.csv - 失败
            {'NO': '1', 'TYPE': 'TYPE1'},            # cntrl.csv - 成功
            None,                                     # define.csv - 失败
            {'NO': '1', 'TYPE': 'TYPE1'},            # chngValue.csv - 成功
            None,                                     # calc.csv - 失败
            {'NO': '1', 'TYPE': 'TYPE1'}             # relation.csv - 成功
        ]
        
        # 执行加载
        result = self.config_manager.load_all_configs()
        
        # 验证结果
        self.assertTrue(result)  # 部分失败仍然返回True
        self.assertEqual(mock_load_csv.call_count, 11)
        
    @patch('dnc_python_project.src.core.config.ConfigManager._load_csv')
    def test_load_all_configs_complete_failure(self, mock_load_csv):
        """测试所有配置加载失败"""
        # 设置所有加载都失败
        mock_load_csv.return_value = None
        
        # 执行加载
        result = self.config_manager.load_all_configs()
        
        # 验证结果
        self.assertFalse(result)
        
    def test_get_config_names(self):
        """测试获取配置名称列表"""
        # 设置测试数据
        self.config_manager.config_cache = {
            'ini': {'KEY': 'VALUE'},
            'header': {'KEY': 'VALUE'},
            'type_define': {'KEY': 'VALUE'}
        }
        
        # 获取配置名称
        names = self.config_manager.get_config_names()
        
        # 验证结果
        expected_names = ['ini', 'header', 'type_define']
        self.assertEqual(sorted(names), sorted(expected_names))
        
    def test_get_config_stats(self):
        """测试获取配置统计信息"""
        # 设置测试数据
        self.config_manager.config_cache = {
            'ini': {'KEY1': 'VALUE1', 'KEY2': 'VALUE2'},
            'header': {'KEY3': 'VALUE3'}
        }
        
        # 获取统计信息
        stats = self.config_manager.get_config_stats()
        
        # 验证结果
        expected_stats = {
            'total_configs': 2,
            'total_entries': 3,
            'config_details': {
                'ini': {'entries': 2},
                'header': {'entries': 1}
            }
        }
        self.assertEqual(stats, expected_stats)
        
    def test_validate_config_integrity(self):
        """测试配置完整性验证"""
        # 设置测试数据
        self.config_manager.config_cache = {
            'ini': {'KEY1': 'VALUE1'},
            'type_define': {'NO': '1', 'TYPE': 'TYPE1'},
            'type_prg': {'NO': '1', 'TYPE': 'TYPE1'},
            'prg': {'NO': '1', 'TYPE': 'TYPE1'},
            'load': {'NO': '1', 'TYPE': 'TYPE1'}
        }
        
        # 验证完整性
        result = self.config_manager.validate_config_integrity()
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['warnings']), 0)
        
    def test_validate_config_integrity_with_warnings(self):
        """测试配置完整性验证（有警告）"""
        # 设置不完整的数据
        self.config_manager.config_cache = {
            'ini': {'KEY1': 'VALUE1'},
            'type_define': {'NO': '1', 'TYPE': 'TYPE1'}
            # 缺少其他必要配置
        }
        
        # 验证完整性
        result = self.config_manager.validate_config_integrity()
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['warnings']), 0)
        
    def test_reload_config(self):
        """测试重新加载配置"""
        # 设置初始数据
        self.config_manager.config_cache['test_config'] = {'OLD_KEY': 'OLD_VALUE'}
        
        # 重新加载配置
        with patch.object(self.config_manager, '_load_csv') as mock_load:
            mock_load.return_value = {'NEW_KEY': 'NEW_VALUE'}
            result = self.config_manager.reload_config('test_config')
            
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(self.config_manager.config_cache['test_config']['NEW_KEY'], 'NEW_VALUE')
        
    def test_reload_nonexistent_config(self):
        """测试重新加载不存在的配置"""
        result = self.config_manager.reload_config('nonexistent_config')
        
        # 验证结果
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
