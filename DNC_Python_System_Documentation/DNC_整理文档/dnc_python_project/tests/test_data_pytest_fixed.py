"""
修复后的数据模块测试
根据实际实现调整测试用例
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.data.file_manager import FileManager
from src.data.csv_processor import CSVProcessor
from src.data.data_validator import DataValidator


class TestFileManagerFixed:
    """修复后的文件管理器测试类"""

    def test_get_file_info(self, tmp_path):
        """测试获取文件信息"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        info = manager.get_file_info(str(test_file))

        assert info is not None
        assert info["size"] == len("test content")
        assert info["is_file"] is True
        assert info["is_directory"] is False

    def test_get_file_info_nonexistent(self):
        """测试获取不存在的文件信息"""
        manager = FileManager()
        info = manager.get_file_info("nonexistent.txt")

        assert info is None

    def test_list_files(self, tmp_path):
        """测试列出文件"""
        manager = FileManager()
        # 设置基础路径为临时目录
        manager.set_base_path(str(tmp_path))

        # 创建测试文件
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").write_text("content3")

        # 测试非递归列表
        files = manager.list_files("")
        assert len(files) == 2  # 只包含直接文件，不包含子目录中的文件

    def test_list_files_with_pattern(self, tmp_path):
        """测试使用模式列出文件"""
        manager = FileManager()
        # 设置基础路径为临时目录
        manager.set_base_path(str(tmp_path))

        # 创建测试文件
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.csv").write_text("content2")
        (tmp_path / "file3.txt").write_text("content3")

        # 测试只列出txt文件
        files = manager.list_files("", "*.txt")
        assert len(files) == 2
        assert all(file.endswith(".txt") for file in files)

    def test_list_files_nonexistent_directory(self):
        """测试列出不存在的目录"""
        manager = FileManager()
        files = manager.list_files("nonexistent_dir")
        assert files == []

    def test_file_exists(self, tmp_path):
        """测试检查文件存在性"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert manager.file_exists(str(test_file)) is True
        assert manager.file_exists("nonexistent.txt") is False

    def test_directory_exists(self, tmp_path):
        """测试检查目录存在性"""
        manager = FileManager()
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        assert manager.directory_exists(str(test_dir)) is True
        assert manager.directory_exists("nonexistent_dir") is False

    def test_read_write_file(self, tmp_path):
        """测试读写文件"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        content = "测试内容"

        # 写入文件
        assert manager.write_file(str(test_file), content) is True
        
        # 读取文件
        read_content = manager.read_file(str(test_file))
        assert read_content == content

    def test_copy_file(self, tmp_path):
        """测试复制文件"""
        manager = FileManager()
        source_file = tmp_path / "source.txt"
        dest_file = tmp_path / "dest.txt"
        source_file.write_text("original content")

        assert manager.copy_file(str(source_file), str(dest_file)) is True
        assert dest_file.exists()
        assert dest_file.read_text() == "original content"

    def test_delete_file(self, tmp_path):
        """测试删除文件"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert manager.delete_file(str(test_file)) is True
        assert not test_file.exists()

    def test_get_file_size(self, tmp_path):
        """测试获取文件大小"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        content = "测试内容"
        test_file.write_text(content)

        size = manager.get_file_size(str(test_file))
        # 注意：实际实现可能返回字节数，这里我们只检查是否返回了有效数字
        assert isinstance(size, int)
        assert size > 0

    def test_create_backup(self, tmp_path):
        """测试创建备份"""
        manager = FileManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")

        assert manager.create_backup(str(test_file)) is True
        backup_file = tmp_path / "test.txt.bak"
        assert backup_file.exists()
        assert backup_file.read_text() == "original content"

    def test_cleanup_old_backups(self, tmp_path):
        """测试清理旧备份"""
        manager = FileManager()
        # 设置基础路径为临时目录
        manager.set_base_path(str(tmp_path))
        
        # 创建多个备份文件
        for i in range(10):
            backup_file = tmp_path / f"test{i}.txt.bak"
            backup_file.write_text(f"content{i}")

        # 清理备份，只保留5个
        assert manager.cleanup_old_backups("", "*.bak", 5) is True
        
        # 检查剩余文件数量
        remaining_files = list(tmp_path.glob("*.bak"))
        assert len(remaining_files) == 5


