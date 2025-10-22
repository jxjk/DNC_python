"""
DNC参数计算系统 - CSV处理器单元测试
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path
from src.data.csv_processor import CSVProcessor


class TestCSVProcessor:
    """CSV处理器测试"""
    
    def test_csv_processor_creation(self):
        """测试CSV处理器创建"""
        processor = CSVProcessor("data/test.csv")
        assert processor.file_path == Path("data/test.csv")
    
    def test_read_csv_success(self, temp_data_dir):
        """测试成功读取CSV文件"""
        # 创建测试CSV文件
        csv_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5
P003,MODEL_C,8"""
        
        csv_file = temp_data_dir / "test.csv"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        processor = CSVProcessor(str(csv_file))
        data = processor.read_csv()
        
        assert data is not None
        assert len(data) == 3
        assert data[0]["product_id"] == "P001"
        assert data[0]["model"] == "MODEL_A"
        assert data[0]["quantity"] == "10"
    
    def test_read_csv_file_not_found(self):
        """测试读取不存在的CSV文件"""
        processor = CSVProcessor("data/nonexistent.csv")
        data = processor.read_csv()
        
        assert data is None
    
    def test_read_csv_empty_file(self, temp_data_dir):
        """测试读取空CSV文件"""
        csv_file = temp_data_dir / "empty.csv"
        csv_file.write_text("", encoding='utf-8')
        
        processor = CSVProcessor(str(csv_file))
        data = processor.read_csv()
        
        assert data is None
    
    def test_read_csv_with_headers_only(self, temp_data_dir):
        """测试读取只有表头的CSV文件"""
        csv_content = "product_id,model,quantity"
        csv_file = temp_data_dir / "headers_only.csv"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        processor = CSVProcessor(str(csv_file))
        data = processor.read_csv()
        
        assert data is not None
        assert len(data) == 0
    
    def test_write_csv_success(self, temp_data_dir):
        """测试成功写入CSV文件"""
        output_file = temp_data_dir / "output.csv"
        processor = CSVProcessor(str(output_file))
        
        data = [
            {"product_id": "P001", "model": "MODEL_A", "quantity": 10},
            {"product_id": "P002", "model": "MODEL_B", "quantity": 5}
        ]
        
        success = processor.write_csv(data)
        
        assert success is True
        assert output_file.exists()
        
        # 验证写入的内容
        written_content = output_file.read_text(encoding='utf-8')
        assert "product_id,model,quantity" in written_content
        assert "P001,MODEL_A,10" in written_content
        assert "P002,MODEL_B,5" in written_content
    
    def test_write_csv_empty_data(self, temp_data_dir):
        """测试写入空数据"""
        output_file = temp_data_dir / "empty_output.csv"
        processor = CSVProcessor(str(output_file))
        
        success = processor.write_csv([])
        
        assert success is True
        assert output_file.exists()
        
        # 验证写入的内容
        written_content = output_file.read_text(encoding='utf-8')
        assert written_content.strip() == ""  # 空文件
    
    def test_validate_data_valid(self):
        """测试验证有效数据"""
        processor = CSVProcessor("data/test.csv")
        
        valid_data = [
            {"product_id": "P001", "model": "MODEL_A", "quantity": "10"},
            {"product_id": "P002", "model": "MODEL_B", "quantity": "5"}
        ]
        
        errors = processor.validate_data(valid_data)
        
        assert len(errors) == 0
    
    def test_validate_data_missing_fields(self):
        """测试验证缺少字段的数据"""
        processor = CSVProcessor("data/test.csv")
        
        invalid_data = [
            {"product_id": "P001", "model": "MODEL_A"},  # 缺少quantity
            {"model": "MODEL_B", "quantity": "5"}  # 缺少product_id
        ]
        
        errors = processor.validate_data(invalid_data)
        
        assert len(errors) == 2
        assert any("缺少必需字段: quantity" in error for error in errors)
        assert any("缺少必需字段: product_id" in error for error in errors)
    
    def test_validate_data_invalid_quantity(self):
        """测试验证无效数量的数据"""
        processor = CSVProcessor("data/test.csv")
        
        invalid_data = [
            {"product_id": "P001", "model": "MODEL_A", "quantity": "invalid"},
            {"product_id": "P002", "model": "MODEL_B", "quantity": "-5"}
        ]
        
        errors = processor.validate_data(invalid_data)
        
        assert len(errors) == 2
        assert any("无效的数量值" in error for error in errors)
        assert any("数量必须为正数" in error for error in errors)
    
    def test_validate_data_empty_fields(self):
        """测试验证空字段的数据"""
        processor = CSVProcessor("data/test.csv")
        
        invalid_data = [
            {"product_id": "", "model": "MODEL_A", "quantity": "10"},  # 空product_id
            {"product_id": "P002", "model": "", "quantity": "5"}  # 空model
        ]
        
        errors = processor.validate_data(invalid_data)
        
        assert len(errors) == 2
        assert any("product_id不能为空" in error for error in errors)
        assert any("model不能为空" in error for error in errors)
    
    def test_process_input_csv_success(self, temp_data_dir):
        """测试成功处理输入CSV文件"""
        # 创建测试输入CSV文件
        input_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5"""
        
        input_file = temp_data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        processor = CSVProcessor(str(input_file))
        records = processor.process_input_csv()
        
        assert records is not None
        assert len(records) == 2
        
        # 验证记录内容
        assert records[0]["product_id"] == "P001"
        assert records[0]["model"] == "MODEL_A"
        assert records[0]["quantity"] == "10"
        
        assert records[1]["product_id"] == "P002"
        assert records[1]["model"] == "MODEL_B"
        assert records[1]["quantity"] == "5"
    
    def test_process_input_csv_with_validation_errors(self, temp_data_dir):
        """测试处理包含验证错误的输入CSV文件"""
        # 创建包含错误的测试CSV文件
        input_content = """product_id,model,quantity
