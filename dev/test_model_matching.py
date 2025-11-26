# 测试型号匹配修复
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

class MockDataManager:
    def get_table_by_name(self, table_name):
        if table_name == 'type_define.csv':
            return [
                {'NO': '220', 'TYPE': 'GPT25GT3060_A', 'DEFINE1': '', 'DEFINE2': ''},
                {'NO': '262', 'TYPE': 'GPT25GT3060_B', 'DEFINE1': '', 'DEFINE2': ''},
                {'NO': '1', 'TYPE': 'GPA18GT15040_A', 'DEFINE1': '', 'DEFINE2': ''}
            ]
        return []

class MockLogger:
    def info(self, msg):
        print('LOG:', msg)
    def error(self, msg):
        print('ERROR:', msg)

class MockMainWindow:
    def __init__(self):
        self.data_manager = MockDataManager()
        self.logger = MockLogger()
    
    def _find_matching_model(self, input_model):
        """根据文档描述的方法，从后往前逐字符删除进行型号匹配"""
        try:
            # 获取type_define.csv中的所有型号
            type_define_data = self.data_manager.get_table_by_name('type_define.csv')
            if not type_define_data:
                return None

            # 从输入型号的末尾开始逐字符删除，查找匹配
            search_string = input_model
            while len(search_string) > 0:
                for row in type_define_data:
                    type_value = row.get('TYPE', '')
                    if type_value and search_string == type_value:
                        self.logger.info(f"找到匹配型号: {type_value} (从输入 {input_model} 匹配)")
                        return type_value
                    
                    # 额外尝试将连字符替换为下划线进行匹配
                    # 这处理输入格式与数据库格式不一致的情况（如 "GPT25GT3060-A-H8" 与 "GPT25GT3060_A"）
                    normalized_search = search_string.replace('-', '_')
                    if type_value and normalized_search == type_value:
                        self.logger.info(f"找到匹配型号: {type_value} (从输入 {input_model} 通过连字符转下划线匹配)")
                        return type_value

                # 删除最后一个字符，继续搜索
                search_string = search_string[:-1]

            # 如果上面的搜索没有找到，尝试其他匹配方法
            # 检查是否是完全匹配
            for row in type_define_data:
                type_value = row.get('TYPE', '')
                if type_value and input_model == type_value:
                    self.logger.info(f"找到完全匹配型号: {type_value}")
                    return type_value
                
                # 额外尝试将连字符替换为下划线进行完全匹配
                normalized_input = input_model.replace('-', '_')
                if type_value and normalized_input == type_value:
                    self.logger.info(f"找到完全匹配型号: {type_value} (从输入 {input_model} 通过连字符转下划线匹配)")
                    return type_value

            return None

        except Exception as e:
            self.logger.error(f"型号匹配失败: {e}")
            return None

# 测试
if __name__ == "__main__":
    main_window = MockMainWindow()
    
    print("测试1: GPT25GT3060-A-H8 (应该匹配到 GPT25GT3060_A)")
    result = main_window._find_matching_model('GPT25GT3060-A-H8')
    print('匹配结果:', result)
    
    print("\n测试2: GPA18GT15040_A (应该完全匹配)")
    result = main_window._find_matching_model('GPA18GT15040_A')
    print('匹配结果:', result)
    
    print("\n测试3: GPT25GT3060-A (应该匹配到 GPT25GT3060_A)")
    result = main_window._find_matching_model('GPT25GT3060-A')
    print('匹配结果:', result)