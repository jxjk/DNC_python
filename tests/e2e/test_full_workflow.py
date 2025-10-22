"""
DNC参数计算系统 - 完整工作流端到端测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.config.config_manager import ConfigManager
from src.data.csv_processor import CSVProcessor
from src.data.data_manager import DataManager
from src.utils.calculation import CalculationEngine


class TestFullWorkflow:
    """完整工作流端到端测试"""
    
    def test_complete_workflow_success(self, temp_workflow_dir):
        """测试完整的成功工作流"""
        # 1. 设置测试环境
        config_dir = temp_workflow_dir / "config"
        data_dir = temp_workflow_dir / "data"
        master_dir = data_dir / "master"
        output_dir = temp_workflow_dir / "output"
        
        config_dir.mkdir()
        data_dir.mkdir()
        master_dir.mkdir()
        output_dir.mkdir()
        
        # 2. 创建配置文件
        config_path = config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
output_directory = output
log_directory = logs

[APPLICATION]
version = 2.05
language = zh-CN
auto_save = true
backup_enabled = true

[UI]
theme = default
font_size = 10
window_width = 1024
window_height = 768

[CALCULATION]
precision = 4
rounding_method = round
auto_validate = true
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        # 3. 创建master数据文件
        master_content = """product_id,model,length,width,height,density,material
P001,MODEL_A,100.0,50.0,25.0,1.0,Steel
P002,MODEL_B,150.0,75.0,30.0,1.2,Aluminum
P003,MODEL_C,80.0,40.0,20.0,0.8,Plastic
P004,MODEL_D,120.0,60.0,35.0,1.5,Bronze
P005,MODEL_E,90.0,45.0,22.0,0.9,Copper"""
        
        master_file = master_dir / "products.csv"
        master_file.write_text(master_content, encoding='utf-8')
        
        # 4. 创建输入文件
        input_content = """product_id,model,quantity,priority
P001,MODEL_A,10,High
P002,MODEL_B,5,Medium
P003,MODEL_C,8,Low
P004,MODEL_D,3,High
P005,MODEL_E,12,Medium"""
        
        input_file = data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        # 5. 初始化系统组件
        config_manager = ConfigManager(str(config_path))
        assert config_manager.load_config() is True
        
        data_manager = DataManager(str(config_path))
        assert data_manager.load_csv_files() is True
        
        calculation_engine = CalculationEngine()
        
        # 6. 处理输入数据
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        assert input_records is not None
        assert len(input_records) == 5
        
        # 7. 执行批量计算
        batch_results = []
        total_records = len(input_records)
        successful_records = 0
        failed_records = 0
        error_messages = []
        
        for record in input_records:
            try:
                # 获取产品数据
                product_data = data_manager.get_product_data(record["model"])
                if not product_data:
                    raise ValueError(f"未找到产品型号: {record['model']}")
                
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
                if not is_valid:
                    raise ValueError("计算结果验证失败")
                
                # 创建结果记录
                result = {
                    "product_id": record["product_id"],
                    "model": record["model"],
                    "quantity": int(record["quantity"]),
                    "priority": record.get("priority", "Normal"),
                    "input_parameters": product_data,
                    "calculated_parameters": calculated_params,
                    "total_volume": volume * int(record["quantity"]),
                    "total_weight": weight * int(record["quantity"]),
                    "success": True
                }
                
                batch_results.append(result)
                successful_records += 1
                
            except Exception as e:
                failed_records += 1
                error_messages.append(f"产品 {record.get('product_id', 'Unknown')}: {str(e)}")
        
        # 8. 验证批量处理结果
        assert len(batch_results) == 5
        assert successful_records == 5
        assert failed_records == 0
        assert len(error_messages) == 0
        
        # 9. 验证具体计算结果
        # 验证第一条记录
        first_result = batch_results[0]
        assert first_result["product_id"] == "P001"
        assert first_result["model"] == "MODEL_A"
        assert first_result["quantity"] == 10
        assert first_result["priority"] == "High"
        assert first_result["success"] is True
        
        # 验证计算参数
        calculated = first_result["calculated_parameters"]
        assert "volume" in calculated
        assert "surface_area" in calculated
        assert "weight" in calculated
        
        # 验证体积计算
        expected_volume = 100.0 * 50.0 * 25.0
        assert calculated["volume"] == expected_volume
        
        # 验证重量计算
        expected_weight = expected_volume * 1.0  # density = 1.0
        assert calculated["weight"] == expected_weight
        
        # 验证总量计算
        assert first_result["total_volume"] == expected_volume * 10
        assert first_result["total_weight"] == expected_weight * 10
        
        # 10. 生成输出文件
        output_data = []
        for result in batch_results:
            output_record = {
                "product_id": result["product_id"],
                "model": result["model"],
                "quantity": result["quantity"],
                "priority": result["priority"],
                "length": result["input_parameters"].get("length"),
                "width": result["input_parameters"].get("width"),
                "height": result["input_parameters"].get("height"),
                "density": result["input_parameters"].get("density"),
                "material": result["input_parameters"].get("material"),
                "volume": result["calculated_parameters"]["volume"],
                "surface_area": result["calculated_parameters"]["surface_area"],
                "weight": result["calculated_parameters"]["weight"],
                "total_volume": result["total_volume"],
                "total_weight": result["total_weight"]
            }
            output_data.append(output_record)
        
        # 写入输出文件
        output_processor = CSVProcessor(str(output_dir / "results.csv"))
        success = output_processor.write_csv(output_data)
        assert success is True
        
        # 验证输出文件存在
        output_file = output_dir / "results.csv"
        assert output_file.exists()
        
        # 11. 生成汇总报告
        total_volume = sum(r["total_volume"] for r in batch_results)
        total_weight = sum(r["total_weight"] for r in batch_results)
        total_quantity = sum(r["quantity"] for r in batch_results)
        
        summary = {
            "total_records": total_records,
            "successful_records": successful_records,
            "failed_records": failed_records,
            "success_rate": (successful_records / total_records) * 100,
            "total_quantity": total_quantity,
            "total_volume": total_volume,
            "total_weight": total_weight
        }
        
        # 验证汇总数据
        assert summary["total_records"] == 5
        assert summary["successful_records"] == 5
        assert summary["failed_records"] == 0
        assert summary["success_rate"] == 100.0
        assert summary["total_quantity"] == 38  # 10+5+8+3+12
        
        print("完整工作流测试成功完成")
        print(f"处理记录: {summary['total_records']}")
        print(f"成功记录: {summary['successful_records']}")
        print(f"失败记录: {summary['failed_records']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"总数量: {summary['total_quantity']}")
        print(f"总体积: {summary['total_volume']:.2f}")
        print(f"总重量: {summary['total_weight']:.2f}")
    
    def test_workflow_with_partial_failures(self, temp_workflow_dir):
        """测试包含部分失败的工作流"""
        # 设置测试环境
        config_dir = temp_workflow_dir / "config"
        data_dir = temp_workflow_dir / "data"
        master_dir = data_dir / "master"
        
        config_dir.mkdir()
        data_dir.mkdir()
        master_dir.mkdir()
        
        # 创建配置文件
        config_path = config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        # 创建不完整的master数据
        master_content = """product_id,model,length,width,height,density
