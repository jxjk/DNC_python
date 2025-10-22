"""
DNC参数计算系统 - 数据模型单元测试
"""

import pytest
from pathlib import Path
from src.data.models import (
    Product, InputRecord, CalculationResult, MasterFile, 
    GeometryParameters, BatchProcessingResult, ExportConfiguration
)


class TestProduct:
    """产品数据模型测试"""
    
    def test_product_creation(self):
        """测试产品创建"""
        product = Product(
            product_id="P001",
            product_type="MODEL_A",
            parameters={"length": 100.0, "width": 50.0},
            drawing_path="drawings/model_a.pdf",
            quantity=10
        )
        
        assert product.product_id == "P001"
        assert product.product_type == "MODEL_A"
        assert product.parameters["length"] == 100.0
        assert product.drawing_path == "drawings/model_a.pdf"
        assert product.quantity == 10
    
    def test_get_parameter(self):
        """测试获取参数值"""
        product = Product(
            product_id="P001",
            product_type="MODEL_A",
            parameters={"length": 100.0, "width": 50.0}
        )
        
        assert product.get_parameter("length") == 100.0
        assert product.get_parameter("height", 25.0) == 25.0
        assert product.get_parameter("nonexistent") is None
    
    def test_update_parameter(self):
        """测试更新参数值"""
        product = Product(
            product_id="P001",
            product_type="MODEL_A",
            parameters={"length": 100.0}
        )
        
        product.update_parameter("width", 50.0)
        assert product.parameters["width"] == 50.0
        
        product.update_parameter("length", 120.0)
        assert product.parameters["length"] == 120.0
    
    def test_validate_parameters(self):
        """测试参数验证"""
        # 测试有效参数
        valid_product = Product(
            product_id="P001",
            product_type="MODEL_A",
            parameters={"NO": "001", "TYPE": "A"}
        )
        errors = valid_product.validate_parameters()
        assert len(errors) == 0
        
        # 测试缺少必需字段
        invalid_product = Product(
            product_id="P002",
            product_type="MODEL_B",
            parameters={"NO": "002"}  # 缺少TYPE字段
        )
        errors = invalid_product.validate_parameters()
        assert len(errors) == 1
        assert "缺少必需字段: TYPE" in errors[0]


class TestInputRecord:
    """输入记录模型测试"""
    
    def test_input_record_creation(self):
        """测试输入记录创建"""
        record = InputRecord(
            product_id="P001",
            model="MODEL_A",
            quantity=10,
            master_data={"length": 100.0, "width": 50.0}
        )
        
        assert record.product_id == "P001"
        assert record.model == "MODEL_A"
        assert record.quantity == 10
        assert record.master_data["length"] == 100.0
        assert record.calculated_params is None
    
    def test_to_dict(self):
        """测试转换为字典"""
        record = InputRecord(
            product_id="P001",
            model="MODEL_A",
            quantity=10,
            master_data={"length": 100.0},
            calculated_params={"volume": 125000.0}
        )
        
        result = record.to_dict()
        assert result["product_id"] == "P001"
        assert result["model"] == "MODEL_A"
        assert result["quantity"] == 10
        assert result["master_data"]["length"] == 100.0
        assert result["calculated_params"]["volume"] == 125000.0


class TestCalculationResult:
    """计算结果模型测试"""
    
    def test_calculation_result_creation(self):
        """测试计算结果创建"""
        result = CalculationResult(
            product_type="MODEL_A",
            input_parameters={"length": 100.0},
            calculated_parameters={"volume": 125000.0},
            success=True,
            calculation_time=0.001
        )
        
        assert result.product_type == "MODEL_A"
        assert result.input_parameters["length"] == 100.0
        assert result.calculated_parameters["volume"] == 125000.0
        assert result.success is True
        assert result.calculation_time == 0.001
    
    def test_is_valid(self):
        """测试有效性检查"""
        # 测试有效结果
        valid_result = CalculationResult(
            product_type="MODEL_A",
            input_parameters={},
            calculated_parameters={},
            success=True
        )
        assert valid_result.is_valid() is True
        
        # 测试失败结果
        failed_result = CalculationResult(
            product_type="MODEL_A",
            input_parameters={},
            calculated_parameters={},
            success=False,
            error_message="计算错误"
        )
        assert failed_result.is_valid() is False


