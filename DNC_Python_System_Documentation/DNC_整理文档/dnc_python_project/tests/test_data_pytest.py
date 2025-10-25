"""
数据模块测试
测试数据相关的功能
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.data.file_manager import FileManager
from src.data.csv_processor import CSVProcessor
from src.data.data_validator import DataValidator


class TestFileManager:
    """文件管理器测试类"""

    def test_get_file_info(self, tmp_path):
        """测试获取文件信息"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        info = manager.get_file_info(str(test_file))
        
        assert info is not None
        assert info["exists"] is True
        assert info["size"] > 0
        assert info["extension"] == ".txt"
        assert "created_time" in info
        assert "modified_time" in info

    def test_get_file_info_nonexistent(self):
        """测试获取不存在的文件信息"""
        manager = FileManager()
        info = manager.get_file_info("nonexistent.txt")
        
        assert info is not None
        assert info["exists"] is False
        assert info["size"] == 0

    def test_list_files(self, tmp_path):
        """测试列出文件"""
        manager = FileManager()
        
        # 创建测试文件
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").write_text("content3")
        
        # 测试非递归列表
        files = manager.list_files(str(tmp_path), recursive=False)
        assert len(files) == 3  # file1.txt, file2.txt, subdir
        assert any("file1.txt" in f["name"] for f in files)
        assert any("file2.txt" in f["name"] for f in files)
        assert any("subdir" in f["name"] for f in files)

    def test_list_files_recursive(self, tmp_path):
        """测试递归列出文件"""
        manager = FileManager()
        
        # 创建测试文件
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.txt").write_text("content2")
        
        # 测试递归列表
        files = manager.list_files(str(tmp_path), recursive=True)
        assert len(files) >= 2
        assert any("file1.txt" in f["name"] for f in files)
        assert any("file2.txt" in f["name"] for f in files)

    def test_list_files_nonexistent_directory(self):
        """测试列出不存在的目录"""
        manager = FileManager()
        files = manager.list_files("nonexistent_dir")
        assert files is None

    def test_search_files(self, tmp_path):
        """测试搜索文件"""
        manager = FileManager()
        
        # 创建测试文件
        (tmp_path / "test_file.txt").write_text("test content")
        (tmp_path / "another_file.txt").write_text("another content")
        (tmp_path / "image.png").write_text("image data")
        
        # 搜索txt文件
        results = manager.search_files(str(tmp_path), "*.txt")
        assert len(results) == 2
        assert any("test_file.txt" in f["name"] for f in results)
        assert any("another_file.txt" in f["name"] for f in results)

    def test_search_files_no_matches(self, tmp_path):
        """测试搜索无匹配文件"""
        manager = FileManager()
        (tmp_path / "test.txt").write_text("content")
        
        results = manager.search_files(str(tmp_path), "*.jpg")
        assert len(results) == 0

    def test_get_directory_size(self, tmp_path):
        """测试获取目录大小"""
        manager = FileManager()
        
        # 创建测试文件
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2" * 100)  # 更大的文件
        
        size = manager.get_directory_size(str(tmp_path))
        assert size > 0

    def test_get_directory_size_nonexistent(self):
        """测试获取不存在的目录大小"""
        manager = FileManager()
        size = manager.get_directory_size("nonexistent_dir")
        assert size == 0

    def test_check_file_permissions(self, tmp_path):
        """测试检查文件权限"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        permissions = manager.check_file_permissions(str(test_file))
        assert permissions is not None
        assert "readable" in permissions
        assert "writable" in permissions
        assert "executable" in permissions

    def test_check_file_permissions_nonexistent(self):
        """测试检查不存在的文件权限"""
        manager = FileManager()
        permissions = manager.check_file_permissions("nonexistent.txt")
        assert permissions is None

    def test_backup_file(self, tmp_path):
        """测试备份文件"""
        manager = FileManager()
        source_file = tmp_path / "source.txt"
        backup_dir = tmp_path / "backup"
        source_file.write_text("original content")
        
        result = manager.backup_file(str(source_file), str(backup_dir))
        assert result is True
        
        # 检查备份文件是否存在
        backup_files = list(backup_dir.glob("*.bak"))
        assert len(backup_files) == 1

    def test_backup_file_nonexistent(self, tmp_path):
        """测试备份不存在的文件"""
        manager = FileManager()
        backup_dir = tmp_path / "backup"
        
        result = manager.backup_file("nonexistent.txt", str(backup_dir))
        assert result is False

    def test_cleanup_old_files(self, tmp_path):
        """测试清理旧文件"""
        manager = FileManager()
        
        # 创建一些测试文件
        (tmp_path / "new_file.txt").write_text("new")
        (tmp_path / "old_file.txt").write_text("old")
        
        # 这里主要测试函数调用不抛出异常
        # 实际的文件清理逻辑可能需要更复杂的测试
        result = manager.cleanup_old_files(str(tmp_path), days=1)
        assert result is True

    def test_validate_file_path(self):
        """测试验证文件路径"""
        manager = FileManager()
        
        # 测试有效路径
        result = manager.validate_file_path("/valid/path/file.txt")
        assert result["valid"] is True
        
        # 测试无效路径（包含非法字符）
        result = manager.validate_file_path("/invalid/path/file?.txt")
        assert result["valid"] is False
        assert "非法字符" in result["error"]

    @pytest.mark.parametrize("path,expected_valid", [
        ("/valid/path/file.txt", True),
        ("/path/with spaces/file.txt", True),
        ("/path/with?invalid/file.txt", False),
        ("/path/with*invalid/file.txt", False),
        ("/path/with|invalid/file.txt", False),
        ("", False),
    ])
    def test_validate_file_path_parametrized(self, path, expected_valid):
        """参数化测试文件路径验证"""
        manager = FileManager()
        result = manager.validate_file_path(path)
        assert result["valid"] == expected_valid


class TestCSVProcessor:
    """CSV处理器测试类"""

    def test_read_csv(self, temp_csv_file):
        """测试读取CSV文件"""
        processor = CSVProcessor()
        data = processor.read_csv(temp_csv_file)
        
        assert data is not None
        assert len(data) > 0
        assert isinstance(data, list)

    def test_read_csv_nonexistent(self):
        """测试读取不存在的CSV文件"""
        processor = CSVProcessor()
        data = processor.read_csv("nonexistent.csv")
        
        assert data is None

    def test_write_csv(self, tmp_path):
        """测试写入CSV文件"""
        processor = CSVProcessor()
        test_data = [
            ["col1", "col2", "col3"],
            ["val1", "val2", "val3"],
            ["val4", "val5", "val6"]
        ]
        
        output_file = tmp_path / "output.csv"
        result = processor.write_csv(str(output_file), test_data)
        
        assert result is True
        assert output_file.exists()
        
        # 验证写入的内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "col1,col2,col3" in content
            assert "val1,val2,val3" in content

    def test_validate_csv_data(self):
        """测试验证CSV数据"""
        processor = CSVProcessor()
        
        # 测试有效数据
        valid_data = [["col1", "col2"], ["val1", "val2"]]
        result = processor.validate_csv_data(valid_data)
        assert result["valid"] is True
        
        # 测试无效数据（空列表）
        invalid_data = []
        result = processor.validate_csv_data(invalid_data)
        assert result["valid"] is False


class TestDataValidator:
    """数据验证器测试类"""

    def test_validate_numeric(self):
        """测试验证数值数据"""
        validator = DataValidator()
        
        # 测试有效数值
        assert validator.validate_numeric("123") is True
        assert validator.validate_numeric("123.45") is True
        assert validator.validate_numeric("-123.45") is True
        
        # 测试无效数值
        assert validator.validate_numeric("abc") is False
        assert validator.validate_numeric("123abc") is False

    def test_validate_string(self):
        """测试验证字符串数据"""
        validator = DataValidator()
        
        # 测试有效字符串
        assert validator.validate_string("hello", min_length=1, max_length=10) is True
        assert validator.validate_string("test", min_length=1, max_length=10) is True
        
        # 测试无效字符串
        assert validator.validate_string("", min_length=1, max_length=10) is False
        assert validator.validate_string("toolongstring", min_length=1, max_length=5) is False

    def test_validate_range(self):
        """测试验证范围"""
        validator = DataValidator()
        
        # 测试有效范围
        assert validator.validate_range(5, 0, 10) is True
        assert validator.validate_range(0, 0, 10) is True
        assert validator.validate_range(10, 0, 10) is True
        
        # 测试无效范围
        assert validator.validate_range(-1, 0, 10) is False
        assert validator.validate_range(11, 0, 10) is False

    def test_validate_list(self):
        """测试验证列表"""
        validator = DataValidator()
        
        # 测试有效列表
        assert validator.validate_list([1, 2, 3], min_length=1, max_length=5) is True
        assert validator.validate_list(["a", "b"], min_length=1, max_length=5) is True
        
        # 测试无效列表
        assert validator.validate_list([], min_length=1, max_length=5) is False
        assert validator.validate_list([1, 2, 3, 4, 5, 6], min_length=1, max_length=5) is False


if __name__ == '__main__':
    pytest.main([__file__])