P001,MODEL_A,100.0,50.0,25.0,1.0
P003,MODEL_C,80.0,40.0,20.0,0.8"""
        # 注意：缺少MODEL_B的数据
        
        master_file = master_dir / "products.csv"
        master_file.write_text(master_content, encoding='utf-8')
        
        # 创建输入文件
        input_content = """product_id,model,quantity
P001,MODEL_A,10
P002,MODEL_B,5  # 这个会失败，因为master中没有MODEL_B
P003,MODEL_C,8"""
        
        input_file = data_dir / "input.csv"
        input_file.write_text(input_content, encoding='utf-8')
        
        # 初始化系统
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        data_manager = DataManager(str(config_path))
        data_manager.load_csv_files()
        
        calculation_engine = CalculationEngine()
        
        # 处理数据
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        # 执行计算
        batch_results = []
        successful_records = 0
        failed_records = 0
        
        for record in input_records:
            try:
                product_data = data_manager.get_product_data(record["model"])
                if not product_data:
                    raise ValueError(f"未找到产品型号: {record['model']}")
                
                volume = calculation_engine.calculate_geometry("volume", product_data)
                
                result = {
                    "product_id": record["product_id"],
                    "model": record["model"],
                    "success": True
                }
                batch_results.append(result)
                successful_records += 1
                
            except Exception:
                failed_records += 1
        
        # 验证部分失败的结果
        assert len(batch_results) == 2  # 只有MODEL_A和MODEL_C成功
        assert successful_records == 2
        assert failed_records == 1  # MODEL_B失败
    
    def test_workflow_with_large_dataset(self, temp_workflow_dir):
        """测试大数据集工作流"""
        import time
        
        # 设置测试环境
        config_dir = temp_workflow_dir / "config"
        data_dir = temp_workflow_dir / "data"
        master_dir = data_dir / "master"
        
        config_dir.mkdir()
        data_dir.mkdir()
        master_dir.mkdir()
        
        # 创建配置文件
        config_path = config_dir / "config.ini"
        config_content = """
[PATHS]
master_directory = data/master
input_file = data/input.csv
"""
        config_path.write_text(config_content, encoding='utf-8')
        
        # 生成大量master数据
        master_lines = ["product_id,model,length,width,height,density"]
        for i in range(200):
            master_lines.append(f"P{i:03d},MODEL_{i%20},{100+i%50},{50+i%25},{25+i%10},1.0")
        
        master_file = master_dir / "products.csv"
        master_file.write_text("\n".join(master_lines), encoding='utf-8')
        
        # 生成大量输入数据
        input_lines = ["product_id,model,quantity"]
        for i in range(100):
            input_lines.append(f"P{i:03d},MODEL_{i%20},{i%10 + 1}")
        
        input_file = data_dir / "input.csv"
        input_file.write_text("\n".join(input_lines), encoding='utf-8')
        
        # 测量处理时间
        start_time = time.time()
        
        # 初始化系统
        config_manager = ConfigManager(str(config_path))
        config_manager.load_config()
        
        data_manager = DataManager(str(config_path))
        data_manager.load_csv_files()
        
        calculation_engine = CalculationEngine()
        
        # 处理数据
        csv_processor = CSVProcessor(str(input_file))
        input_records = csv_processor.process_input_csv()
        
        # 执行计算
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
        assert len(results) == 100
        assert processing_time < 10.0  # 处理100条记录应该在10秒内完成
        
        print(f"大数据集测试: 处理100条记录耗时 {processing_time:.2f}秒")


if __name__ == "__main__":
    pytest.main([__file__])
