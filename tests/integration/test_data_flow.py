"""
DNC参数计算系统 - 数据流集成测试
"""

import pytest
import tempfile
from pathlib import Path
from src.config.config_manager import ConfigManager
from src.data.csv_processor import CSVProcessor
from src.data.data_manager import DataManager
from src.utils.calculation import CalculationEngine


class TestDataFlow:
    """数据流集成测试"""
    
    def test_complete_data_flow(self, temp_config_dir, temp_data_dir):
        """测试完整的数据流：从配置到计算"""
        # 1. 配置管理
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
log_directory = logs

[APPLICATION]
version = 2.05
language = zh-CN

[CALCULATION]
precision = 4
auto_validate = true
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        assert config_manager.load_config() is True
        
        # 2. 创建测试数据
        master_dir = temp_data_dir / "master"
        master_dir.mkdir()
        
        # 创建master数据文件
        master_content = """product_id,model,length,width,height,density
P001,MODEL_A,100,50,25,1.0
P002,MODEL_B,150,75,30,1.2
P003,MODEL_C,80,40,20,0.8"""
        
        master_file = master_dir / "master_data.csv"
        master_file.write_text(master_content, encoding='utf-8')
        
        # 创建输入文件
        input_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5
P003,MODEL_C,8"""
        
        input_file = temp_data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        # 3. CSV处理
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        assert input_records is not None
        assert len(input_records) == 3
        
        # 4. 数据管理
        data_manager = DataManager(str(config_path))
        assert data_manager.load_csv_files() is True
        
        # 5. 计算引擎
        calculation_engine = CalculationEngine()
        
        # 6. 处理每条记录
        results = []
        for record in input_records:
            # 获取产品数据
            product_data = data_manager.get_product_data(record["model"])
            assert product_data is not None
            
            # 执行计算
            volume = calculation_engine.calculate_geometry("volume", product_data)
            surface_area = calculation_engine.calculate_geometry("surface_area", product_data)
            weight = calculation_engine.calculate_geometry("weight", product_data)
            
            # 验证计算
            calculated_params = {
                "volume": volume,
                "surface_area": surface_area,
                "weight": weight
            }
            
            is_valid = calculation_engine.validate_calculation(product_data, calculated_params)
            assert is_valid is True
            
            # 存储结果
            result = {
                "product_id": record["product_id"],
                "model": record["model"],
                "quantity": int(record["quantity"]),
                "input_parameters": product_data,
                "calculated_parameters": calculated_params,
                "success": True
            }
            results.append(result)
        
        # 验证最终结果
        assert len(results) == 3
        
        # 验证第一条记录的计算结果
        first_result = results[0]
        assert first_result["product_id"] == "P001"
        assert first_result["model"] == "MODEL_A"
        assert first_result["quantity"] == 10
        assert first_result["success"] is True
        
        # 验证计算参数
        calculated = first_result["calculated_parameters"]
        assert "volume" in calculated
        assert "surface_area" in calculated
        assert "weight" in calculated
        
        # 验证体积计算正确性
        expected_volume = 100 * 50 * 25  # length * width * height
        assert calculated["volume"] == expected_volume
        
        # 验证重量计算正确性
        expected_weight = expected_volume * 1.0  # volume * density
        assert calculated["weight"] == expected_weight
    
    def test_data_flow_with_invalid_input(self, temp_config_dir, temp_data_dir):
        """测试包含无效输入的数据流"""
        # 配置管理
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 创建master数据
        master_dir = temp_data_dir / "master"
        master_dir.mkdir()
        
        master_content = """product_id,model,length,width,height
P001,MODEL_A,100,50,25"""
        master_file = master_dir / "master_data.csv"
        master_file.write_text(master_content, encoding='utf-8')
        
        # 创建包含无效记录的输入文件
        input_content = """product_id,model,quantity