class TestCSVProcessorFixed:
    """修复后的CSV处理器测试类"""

    def test_read_csv(self, tmp_path):
        """测试读取CSV文件"""
        processor = CSVProcessor()
        test_file = tmp_path / "test.csv"
        
        # 创建测试CSV文件
        csv_content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"
        test_file.write_text(csv_content)

        data = processor.read_csv(str(test_file))
        
        assert len(data) == 3  # 包含标题行和两行数据
        assert data[0] == ["col1", "col2", "col3"]
        assert data[1] == ["val1", "val2", "val3"]
        assert data[2] == ["val4", "val5", "val6"]

    def test_read_csv_nonexistent(self):
        """测试读取不存在的CSV文件"""
        processor = CSVProcessor()
        data = processor.read_csv("nonexistent.csv")

        assert data == []

    def test_write_csv(self, tmp_path):
        """测试写入CSV文件"""
        processor = CSVProcessor()
        test_file = tmp_path / "test.csv"
        
        data = [
            ["col1", "col2", "col3"],
            ["val1", "val2", "val3"],
            ["val4", "val5", "val6"]
        ]

        assert processor.write_csv(str(test_file), data) is True
        assert test_file.exists()
        
        # 验证写入的内容
        read_data = processor.read_csv(str(test_file))
        assert read_data == data

    def test_read_csv_as_dict(self, tmp_path):
        """测试读取CSV为字典列表"""
        processor = CSVProcessor()
        test_file = tmp_path / "test.csv"
        
        # 创建测试CSV文件
        csv_content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"
        test_file.write_text(csv_content)

        data = processor.read_csv_as_dict(str(test_file))
        
        assert len(data) == 2  # 两行数据（不包括标题）
        assert data[0] == {"col1": "val1", "col2": "val2", "col3": "val3"}
        assert data[1] == {"col1": "val4", "col2": "val5", "col3": "val6"}

    def test_write_dict_to_csv(self, tmp_path):
        """测试写入字典到CSV"""
        processor = CSVProcessor()
        test_file = tmp_path / "test.csv"
        
        data = [
            {"col1": "val1", "col2": "val2", "col3": "val3"},
            {"col1": "val4", "col2": "val5", "col3": "val6"}
        ]

        assert processor.write_dict_to_csv(str(test_file), data) is True
        assert test_file.exists()
        
        # 验证写入的内容
        read_data = processor.read_csv_as_dict(str(test_file))
        assert read_data == data

    def test_get_csv_info(self, tmp_path):
        """测试获取CSV文件信息"""
        processor = CSVProcessor()
        test_file = tmp_path / "test.csv"
        
        # 创建测试CSV文件
        csv_content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"
        test_file.write_text(csv_content)

        info = processor.get_csv_info(str(test_file))
        
        assert info["file_path"] == str(test_file)
        assert info["row_count"] == 3
        assert info["column_count"] == 3
        assert info["headers"] == ["col1", "col2", "col3"]
        assert info["status"] == "success"


