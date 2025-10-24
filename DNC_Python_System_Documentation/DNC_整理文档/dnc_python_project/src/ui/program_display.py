import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QTextEdit, QPushButton, QScrollArea,
                            QSplitter, QFrame, QProgressBar)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from typing import Dict, Any, List


class NCHighlighter(QSyntaxHighlighter):
    """NC代码语法高亮器"""
    
    def __init__(self, document):
        super().__init__(document)
        self._init_formats()
    
    def _init_formats(self):
        """初始化格式"""
        # G代码格式
        self.g_code_format = QTextCharFormat()
        self.g_code_format.setForeground(QColor(0, 0, 255))  # 蓝色
        self.g_code_format.setFontWeight(QFont.Bold)
        
        # M代码格式
        self.m_code_format = QTextCharFormat()
        self.m_code_format.setForeground(QColor(128, 0, 128))  # 紫色
        self.m_code_format.setFontWeight(QFont.Bold)
        
        # 坐标格式
        self.coordinate_format = QTextCharFormat()
        self.coordinate_format.setForeground(QColor(255, 0, 0))  # 红色
        
        # 注释格式
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(0, 128, 0))  # 绿色
        self.comment_format.setFontItalic(True)
        
        # 行号格式
        self.line_number_format = QTextCharFormat()
        self.line_number_format.setForeground(QColor(128, 128, 128))  # 灰色
    
    def highlightBlock(self, text):
        """高亮文本块"""
        # 高亮注释
        comment_pattern = r'\(.*?\)'
        import re
        for match in re.finditer(comment_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), 
                          self.comment_format)
        
        # 高亮G代码
        g_code_pattern = r'\bG\d{1,3}\b'
        for match in re.finditer(g_code_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), 
                          self.g_code_format)
        
        # 高亮M代码
        m_code_pattern = r'\bM\d{1,3}\b'
        for match in re.finditer(m_code_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), 
                          self.m_code_format)
        
        # 高亮坐标
        coordinate_pattern = r'[XYZ][+-]?\d*\.?\d+'
        for match in re.finditer(coordinate_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), 
                          self.coordinate_format)
        
        # 高亮行号
        line_number_pattern = r'^N\d+'
        for match in re.finditer(line_number_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), 
                          self.line_number_format)