P001,MODEL_A,10
,MODEL_B,5  # 缺少product_id
P003,,8     # 缺少model
P004,MODEL_D,invalid  # 无效数量"""
        
        input_file = temp_data_dir / "invalid_input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        processor = CSVProcessor(str(input_file))
        records = processor.process_input_csv()
        
        # 应该只返回有效记录
        assert records is not None
        assert len(records) == 1  # 只有第一条记录有效
        assert records[0]["product_id"] == "P001"
    
    def test_process_input_csv_file_not_found(self):
        """测试处理不存在的输入CSV文件"""
        processor = CSVProcessor("data/nonexistent.csv")
        records = processor.process_input_csv()
        
        assert records is None
    
    def test_read_csv_with_different_encodings(self, temp_data_dir):
        """测试使用不同编码读取CSV文件"""
        # 测试UTF-8编码
        utf8_content = "product_id,model,quantity\nP001,模型_A,10"
        utf8_file = temp_data_dir / "utf8.csv"
        utf8_file.write_text(utf8_content, encoding='utf-8')
        
        processor = CSVProcessor(str(utf8_file))
        data = processor.read_csv()
        
        assert data is not None
        assert len(data) == 1
        assert data[0]["model"] == "模型_A"
    
    def test_write_csv_with_special_characters(self, temp_data_dir):
        """测试写入包含特殊字符的CSV文件"""
        output_file = temp_data_dir / "special_chars.csv"
        processor = CSVProcessor(str(output_file))
        
        data = [
            {"product_id": "P001", "model": "模型_A", "quantity": 10},
            {"product_id": "P002", "model": "MODEL,B", "quantity": 5}  # 包含逗号
        ]
        
        success = processor.write_csv(data)
        
        assert success is True
        assert output_file.exists()
        
        # 验证写入的内容正确处理了特殊字符
        written_content = output_file.read_text(encoding='utf-8')
        assert "模型_A" in written_content
        # CSV应该正确处理包含逗号的值


if __name__ == "__main__":
    pytest.main([__file__])