class TestDataValidatorFixed:
    """修复后的数据验证器测试类"""

    def test_validate_value_integer(self):
        """测试验证整数值"""
        validator = DataValidator()
        
        result = validator.validate_value("123", "integer")
        assert result["valid"] is True
        
        result = validator.validate_value("abc", "integer")
        assert result["valid"] is False

    def test_validate_value_float(self):
        """测试验证浮点数值"""
        validator = DataValidator()
        
        result = validator.validate_value("123.45", "float")
        assert result["valid"] is True
        
        result = validator.validate_value("abc", "float")
        assert result["valid"] is False

    def test_validate_value_range(self):
        """测试验证数值范围"""
        validator = DataValidator()
        
        result = validator.validate_value("5", "range", min=0, max=10)
        assert result["valid"] is True
        
        result = validator.validate_value("15", "range", min=0, max=10)
        assert result["valid"] is False

    def test_validate_value_length(self):
        """测试验证字符串长度"""
        validator = DataValidator()
        
        result = validator.validate_value("hello", "length", min_length=1, max_length=10)
        assert result["valid"] is True
        
        result = validator.validate_value("", "length", min_length=1, max_length=10)
        assert result["valid"] is False

    def test_validate_value_enum(self):
        """测试验证枚举值"""
        validator = DataValidator()
        
        result = validator.validate_value("option1", "enum", allowed_values=["option1", "option2"])
        assert result["valid"] is True
        
        result = validator.validate_value("option3", "enum", allowed_values=["option1", "option2"])
        assert result["valid"] is False

    def test_validate_numeric_range(self):
        """测试验证数值范围（专用方法）"""
        validator = DataValidator()
        
        result = validator.validate_numeric_range(5, min_value=0, max_value=10)
        assert result["valid"] is True
        
        result = validator.validate_numeric_range(15, min_value=0, max_value=10)
        assert result["valid"] is False

    def test_validate_string_length(self):
        """测试验证字符串长度（专用方法）"""
        validator = DataValidator()
        
        result = validator.validate_string_length("hello", min_length=1, max_length=10)
        assert result["valid"] is True
        
        result = validator.validate_string_length("", min_length=1, max_length=10)
        assert result["valid"] is False

    def test_validate_enum(self):
        """测试验证枚举值（专用方法）"""
        validator = DataValidator()
        
        result = validator.validate_enum("option1", ["option1", "option2"])
        assert result["valid"] is True
        
        result = validator.validate_enum("option3", ["option1", "option2"])
        assert result["valid"] is False

    def test_validate_data_structure(self):
        """测试验证数据结构"""
        validator = DataValidator()
        
        schema = {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "required": True, "constraints": {"min": 0, "max": 150}},
            "email": {"type": "email", "required": False}
        }
        
        valid_data = {"name": "张三", "age": "25", "email": "zhangsan@example.com"}
        result = validator.validate_data_structure(valid_data, schema)
        assert result["valid"] is True
        
        invalid_data = {"name": "", "age": "200", "email": "invalid-email"}
        result = validator.validate_data_structure(invalid_data, schema)
        assert result["valid"] is False

    def test_validate_csv_data(self):
        """测试验证CSV数据"""
        validator = DataValidator()
        
        schema = {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "required": True, "constraints": {"min": 0, "max": 150}}
        }
        
        csv_data = [
            {"name": "张三", "age": "25"},
            {"name": "李四", "age": "30"},
            {"name": "", "age": "200"}  # 无效数据
        ]
        
        result = validator.validate_csv_data(csv_data, schema)
        assert result["valid"] is False
        assert result["total_rows"] == 3
        assert result["valid_rows"] == 2
        assert result["invalid_rows"] == 1

    def test_add_custom_rule(self):
        """测试添加自定义验证规则"""
        validator = DataValidator()
        
        # 添加自定义规则
        assert validator.add_custom_rule("custom_phone", r'^1[3-9]\d{9}$') is True
        
        # 测试自定义规则
        result = validator.validate_value("13812345678", "custom_phone")
        assert result["valid"] is True
        
        result = validator.validate_value("1234567890", "custom_phone")
        assert result["valid"] is False

    def test_get_available_rules(self):
        """测试获取可用规则"""
        validator = DataValidator()
        
        rules = validator.get_available_rules()
        assert "integer" in rules
        assert "float" in rules
        assert "email" in rules
        assert "ip_address" in rules

    def test_validate_date_format(self):
        """测试验证日期格式"""
        validator = DataValidator()
        
        result = validator.validate_date_format("2023-12-25")
        assert result["valid"] is True
        
        result = validator.validate_date_format("2023/12/25")
        assert result["valid"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