class ProgramDisplayWidget(QWidget):
    """程序显示组件"""
    
    # 信号定义
    program_saved = pyqtSignal(str)
    program_loaded = pyqtSignal(str)
    current_line_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program = ""
        self.current_line = 0
        self.total_lines = 0
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self) -> None:
        """初始化用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 程序信息组
        info_group = self._create_info_group()
        splitter.addWidget(info_group)
        
        # 代码显示组
        code_group = self._create_code_group()
        splitter.addWidget(code_group)
        
        # 设置分割比例
        splitter.setSizes([100, 400])
        
        main_layout.addWidget(splitter)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def _create_info_group(self) -> QGroupBox:
        """创建程序信息组"""
        group = QGroupBox("程序信息")
        layout = QVBoxLayout()
        
        # 基本信息布局
        info_layout = QHBoxLayout()
        
        # 程序名称
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("程序名称:"))
        self.program_name_label = QLabel("未加载程序")
        self.program_name_label.setStyleSheet("font-weight: bold; color: blue;")
        name_layout.addWidget(self.program_name_label)
        
        # 程序大小
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("程序大小:"))
        self.program_size_label = QLabel("0 行")
        size_layout.addWidget(self.program_size_label)
        
        # 当前行
        line_layout = QVBoxLayout()
        line_layout.addWidget(QLabel("当前行:"))
        self.current_line_label = QLabel("0")
        line_layout.addWidget(self.current_line_label)
        
        # 状态
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("状态:"))
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: green;")
        status_layout.addWidget(self.status_label)
        
        info_layout.addLayout(name_layout)
        info_layout.addLayout(size_layout)
        info_layout.addLayout(line_layout)
        info_layout.addLayout(status_layout)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("加载程序")
        self.save_button = QPushButton("保存程序")
        self.edit_button = QPushButton("编辑模式")
        self.view_button = QPushButton("查看模式")
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.view_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_code_group(self) -> QGroupBox:
        """创建代码显示组"""
        group = QGroupBox("NC程序代码")
        layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 代码编辑器
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Courier New", 10))
        self.code_editor.setReadOnly(True)
        
        # 设置语法高亮
        self.highlighter = NCHighlighter(self.code_editor.document())
        
        # 设置行号
        self.code_editor.setLineWrapMode(QTextEdit.NoWrap)
        
        scroll_area.setWidget(self.code_editor)
        layout.addWidget(scroll_area)
        
        group.setLayout(layout)
        return group
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.load_button.clicked.connect(self._on_load_clicked)
        self.save_button.clicked.connect(self._on_save_clicked)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.view_button.clicked.connect(self._on_view_clicked)
        
        # 连接文本变化信号
        self.code_editor.textChanged.connect(self._on_text_changed)
    
    def _on_load_clicked(self) -> None:
        """加载程序按钮点击处理"""
        # 这里应该实现文件选择对话框
        # 暂时使用模拟数据
        self.load_program("O1001", "模拟加工程序")
    
    def _on_save_clicked(self) -> None:
        """保存程序按钮点击处理"""
        program_text = self.code_editor.toPlainText()
        if program_text:
            self.program_saved.emit(program_text)
            self.status_label.setText("已保存")
            self.status_label.setStyleSheet("color: blue;")
    
    def _on_edit_clicked(self) -> None:
        """编辑模式按钮点击处理"""
        self.code_editor.setReadOnly(False)
        self.status_label.setText("编辑模式")
        self.status_label.setStyleSheet("color: orange;")
    
    def _on_view_clicked(self) -> None:
        """查看模式按钮点击处理"""
        self.code_editor.setReadOnly(True)
        self.status_label.setText("查看模式")
        self.status_label.setStyleSheet("color: green;")
    
    def _on_text_changed(self) -> None:
        """文本变化处理"""
        text = self.code_editor.toPlainText()
        lines = text.split('\n')
        self.total_lines = len([line for line in lines if line.strip()])
        self.program_size_label.setText(f"{self.total_lines} 行")
    
    def load_program(self, program_name: str, program_content: str) -> None:
        """加载程序"""
        self.current_program = program_content
        self.code_editor.setPlainText(program_content)
        self.program_name_label.setText(program_name)
        self.status_label.setText("已加载")
        self.status_label.setStyleSheet("color: green;")
        
        # 计算行数
        lines = program_content.split('\n')
        self.total_lines = len([line for line in lines if line.strip()])
        self.program_size_label.setText(f"{self.total_lines} 行")
        
        self.program_loaded.emit(program_name)
    
    def set_current_line(self, line_number: int) -> None:
        """设置当前执行行"""
        if 0 <= line_number < self.total_lines:
            self.current_line = line_number
            self.current_line_label.setText(str(line_number))
            self.current_line_changed.emit(line_number)
            
            # 高亮当前行
            self._highlight_current_line(line_number)
    
    def _highlight_current_line(self, line_number: int) -> None:
        """高亮当前行"""
        # 这里应该实现当前行高亮功能
        # 由于QTextEdit的高亮实现较复杂，这里暂时留空
        pass
    
    def get_program_text(self) -> str:
        """获取程序文本"""
        return self.code_editor.toPlainText()
    
    def set_program_text(self, text: str) -> None:
        """设置程序文本"""
        self.code_editor.setPlainText(text)
    
    def clear_program(self) -> None:
        """清空程序"""
        self.code_editor.clear()
        self.program_name_label.setText("未加载程序")
        self.program_size_label.setText("0 行")
        self.current_line_label.setText("0")
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("color: green;")
        self.current_program = ""
        self.current_line = 0
        self.total_lines = 0
    
    def show_progress(self, visible: bool) -> None:
        """显示/隐藏进度条"""
        self.progress_bar.setVisible(visible)
    
    def set_progress(self, value: int) -> None:
        """设置进度值"""
        self.progress_bar.setValue(value)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 测试数据
    test_program = """O1001 (测试加工程序)
N10 G90 G54 G00 X0 Y0
N20 M03 S1000
N30 G43 H01 Z10.0
N40 G01 Z-5.0 F200
N50 X50.0 Y50.0
N60 G02 X100.0 Y0 R50.0
N70 G01 X0 Y0
N80 G00 Z10.0
N90 M05
N100 M30
"""
    
    widget = ProgramDisplayWidget()
    widget.load_program("O1001", test_program)
    widget.show()
    
    sys.exit(app.exec_())
