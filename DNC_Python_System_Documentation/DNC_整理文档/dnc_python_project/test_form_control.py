"""
表单控制功能测试脚本
测试表单控制器和ON/OFF管理器的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import ConfigManager
from src.ui.form_controller import FormController
from src.core.onoff_manager import OnOffManager


def test_form_controller():
    """测试表单控制器功能"""
    print("=" * 50)
    print("测试表单控制器功能")
    print("=" * 50)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager("config/master")
        if not config_manager.load_config():
            print("配置管理器初始化失败")
            return False
        
        # 初始化表单控制器
        form_controller = FormController(config_manager)
        
        # 加载关系配置
        if not form_controller.load_relation_config():
            print("关系配置加载失败")
            return False
        
        # 测试条件评估
        test_conditions = {
            'size1': 10,
            'size2': 20,
            'size3': 30
        }
        
        # 测试表单显示判断
        test_forms = ['Frm_Input', 'Frm_Calc', 'Frm_Info']
        for form_name in test_forms:
            should_display = form_controller.should_display_form(form_name, test_conditions)
            print(f"表单 {form_name} 显示状态: {should_display}")
        
        # 测试条件表达式评估
        test_expressions = [
            'size1 > 5',
            'size2 < 15',
            'size1 + size2 > 25'
        ]
        
        for expr in test_expressions:
            result = form_controller.evaluate_condition(expr)
            print(f"条件 '{expr}' 评估结果: {result}")
        
        print("表单控制器测试完成")
        return True
        
    except Exception as e:
        print(f"表单控制器测试失败: {e}")
        return False


def test_onoff_manager():
    """测试ON/OFF管理器功能"""
    print("\n" + "=" * 50)
    print("测试ON/OFF管理器功能")
    print("=" * 50)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager("config/master")
        if not config_manager.load_config():
            print("配置管理器初始化失败")
            return False
        
        # 初始化ON/OFF管理器
        onoff_manager = OnOffManager(config_manager)
        
        # 加载ON/OFF状态
        if not onoff_manager.load_onoff_state():
            print("ON/OFF状态加载失败")
            return False
        
        # 测试当前状态
        current_state = onoff_manager.get_current_state()
        print(f"当前ON/OFF状态: {current_state}")
        
        # 测试状态更新
        new_state = 1 if current_state == 0 else 0
        if onoff_manager.update_onoff_state(new_state):
            print(f"ON/OFF状态更新成功: {current_state} -> {new_state}")
        else:
            print("ON/OFF状态更新失败")
        
        # 测试状态循环
        if onoff_manager.cycle_next_state():
            print("ON/OFF状态循环成功")
        else:
            print("ON/OFF状态循环失败")
        
        # 测试switch控件
        test_switches = ['switch1', 'switch2']
        for switch_name in test_switches:
            switch_values = onoff_manager.get_switch_values(switch_name)
            print(f"Switch {switch_name}: {switch_values}")
            
            # 测试switch状态循环
            if onoff_manager.cycle_switch_state(switch_name):
                new_values = onoff_manager.get_switch_values(switch_name)
                print(f"Switch {switch_name} 状态循环后: {new_values}")
        
        print("ON/OFF管理器测试完成")
        return True
        
    except Exception as e:
        print(f"ON/OFF管理器测试失败: {e}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n" + "=" * 50)
    print("测试集成功能")
    print("=" * 50)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager("config/master")
        if not config_manager.load_config():
            print("配置管理器初始化失败")
            return False
        
        # 初始化表单控制器
        form_controller = FormController(config_manager)
        form_controller.load_relation_config()
        
        # 初始化ON/OFF管理器
        onoff_manager = OnOffManager(config_manager)
        onoff_manager.load_onoff_state()
        
        # 模拟表单处理流程
        form_data = {
            'size1': 15,
            'size2': 25,
            'onoff_state': 1,
            'switch_switch1': 'ON'
        }
        
        # 更新表单条件
        form_controller.update_variable('size1', form_data['size1'])
        form_controller.update_variable('size2', form_data['size2'])
        
        # 检查表单显示状态
        form_name = 'Frm_Input'
        should_display = form_controller.should_display_form(form_name, form_data)
        print(f"集成测试 - 表单 {form_name} 显示状态: {should_display}")
        
        # 更新ON/OFF状态
        if 'onoff_state' in form_data:
            onoff_manager.update_onoff_state(form_data['onoff_state'])
            print(f"集成测试 - ON/OFF状态已更新: {onoff_manager.get_current_state()}")
        
        # 获取switch状态
        switch_values = onoff_manager.get_switch_values('switch1')
        print(f"集成测试 - Switch1 状态: {switch_values}")
        
        print("集成测试完成")
        return True
        
    except Exception as e:
        print(f"集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始表单控制功能测试...")
    
    # 运行各项测试
    form_test_passed = test_form_controller()
    onoff_test_passed = test_onoff_manager()
    integration_test_passed = test_integration()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"表单控制器测试: {'通过' if form_test_passed else '失败'}")
    print(f"ON/OFF管理器测试: {'通过' if onoff_test_passed else '失败'}")
    print(f"集成功能测试: {'通过' if integration_test_passed else '失败'}")
    
    overall_success = form_test_passed and onoff_test_passed and integration_test_passed
    print(f"\n总体测试结果: {'全部通过' if overall_success else '存在失败'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
