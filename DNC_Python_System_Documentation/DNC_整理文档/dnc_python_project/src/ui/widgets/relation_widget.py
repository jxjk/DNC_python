"""
关系控件
用于显示参数间的关系和依赖
"""

from typing import Optional, List, Dict
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt


class RelationWidget(QWidget):
    """关系控件"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.relations = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("参数关系图")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 关系树
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["参数", "描述", "值", "状态"])
        self.tree_widget.setColumnWidth(0, 120)
        self.tree_widget.setColumnWidth(1, 200)
        self.tree_widget.setColumnWidth(2, 80)
        self.tree_widget.setColumnWidth(3, 80)
        layout.addWidget(self.tree_widget)
    
    def set_relations(self, relations: List[Dict]):
        """设置关系数据"""
        self.relations = relations
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        self.tree_widget.clear()
        
        # 按依赖关系构建树
        root_items = {}
        all_items = {}
        
        # 第一遍：创建所有项
        for relation in self.relations:
            macro = relation.get('macro', '')
            description = relation.get('description', '')
            value = relation.get('value', '')
            status = relation.get('status', '未知')
            dependencies = relation.get('dependencies', [])
            
            item = QTreeWidgetItem([macro, description, str(value), status])
            all_items[macro] = item
            
            # 如果没有依赖项，添加到根节点
            if not dependencies:
                self.tree_widget.addTopLevelItem(item)
                root_items[macro] = item
        
        # 第二遍：建立父子关系
        for relation in self.relations:
            macro = relation.get('macro', '')
            dependencies = relation.get('dependencies', [])
            
            if macro in all_items:
                item = all_items[macro]
                
                # 为每个依赖项添加子项
                for dep_macro in dependencies:
                    if dep_macro in all_items:
                        dep_item = all_items[dep_macro]
                        item.addChild(dep_item)
                        
                        # 如果依赖项在根节点中，移除它
                        if dep_macro in root_items:
                            index = self.tree_widget.indexOfTopLevelItem(root_items[dep_macro])
                            if index >= 0:
                                self.tree_widget.takeTopLevelItem(index)
                            del root_items[dep_macro]
        
        # 展开所有项
        self.tree_widget.expandAll()
    
    def clear(self):
        """清空显示"""
        self.tree_widget.clear()
        self.relations = []