class TestMasterFile:
    """Master文件模型测试"""
    
    def test_master_file_creation(self):
        """测试Master文件创建"""
        data = [
            {"id": "001", "name": "产品A", "length": 100.0},
            {"id": "002", "name": "产品B", "length": 150.0}
        ]
        
        master_file = MasterFile(
            file_name="test.csv",
            file_path=Path("data/master/test.csv"),
            data=data,
            description="测试数据文件"
        )
        
        assert master_file.file_name == "test.csv"
        assert master_file.get_record_count() == 2
        assert master_file.description == "测试数据文件"
    
    def test_find_records(self):
        """测试查找记录"""
        data = [
            {"id": "001", "name": "产品A"},
            {"id": "002", "name": "产品B"},
            {"id": "001", "name": "产品A2"}
        ]
        
        master_file = MasterFile(
            file_name="test.csv",
            file_path=Path("data/master/test.csv"),
            data=data
        )
        
        results = master_file.find_records("id", "001")
        assert len(results) == 2
        assert results[0]["name"] == "产品A"
        assert results[1]["name"] == "产品A2"
    
    def test_update_record(self):
        """测试更新记录"""
        data = [
            {"id": "001", "name": "产品A", "length": 100.0},
            {"id": "002", "name": "产品B", "length": 150.0}
        ]
        
        master_file = MasterFile(
            file_name="test.csv",
            file_path=Path("data/master/test.csv"),
            data=data
        )
        
        # 测试成功更新
        success = master_file.update_record("id", "001", {"length": 120.0})
        assert success is True
        assert master_file.data[0]["length"] == 120.0
        
        # 测试更新不存在的记录
        failed = master_file.update_record("id", "003", {"length": 200.0})
        assert failed is False


class TestGeometryParameters:
    """几何参数模型测试"""
    
    def test_geometry_parameters_creation(self):
        """测试几何参数创建"""
        geometry = GeometryParameters(
            length=100.0,
            width=50.0,
            height=25.0,
            volume=125000.0,
            surface_area=17500.0
        )
        
        assert geometry.length == 100.0
        assert geometry.width == 50.0
        assert geometry.height == 25.0
        assert geometry.volume == 125000.0
        assert geometry.surface_area == 17500.0
    
    def test_to_dict(self):
        """测试转换为字典"""
        geometry = GeometryParameters(
            length=100.0,
            width=50.0,
            diameter=None  # 不包含None值
        )
        
        result = geometry.to_dict()
        assert "length" in result
        assert "width" in result
        assert "diameter" not in result


class TestBatchProcessingResult:
    """批处理结果模型测试"""
    
    def test_batch_processing_result_creation(self):
        """测试批处理结果创建"""
        results = [
            CalculationResult(
                product_type="MODEL_A",
                input_parameters={},
                calculated_parameters={},
                success=True
            )
        ]
        
        batch_result = BatchProcessingResult(
            total_records=10,
            successful_records=8,
            failed_records=2,
            processing_time=5.5,
            results=results,
            error_messages=["错误1", "错误2"]
        )
        
        assert batch_result.total_records == 10
        assert batch_result.successful_records == 8
        assert batch_result.failed_records == 2
        assert batch_result.processing_time == 5.5
        assert len(batch_result.results) == 1
        assert len(batch_result.error_messages) == 2
    
    def test_success_rate(self):
        """测试成功率计算"""
        # 测试正常情况
        batch_result = BatchProcessingResult(
            total_records=10,
            successful_records=8,
            failed_records=2,
            processing_time=5.5,
            results=[],
            error_messages=[]
        )
        assert batch_result.success_rate() == 80.0
        
        # 测试零记录情况
        empty_batch = BatchProcessingResult(
            total_records=0,
            successful_records=0,
            failed_records=0,
            processing_time=0.0,
            results=[],
            error_messages=[]
        )
        assert empty_batch.success_rate() == 0.0


class TestExportConfiguration:
    """导出配置模型测试"""
    
    def test_export_configuration_creation(self):
        """测试导出配置创建"""
        config = ExportConfiguration(
            output_format="csv",
            include_calculated_params=True,
            include_master_data=False,
            include_errors=True,
            file_name_template="output_{timestamp}"
        )
        
        assert config.output_format == "csv"
        assert config.include_calculated_params is True
        assert config.include_master_data is False
        assert config.include_errors is True
        assert config.file_name_template == "output_{timestamp}"
    
    def test_validate(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = ExportConfiguration(output_format="csv")
        errors = valid_config.validate()
        assert len(errors) == 0
        
        # 测试无效格式
        invalid_config = ExportConfiguration(output_format="pdf")
        errors = invalid_config.validate()
        assert len(errors) == 1
        assert "不支持的输出格式" in errors[0]


if __name__ == "__main__":
    pytest.main([__file__])