P001,MODEL_A,10
,MODEL_B,5  # 缺少product_id
P003,,8     # 缺少model
P004,MODEL_D,invalid  # 无效数量"""
        
        input_file = temp_data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        # CSV处理
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        # 应该只返回有效记录
        assert input_records is not None
        assert len(input_records) == 1  # 只有第一条记录有效
        assert input_records[0]["product_id"] == "P001"
    
    def test_data_flow_missing_master_data(self, temp_config_dir, temp_data_dir):
        """测试缺少master数据的数据流"""
        # 配置管理
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 创建输入文件（不创建master数据）
        input_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5"""
        
        input_file = temp_data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        # 数据管理
        data_manager = DataManager(str(config_path))
        success = data_manager.load_csv_files()
        
        # 应该加载失败，因为master目录不存在
        assert success is False
        
        # CSV处理应该仍然工作
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        assert input_records is not None
        assert len(input_records) == 2
    
    def test_data_flow_with_calculation_errors(self, temp_config_dir, temp_data_dir):
        """测试包含计算错误的数据流"""
        # 配置管理
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 创建master数据（包含无效参数）
        master_dir = temp_data_dir / "master"
        master_dir.mkdir()
        
        master_content = """product_id,model,length,width,height
P001,MODEL_A,100,50,invalid  # 无效高度值
P002,MODEL_B,150,75,30"""
        
        master_file = master_dir / "master_data.csv"
        master_file.write_text(master_content, encoding='utf-8')
        
        # 创建输入文件
        input_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5"""
        
        input_file = temp_data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        # 数据管理
        data_manager = DataManager(str(config_path))
        data_manager.load_csv_files()
        
        # CSV处理
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        # 计算引擎
        calculation_engine = CalculationEngine()
        
        results = []
        for record in input_records:
            product_data = data_manager.get_product_data(record["model"])
            
            if product_data:
                # 尝试计算
                volume = calculation_engine.calculate_geometry("volume", product_data)
                
                result = {
                    "product_id": record["product_id"],
                    "model": record["model"],
                    "success": volume is not None
                }
                results.append(result)
        
        # 验证结果
        assert len(results) == 2
        
        # MODEL_A应该计算失败（无效参数）
        model_a_result = next(r for r in results if r["model"] == "MODEL_A")
        assert model_a_result["success"] is False
        
        # MODEL_B应该计算成功
        model_b_result = next(r for r in results if r["model"] == "MODEL_B")
        assert model_b_result["success"] is True
    
    def test_data_flow_performance(self, temp_config_dir, temp_data_dir):
        """测试数据流性能"""
        import time
        
        # 配置管理
        config_path = temp_config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        # 创建大量测试数据
        master_dir = temp_data_dir / "master"
        master_dir.mkdir()
        
        # 生成100条master记录
        master_lines = ["product_id,model,length,width,height,density"]
        for i in range(100):
            master_lines.append(f"P{i:03d},MODEL_{i%10},{100+i},{50+i%20},{25+i%10},1.0")
        
        master_file = master_dir / "master_data.csv"
        master_file.write_text("\n".join(master_lines), encoding='utf-8')
        
        # 生成50条输入记录
        input_lines = ["product_id,model,quantity"]
        for i in range(50):
            input_lines.append(f"P{i:03d},MODEL_{i%10},{i+1}")
        
        input_file = temp_data_dir / "input.csv"
        input_file.write_text("\n".join(input_lines), encoding='utf-8')
        
        # 测量处理时间
        start_time = time.time()
        
        # 数据管理
        data_manager = DataManager(str(config_path))
        data_manager.load_csv_files()
        
        # CSV处理
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        # 计算引擎
        calculation_engine = CalculationEngine()
        
        results = []
        for record in input_records:
            product_data = data_manager.get_product_data(record["model"])
            if product_data:
                volume = calculation_engine.calculate_geometry("volume", product_data)
                results.append({
                    "product_id": record["product_id"],
                    "volume": volume
                })
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 验证性能
        assert len(results) == 50
        assert processing_time < 5.0  # 处理50条记录应该在5秒内完成
        
        print(f"处理50条记录耗时: {processing_time:.2f}秒")


if __name__ == "__main__":
    pytest.main([__file__])
