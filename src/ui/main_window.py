import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..data.data_manager import DataManager
from ..config.config_manager import ConfigManager
from ..data.models import InputRecord, CalculationResult

class MainWindow:
    """主窗口类，负责管理应用程序的主要界面"""
    
    def __init__(self, config_manager: ConfigManager, data_manager: DataManager):
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("DNC参数计算系统")
        self.root.geometry("1200x800")

    def _configure_styles(self):
        """配置界面样式，使界面更美观易读"""
        # 获取ttk样式对象
        style = ttk.Style()
        
        # 配置主题
        try:
            style.theme_use('clam')  # 使用clam主题，更现代
        except:
            pass  # 如果主题不可用则使用默认主题

        # 配置标签样式
        style.configure('Title.TLabelframe', font=('Microsoft YaHei', 12, 'bold'), foreground='darkblue')
        style.configure('Control.TLabelframe', font=('Microsoft YaHei', 11, 'bold'), foreground='darkgreen')
        style.configure('Bottom.TLabelframe', font=('Microsoft YaHei', 12, 'bold'), foreground='darkred')
        style.configure('TLabel', font=('Microsoft YaHei', 10))
        style.configure('TCheckbutton', font=('Microsoft YaHei', 10))
        
        # 配置按钮样式
        style.configure('Action.TButton', font=('Microsoft YaHei', 10, 'bold'), padding=6)
        style.configure('Send.TButton', font=('Microsoft YaHei', 12, 'bold'), 
                       foreground='white', background='#228B22', padding=8)  # 森林绿，更显眼
        style.map('Send.TButton', background=[('active', '#006400')], foreground=[('active', 'white')])  # 深绿色激活状态
        
        # 配置输入框样式
        style.configure('Model.TEntry', font=('Microsoft YaHei', 12), fieldbackground='#f0f8ff')
        style.configure('Barcode.TEntry', font=('Consolas', 12), fieldbackground='#fff8dc')
        style.map('Barcode.TEntry', fieldbackground=[('focus', '#ffffff')])
        style.configure('Input.TEntry', font=('Consolas', 10), fieldbackground='#e6f3ff')  # input控件样式
        style.configure('Measure.TEntry', font=('Consolas', 10), fieldbackground='#f0fff0')  # measure控件样式
        style.configure('Correct.TEntry', font=('Consolas', 10), fieldbackground='#fff0f5')  # correct控件样式
        
    def _create_widgets(self):
        """创建界面组件，与VB.NET界面功能对应"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建顶部控制区域(对应VB.NET中的TB_Model, TB_Barcode等)
        self._create_control_area()
        
        # 创建中央数据显示区域(对应VB.NET中的Panel1, FlowLayoutPanel1)
        self._create_data_display_area()
        
        # 创建底部控制区域(对应VB.NET中的按钮区域)
        self._create_bottom_control_area()
        
        # 创建状态栏
        self._create_status_bar()
        
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开输入文件", command=self._open_input_file)
        file_menu.add_command(label="导出结果", command=self._export_results)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._exit_application)
        
        # 数据菜单
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="数据", menu=data_menu)
        data_menu.add_command(label="重新加载数据", command=self._reload_data)
        data_menu.add_command(label="查看数据统计", command=self._show_statistics)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="设置", command=self._show_settings)
        tools_menu.add_command(label="计算器", command=self._show_calculator)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
        
    def _create_control_area(self):
        """创建控制区域，包括型号显示和输入功能"""
        # 创建型号显示区域 (对应VB.NET的TB_Model)
        model_frame = ttk.LabelFrame(self.main_frame, text="型号信息", padding="15", style='Title.TLabelframe')
        model_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        model_frame.configure(relief='groove', borderwidth=2)
        
        # 型号显示
        ttk.Label(model_frame, text="型号:", font=("Microsoft YaHei", 11, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(5, 5))
        self.TB_Model_var = tk.StringVar()
        self.TB_Model = ttk.Entry(model_frame, textvariable=self.TB_Model_var, width=50, font=("Microsoft YaHei", 12), 
                                  style='Model.TEntry')
        self.TB_Model.grid(row=0, column=1, padx=(5, 15), sticky=(tk.W, tk.E))
        self.TB_Model.config(state='readonly', foreground='blue', background='#f0f8ff')  # 设为只读，通过条码输入更新
        
        # 程序显示 (对应VB.NET的TB_Prg)
        ttk.Label(model_frame, text="程序:", font=("Microsoft YaHei", 11, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.TB_Prg_var = tk.StringVar()
        self.TB_Prg = ttk.Entry(model_frame, textvariable=self.TB_Prg_var, width=15, font=("Microsoft YaHei", 10))
        self.TB_Prg.grid(row=0, column=3, padx=(5, 5))
        self.TB_Prg.config(state='readonly', foreground='darkgreen')  # 设为只读

        # 配置列权重
        model_frame.columnconfigure(1, weight=1)

        # 创建控制面板 (原有的输入文件功能)
        control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding="12", style='Control.TLabelframe')
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.configure(relief='groove', borderwidth=2)
        
        # 输入文件选择
        ttk.Label(control_frame, text="输入文件:", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky=tk.W, padx=(5, 5))
        self.input_file_var = tk.StringVar()
        self.input_file_entry = ttk.Entry(control_frame, textvariable=self.input_file_var, width=40, font=("Microsoft YaHei", 10))
        self.input_file_entry.grid(row=0, column=1, padx=(5, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="浏览...", command=self._browse_input_file, style='Action.TButton').grid(row=0, column=2, padx=(5, 10))
        
        # 处理按钮
        ttk.Button(control_frame, text="处理输入文件", command=self._process_input_file, style='Action.TButton').grid(row=0, column=3, padx=(5, 10))
        ttk.Button(control_frame, text="清空结果", command=self._clear_results, style='Action.TButton').grid(row=0, column=4, padx=(5, 10))
        
        # 搜索框
        ttk.Label(control_frame, text="搜索产品:", font=("Microsoft YaHei", 10)).grid(row=1, column=0, sticky=tk.W, pady=(12, 0), padx=(5, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=25, font=("Microsoft YaHei", 10))
        self.search_entry.grid(row=1, column=1, padx=(5, 10), pady=(12, 0), sticky=(tk.W, tk.E))
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        ttk.Button(control_frame, text="搜索", command=self._search_products, style='Action.TButton').grid(row=1, column=2, pady=(12, 0), padx=(0, 10))
        
        # 配置列权重
        control_frame.columnconfigure(1, weight=1)
        
    def _create_data_display_area(self):
        """创建数据显示区域"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 输入数据标签页
        self.input_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.input_tab, text="输入数据")
        self._create_input_data_tab()
        
        # 计算结果标签页
        self.result_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.result_tab, text="计算结果")
        self._create_result_tab()
        
        # 错误信息标签页
        self.error_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.error_tab, text="错误信息")
        self._create_error_tab()
        
        # 产品目录标签页
        self.catalog_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.catalog_tab, text="产品目录")
        self._create_catalog_tab()
        
    def _create_input_data_tab(self):
        """创建输入数据标签页"""
        # 创建树形视图显示输入数据
        columns = ('product_id', 'model', 'quantity')
        self.input_tree = ttk.Treeview(self.input_tab, columns=columns, show='headings')
        
        # 设置列标题
        self.input_tree.heading('product_id', text='产品编号')
        self.input_tree.heading('model', text='产品型号')
        self.input_tree.heading('quantity', text='数量')
        
        # 设置列宽
        self.input_tree.column('product_id', width=150)
        self.input_tree.column('model', width=200)
        self.input_tree.column('quantity', width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.input_tab, orient=tk.VERTICAL, command=self.input_tree.yview)
        self.input_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.input_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.input_tab.columnconfigure(0, weight=1)
        self.input_tab.rowconfigure(0, weight=1)
        
    def _create_result_tab(self):
        """创建计算结果标签页"""
        # 创建树形视图显示计算结果
        columns = ('product_id', 'model', 'quantity', 'volume', 'surface_area', 'weight')
        self.result_tree = ttk.Treeview(self.result_tab, columns=columns, show='headings')
        
        # 设置列标题
        self.result_tree.heading('product_id', text='产品编号')
        self.result_tree.heading('model', text='产品型号')
        self.result_tree.heading('quantity', text='数量')
        self.result_tree.heading('volume', text='体积')
        self.result_tree.heading('surface_area', text='表面积')
        self.result_tree.heading('weight', text='重量')
        
        # 设置列宽
        self.result_tree.column('product_id', width=120)
        self.result_tree.column('model', width=150)
        self.result_tree.column('quantity', width=80)
        self.result_tree.column('volume', width=100)
        self.result_tree.column('surface_area', width=100)
        self.result_tree.column('weight', width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.result_tab, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.result_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.result_tab.columnconfigure(0, weight=1)
        self.result_tab.rowconfigure(0, weight=1)
        
    def _create_error_tab(self):
        """创建错误信息标签页"""
        # 创建文本框显示错误信息
        self.error_text = tk.Text(self.error_tab, wrap=tk.WORD, height=15)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.error_tab, orient=tk.VERTICAL, command=self.error_text.yview)
        self.error_text.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.error_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.error_tab.columnconfigure(0, weight=1)
        self.error_tab.rowconfigure(0, weight=1)
        
    def _create_catalog_tab(self):
        """创建产品目录标签页"""
        # 创建树形视图显示产品目录
        columns = ('product_type', 'description')
        self.catalog_tree = ttk.Treeview(self.catalog_tab, columns=columns, show='headings')
        
        # 设置列标题
        self.catalog_tree.heading('product_type', text='产品型号')
        self.catalog_tree.heading('description', text='描述')
        
        # 设置列宽
        self.catalog_tree.column('product_type', width=200)
        self.catalog_tree.column('description', width=400)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.catalog_tab, orient=tk.VERTICAL, command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.catalog_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.catalog_tab.columnconfigure(0, weight=1)
        self.catalog_tab.rowconfigure(0, weight=1)
        
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))  # 改为row=4，避免与bottom_frame(row=3)重叠
        
    def _create_bottom_control_area(self):
        """创建底部控制区域，对应VB.NET中的按钮区域"""
        # 创建底部控制面板
        bottom_frame = ttk.LabelFrame(self.main_frame, text="条码/操作面板", padding="20", style='Bottom.TLabelframe')
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.configure(relief='groove', borderwidth=2)
        
        # 对应VB.NET中的TB_Barcode, Btn_Keyboard, Btn_send, Btn_chgOperator
        # 条码输入框(对应TB_Barcode)
        ttk.Label(bottom_frame, text="条码/型号输入:", font=("Microsoft YaHei", 11, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(5, 10))
        self.barcode_var = tk.StringVar()
        self.barcode_entry = ttk.Entry(bottom_frame, textvariable=self.barcode_var, width=45, font=("Consolas", 12), 
                                       style='Barcode.TEntry')
        self.barcode_entry.grid(row=0, column=1, padx=(5, 15), sticky=(tk.W, tk.E))
        self.barcode_entry.bind('<Return>', self._on_barcode_enter)
        # 设置焦点到条码输入框，便于扫描枪输入
        self.barcode_entry.focus()
        
        # 第二行按钮
        ttk.Button(bottom_frame, text="虚拟键盘", command=self._show_keyboard, style='Action.TButton').grid(row=1, column=0, padx=(5, 10), pady=(10, 5))
        ttk.Button(bottom_frame, text="发送数据", command=self._send_data, style='Send.TButton').grid(row=1, column=1, padx=(5, 10), pady=(10, 5), sticky=(tk.W,))
        
        # 第三行按钮
        ttk.Button(bottom_frame, text="操作员设置", command=self._change_operator, style='Action.TButton').grid(row=2, column=0, padx=(5, 10), pady=(5, 5))
        ttk.Button(bottom_frame, text="程序切换", command=self._change_program, style='Action.TButton').grid(row=2, column=1, padx=(5, 10), pady=(5, 5), sticky=(tk.W,))
        # 程序切换按钮默认隐藏，有多个程序时显示
        self.prg_change_btn = bottom_frame.winfo_children()[-1]  # 获取最后添加的按钮引用
        self.prg_change_btn.grid_remove()
        
        # 连接状态复选框(对应CB_Connection)
        self.connection_var = tk.BooleanVar()
        self.connection_check = ttk.Checkbutton(bottom_frame, text="设备连接", variable=self.connection_var, 
                                                style='Connection.TCheckbutton')
        self.connection_check.grid(row=1, column=2, rowspan=2, padx=(20, 5), pady=(10, 5), sticky=tk.N)
        
        # 配置列权重
        bottom_frame.columnconfigure(1, weight=1)
        
    def _setup_layout(self):
        """设置布局"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.main_frame.columnconfigure(0, weight=1)
        # 设置主框架的行权重，确保各部分比例合适
        self.main_frame.rowconfigure(0, weight=0)  # 型号信息行
        self.main_frame.rowconfigure(1, weight=0)  # 控制面板行
        self.main_frame.rowconfigure(2, weight=1)  # 标签页区域获得最多空间
        self.main_frame.rowconfigure(3, weight=0)  # 底部控制行
        self.main_frame.rowconfigure(4, weight=0)  # 状态栏行

        # 确保标签页也具有合适的布局
        if hasattr(self, 'notebook'):
            self.notebook.columnconfigure(0, weight=1)
            self.notebook.rowconfigure(0, weight=1)
        
    def _open_input_file(self):
        """打开输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.input_file_var.set(file_path)
            self.status_var.set(f"已选择输入文件: {file_path}")
            
    def _browse_input_file(self):
        """浏览输入文件"""
        self._open_input_file()
        
    def _process_input_file(self):
        """处理输入文件"""
        input_file_path = self.input_file_var.get()
        if not input_file_path:
            messagebox.showwarning("警告", "请先选择输入文件")
            return
            
        try:
            self.status_var.set("正在处理输入文件...")
            
            # 处理输入文件
            valid_records, error_messages = self.data_manager.process_input_file(input_file_path)
            
            # 更新界面
            self.current_data = valid_records
            self.error_messages = error_messages
            
            self._update_input_data_tab()
            self._update_result_tab()
            self._update_error_tab()
            
            # 更新状态
            total_records = len(valid_records)
            error_count = len(error_messages)
            self.status_var.set(f"处理完成: {total_records} 条有效记录, {error_count} 条错误")
            
            if error_count > 0:
                self.notebook.select(self.error_tab)
                messagebox.showwarning("处理完成", f"处理完成，但有 {error_count} 条错误，请查看错误信息标签页")
            else:
                messagebox.showinfo("处理完成", f"成功处理 {total_records} 条记录")
                
        except Exception as e:
            self.logger.error(f"处理输入文件失败: {e}")
            messagebox.showerror("错误", f"处理输入文件失败: {e}")
            self.status_var.set("处理失败")
            
    def _clear_results(self):
        """清空结果"""
        self.current_data = []
        self.error_messages = []
        
        # 清空所有显示
        for tree in [self.input_tree, self.result_tree, self.catalog_tree]:
            for item in tree.get_children():
                tree.delete(item)
                
        self.error_text.delete(1.0, tk.END)
        self.status_var.set("已清空结果")
        
    def _search_products(self):
        """搜索产品"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showinfo("提示", "请输入搜索关键词")
            return
            
        try:
            matching_products = self.data_manager.search_products(keyword)
            
            # 清空当前显示
            for item in self.catalog_tree.get_children():
                self.catalog_tree.delete(item)
                
            # 显示搜索结果
            for product_type in matching_products:
                product_data = self.data_manager.get_product_data(product_type)
                description = product_data.get('DESCRIPTION', '') if product_data else ''
                self.catalog_tree.insert('', tk.END, values=(product_type, description))
                
            self.notebook.select(self.catalog_tab)
            self.status_var.set(f"找到 {len(matching_products)} 个匹配的产品")
            
        except Exception as e:
            self.logger.error(f"搜索产品失败: {e}")
            messagebox.showerror("错误", f"搜索失败: {e}")
            
    def _on_search_changed(self, event):
        """搜索框内容改变时的处理"""
        # 可以在这里实现实时搜索
        pass
        
    def _update_input_data_tab(self):
        """更新输入数据标签页"""
        # 清空当前显示
        for item in self.input_tree.get_children():
            self.input_tree.delete(item)
            
        # 添加新数据
        for record in self.current_data:
            self.input_tree.insert('', tk.END, values=(
                record['product_id'],
                record['model'],
                record['quantity']
            ))
            
    def _update_result_tab(self):
        """更新计算结果标签页"""
        # 清空当前显示
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
            
        # 添加新数据
        for record in self.current_data:
            calculated_params = record.get('calculated_params', {})
            self.result_tree.insert('', tk.END, values=(
                record['product_id'],
                record['model'],
                record['quantity'],
                calculated_params.get('volume', ''),
                calculated_params.get('surface_area', ''),
                calculated_params.get('weight', '')
            ))
            
    def _update_error_tab(self):
        """更新错误信息标签页"""
        self.error_text.delete(1.0, tk.END)
        
        for error in self.error_messages:
            self.error_text.insert(tk.END, error + '\n')
            
    def _export_results(self):
        """导出结果"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有数据可导出")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="导出结果",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("正在导出结果...")
                
                # 准备导出数据
                export_data = []
                for record in self.current_data:
                    export_record = {
                        'product_id': record['product_id'],
                        'model': record['model'],
                        'quantity': record['quantity']
                    }
                    
                    # 添加计算参数
                    calculated_params = record.get('calculated_params', {})
                    for key, value in calculated_params.items():
                        export_record[key] = value
                        
                    export_data.append(export_record)
                    
                # 确定文件类型
                file_type = 'csv'
                if file_path.lower().endswith('.xlsx'):
                    file_type = 'excel'
                    
                # 保存文件
                if self.data_manager.save_data(export_data, file_path, file_type):
                    self.status_var.set(f"结果已导出到: {file_path}")
                    messagebox.showinfo("导出成功", f"结果已成功导出到: {file_path}")
                else:
                    messagebox.showerror("导出失败", "导出结果失败")
                    
            except Exception as e:
                self.logger.error(f"导出结果失败: {e}")
                messagebox.showerror("错误", f"导出失败: {e}")
                self.status_var.set("导出失败")
                
    def _reload_data(self):
        """重新加载数据"""
        try:
            self.status_var.set("正在重新加载数据...")
            
            if self.data_manager.load_csv_files():
                # 更新产品目录
                self._update_catalog_tab()
                self.status_var.set("数据重新加载成功")
                messagebox.showinfo("成功", "数据重新加载成功")
            else:
                self.status_var.set("数据重新加载失败")
                messagebox.showerror("错误", "数据重新加载失败")
                
        except Exception as e:
            self.logger.error(f"重新加载数据失败: {e}")
            messagebox.showerror("错误", f"重新加载数据失败: {e}")
            self.status_var.set("重新加载失败")
            
    def _show_statistics(self):
        """显示数据统计"""
        try:
            stats = self.data_manager.get_statistics()
            
            stats_text = f"数据统计信息:\n"
            stats_text += f"产品型号总数: {stats['total_product_types']}\n"
            stats_text += f"已加载文件数: {stats['loaded_files']}\n"
            stats_text += f"总记录数: {stats['total_records']}\n"
            
            messagebox.showinfo("数据统计", stats_text)
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            messagebox.showerror("错误", f"获取统计信息失败: {e}")
            
    def _show_settings(self):
        """显示设置对话框"""
        messagebox.showinfo("设置", "设置功能正在开发中...")
        
    def _show_calculator(self):
        """显示计算器"""
        messagebox.showinfo("计算器", "计算器功能正在开发中...")
        
    def _show_about(self):
        """显示关于信息"""
        about_text = f"""
DNC 参数计算系统

版本: {self.config_manager.get_setting('APPLICATION', 'version', '2.05')}
        
功能:
- 从CSV文件输入产品数据
- 自动计算几何参数
- 支持批量处理
- 数据验证和错误报告
- 结果导出
        
基于原始VB.NET项目DNC2.05重写
        """
        messagebox.showinfo("关于", about_text)
        
    def _exit_application(self):
        """退出应用程序"""
        if messagebox.askokcancel("退出", "确定要退出应用程序吗？"):
            self.root.quit()
            
    def _update_catalog_tab(self):
        """更新产品目录标签页"""
        # 清空当前显示
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
            
        # 添加所有产品
        product_types = self.data_manager.get_all_product_types()
        for product_type in product_types:
            product_data = self.data_manager.get_product_data(product_type)
            description = product_data.get('DESCRIPTION', '') if product_data else ''
            self.catalog_tree.insert('', tk.END, values=(product_type, description))
            
    def run(self):
        """运行应用程序"""
        try:
            # 配置界面样式
            self._configure_styles()
            
            # 加载配置
            if not self.config_manager.load_config():
                self.logger.warning("配置文件加载失败，使用默认配置")
            
            # 创建界面组件（这会初始化status_var等变量）
            self._create_widgets()
            self._setup_layout()
            
            # 加载数据
            self.status_var.set("正在加载数据...")
            if self.data_manager.load_csv_files():
                self._update_catalog_tab()
                self.status_var.set("数据加载完成")
            else:
                self.status_var.set("数据加载失败")
                messagebox.showerror("错误", "数据加载失败，请检查master目录")
                
            # 启动主循环
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"应用程序启动失败: {e}")
            messagebox.showerror("错误", f"应用程序启动失败: {e}")

    def _on_barcode_enter(self, event):
        """条码输入框回车事件处理，支持QR码格式：PO@型式@数量"""
        barcode_value = self.barcode_var.get().strip()
        if barcode_value:
            # 解析QR码，支持格式：PO@型式@数量
            qr_parts = barcode_value.split('@')
            if len(qr_parts) == 3:
                # QR码格式：PO@型式@数量
                po_number = qr_parts[0]
                model = qr_parts[1]
                quantity = qr_parts[2]
                
                self.status_var.set(f"PO: {po_number}, 型号: {model}, 数量: {quantity}")
                self._process_model(model, quantity)
            elif len(qr_parts) == 1:
                # 直接输入型号
                model = barcode_value.strip()
                self.status_var.set(f"型号: {model}")
                self._process_model(model)
            else:
                self.status_var.set(f"无法解析的条码格式: {barcode_value}")
                messagebox.showwarning("警告", f"无法解析的条码格式: {barcode_value}")

    def _process_model(self, original_model, quantity=None):
        """处理型号，通过从后往前逐字符删除进行匹配，生成对应的UI控件"""
        try:
            # 实现文档中描述的型号匹配方法：从后往前逐字符删除进行匹配
            matched_model = self._find_matching_model(original_model)
            if not matched_model:
                messagebox.showerror("错误", f"未找到匹配的型号: {original_model}")
                return

            # 更新型号显示
            self.TB_Model_var.set(matched_model)
            
            # 根据匹配到的产品数据加载相应的程序和UI控件
            self._load_program_for_model(matched_model)
            
            # 如果有数量信息，也进行处理
            if quantity:
                # 这里可以添加数量处理逻辑
                pass
                
        except Exception as e:
            self.logger.error(f"处理型号失败: {e}")
            messagebox.showerror("错误", f"处理型号失败: {e}")

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

                # 删除最后一个字符，继续搜索
                search_string = search_string[:-1]

            # 如果上面的搜索没有找到，尝试其他匹配方法
            # 检查是否是完全匹配
            for row in type_define_data:
                type_value = row.get('TYPE', '')
                if type_value and input_model == type_value:
                    self.logger.info(f"找到完全匹配型号: {type_value}")
                    return type_value

            return None

        except Exception as e:
            self.logger.error(f"型号匹配失败: {e}")
            return None

    def _load_program_for_model(self, model):
        """根据型号加载相应的程序和UI控件"""
        try:
            # 获取产品数据
            product_data = self.data_manager.get_product_data(model)
            if not product_data:
                return

            # 检查type_prg.csv来确定程序显示顺序
            type_prg_data = self.data_manager.get_table_by_name('type_prg.csv')
            prg_no = None
            
            # 在type_define.csv中查找产品对应的NO
            type_define_data = self.data_manager.get_table_by_name('type_define.csv')
            for row in type_define_data:
                if row.get('TYPE') == model:
                    prg_no = row.get('NO')
                    break

            if prg_no:
                # 查找type_prg.csv中对应的程序顺序
                for prg_row in type_prg_data:
                    if prg_row.get('NO') == prg_no:
                        # 根据type_prg.csv中的配置加载程序控件
                        # 按优先级尝试加载prg1, prg2, prg3等
                        for i in range(1, 4):  # 尝试prg1到prg3
                            prg_key = f'prg{i}'
                            prg_value = prg_row.get(prg_key)
                            if prg_value:
                                self._load_program_controls(prg_value, model)
                                break  # 只加载第一个找到的程序
                        break

            # 如果没有找到程序配置，尝试直接加载第一个可用程序
            if not prg_no:
                self._load_program_controls('1', model)

        except Exception as e:
            self.logger.error(f"加载程序失败: {e}")

    def _load_program_controls(self, prg_no, model):
        """加载指定程序的控件"""
        try:
            # 获取load.csv数据，这是定义UI控件的主要文件
            load_data = self.data_manager.get_program_table(prg_no, 'load')
            if not load_data:
                # 尝试使用默认文件名
                load_data = self.data_manager.get_table_by_name(f'prg{prg_no}/load.csv')
            if not load_data:
                # 尝试从主目录加载load.csv
                load_data = self.data_manager.get_table_by_name('load.csv')

            # 清除现有的控件（如果有的话）
            self._clear_program_controls()

            # 检查是否已存在程序标签页，如果存在则先删除
            if hasattr(self, 'program_tab') and self.program_tab:
                self.notebook.forget(self.program_tab)  # 从notebook中移除标签页
                self.program_tab = None

            # 创建一个新的标签页用于显示程序控件
            self.program_tab = ttk.Frame(self.notebook, padding="5")  # 减少内边距以获得更多空间
            self.notebook.add(self.program_tab, text=f"程序 {prg_no} 控件")
            
            # 为程序标签页配置布局权重
            self.program_tab.columnconfigure(0, weight=1)
            self.program_tab.rowconfigure(0, weight=1)

            # 创建主容器框架
            main_container = ttk.Frame(self.program_tab)
            main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
            main_container.columnconfigure(0, weight=1)
            main_container.rowconfigure(0, weight=1)

            # 创建Canvas和Scrollbar以支持滚动
            canvas = tk.Canvas(main_container, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            # 将滚动区域绑定到canvas
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            # 在canvas中创建窗口来包含滚动框架
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # 创建一个框架来放置程序控件
            self.program_frame = ttk.LabelFrame(scrollable_frame, text=f"型号: {model}", padding="8")
            self.program_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)

            # 如果有load数据，根据数据创建控件
            if load_data:
                for i, load_row in enumerate(load_data):
                    # 检查是否匹配当前型号
                    if load_row.get('TYPE') == model or load_row.get('NO') == model:
                        # 创建控件
                        self._create_controls_from_load_row(load_row, i)
                        break

            # 将canvas和滚动条放置到主容器中
            canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

            # 更新状态
            self.status_var.set(f"已加载程序 {prg_no} 的控件，型号: {model}")

            # 选择新的程序标签页
            self.notebook.select(self.program_tab)

        except Exception as e:
            self.logger.error(f"加载程序控件失败: {e}")

    def _create_controls_from_load_row(self, load_row, row_index):
        """根据load.csv行创建控件"""
        try:
            # 获取cntrl.csv来确定控件类型
            # 首先尝试获取当前程序的cntrl.csv数据
            # 遍历已加载的文件，寻找匹配的程序编号
            cntrl_data = []
            
            # 尝试获取当前程序的cntrl.csv数据
            for key, data in self.data_manager.loaded_files.items():
                if key.endswith('cntrl.csv'):  # 找到cntrl.csv文件
                    cntrl_data = data
                    break
            
            # 如果没找到程序特定的cntrl.csv，尝试主目录的cntrl.csv
            if not cntrl_data:
                cntrl_data = self.data_manager.loaded_files.get('cntrl.csv', [])
            if not cntrl_data:
                # 如果还是没找到，就从主目录加载
                cntrl_data = self.data_manager.get_table_by_name('cntrl.csv')

            # 创建控件容器
            controls_frame = ttk.Frame(self.program_frame)
            controls_frame.grid(row=row_index, column=0, sticky=(tk.W, tk.E), pady=5)

            # 创建一个主容器，用于显示控件
            main_container = ttk.Frame(controls_frame)
            main_container.pack(fill=tk.X, padx=5, pady=5)

            # 获取当前程序号 - 可能需要从当前型号信息获取
            program_no = "1"  # 默认程序号
            # 尝试获取当前程序号
            if hasattr(self, 'TB_Prg_var') and self.TB_Prg_var:
                try:
                    program_no = self.TB_Prg_var.get() or "1"
                except:
                    program_no = "1"  # 如果无法获取，使用默认值
            else:
                # 尝试从load_row的其他数据中推断程序号
                program_no = "1"  # 使用默认值

            # 获取relation.csv数据用于处理关系表达式
            relation_data = self.data_manager.get_program_table(program_no, 'relation')
            if not relation_data:
                relation_data = self.data_manager.get_table_by_name(f'prg{program_no}/relation.csv')
            if not relation_data:
                # 尝试从主目录加载relation.csv
                relation_data = self.data_manager.get_table_by_name('relation.csv')

            # 遍历load.csv中的列，创建对应的控件
            valid_controls = []  # 存储有效的控件
            
            for key, value in load_row.items():
                if key not in ['NO', 'TYPE', 'DRAWING', 'DISPFLG'] and key.startswith('#') and value:  # 只处理以#开头的宏变量
                    # 查找cntrl.csv中对应的控件类型
                    control_info = None
                    for cntrl_row in cntrl_data:
                        if cntrl_row.get('MACRO') == key:
                            control_info = cntrl_row
                            break

                    if control_info:
                        # 处理关系表达式（如果值以"relation"开头）
                        processed_value = self._process_relation_value(value, load_row, relation_data)
                        
                        # 创建控件
                        control_widget = self._create_control(control_info, processed_value, main_container)
                        if control_widget:
                            valid_controls.append(control_widget)

            # 将控件按6列布局排列（更宽的布局，显著减少行数）
            cols = 6  # 设置为6列，大幅减少行数，更好地利用水平空间
            for idx, control_widget in enumerate(valid_controls):
                row_num = idx // cols  # 计算当前行号
                col_num = idx % cols   # 计算当前列号
                
                # 将控件添加到网格
                control_widget.grid(row=row_num, column=col_num, padx=3, pady=2, sticky=(tk.W, tk.E))
                
                # 配置列权重，使其均匀分布
                main_container.columnconfigure(col_num, weight=1)

            # 配置滚动功能，以防控件过多
            # 为main_container添加滚动支持（如果需要）
            main_container.update_idletasks()  # 更新布局信息

        except Exception as e:
            self.logger.error(f"创建控件失败: {e}")

    def _create_control(self, control_info, default_value, parent_frame):
        """创建单个控件，应用新样式使更美观易读"""
        try:
            macro = control_info.get('MACRO', '')
            kind = control_info.get('KIND', '')
            dispflg = control_info.get('DISPFLG', '1')
            labeltxt = control_info.get('LABELTXT', macro) or macro  # 如果LABELTXT为空则使用macro
            sendflg = control_info.get('SEND', '1')  # 获取发送标志

            # 只显示DISPFLG为1的控件
            if dispflg != '1':
                return None

            # 创建控件框架
            ctrl_frame = ttk.Frame(parent_frame, padding="2")
            
            # 创建标签，使用更清晰的字体
            label = ttk.Label(ctrl_frame, text=labeltxt + ":", font=("Microsoft YaHei", 10, "bold"))
            label.pack(side=tk.TOP, padx=(0, 2), pady=(0, 2), anchor="w")

            # 根据类型创建不同的控件
            entry = None
            if kind in ['load', 'input', 'measure', 'select', 'relation', 'switch', 'correct']:
                # 创建文本框控件
                var = tk.StringVar(value=default_value)
                entry = ttk.Entry(ctrl_frame, textvariable=var, width=15, font=("Consolas", 10))
                entry.pack(side=tk.TOP, padx=(0, 2), pady=2)

                # 为不同类型的控件应用不同样式
                if kind == 'input':
                    entry.configure(style='Input.TEntry')  # 自定义样式
                elif kind == 'measure':
                    entry.configure(style='Measure.TEntry')  # 自定义样式
                elif kind == 'correct':
                    entry.configure(style='Correct.TEntry')  # 自定义样式

                # 保存控件引用，以便后续使用
                if not hasattr(self, 'control_vars'):
                    self.control_vars = {}
                self.control_vars[macro] = var

                # 如果SENDFLG为1，则标记为可发送
                if sendflg == '1':
                    # 添加视觉指示器（例如改变背景色或添加图标）
                    pass

            elif kind == 'changePRG':
                # 创建程序切换按钮
                btn_name = control_info.get('BTNNAME', '切换程序')
                change_prg = control_info.get('CHANGEPRG', '')
                entry = ttk.Button(ctrl_frame, text=btn_name, command=lambda p=change_prg: self._change_to_program(p), style='Action.TButton')
                entry.pack(side=tk.TOP, padx=(0, 2), pady=2)

            # 添加类型指示标签（可选，便于识别控件类型）
            type_label = ttk.Label(ctrl_frame, text=f"({kind})", font=("Microsoft YaHei", 8), foreground="gray")
            type_label.pack(side=tk.TOP, anchor="w")

            return ctrl_frame

        except Exception as e:
            self.logger.error(f"创建控件失败: {e}")
            return None

    def _clear_program_controls(self):
        """清除现有的程序控件"""
        if hasattr(self, 'program_frame') and self.program_frame:
            self.program_frame.destroy()

    def _change_to_program(self, program_name):
        """切换到指定程序"""
        self.status_var.set(f"切换到程序: {program_name}")
        # 这里可以实现程序切换逻辑
            
    def _show_keyboard(self):
        """显示虚拟键盘"""
        # TODO: 实现虚拟键盘功能
        messagebox.showinfo("键盘", "虚拟键盘功能待实现")
        
    def _send_data(self):
        """发送数据 - 根据cntrl.csv中的SENDFLG标记，将宏变量和值写入macro.txt文件"""
        try:
            # 获取当前型号
            current_model = self.TB_Model_var.get()
            if not current_model:
                messagebox.showwarning("警告", "请先选择一个型号")
                return

            # 获取当前程序号
            program_no = self.TB_Prg_var.get() or "1"  # 默认使用程序1
            
            # 获取load.csv数据 - 查找与当前型号匹配的行
            load_data = self.data_manager.get_program_table(program_no, 'load')
            if not load_data:
                load_data = self.data_manager.get_table_by_name(f'prg{program_no}/load.csv')
            if not load_data:
                load_data = self.data_manager.get_table_by_name('load.csv')
            
            if not load_data:
                messagebox.showerror("错误", "未找到load.csv数据")
                return

            # 查找与当前型号匹配的行
            load_row = None
            for row in load_data:
                if row.get('TYPE') == current_model or row.get('NO') == current_model:
                    load_row = row
                    break

            if not load_row:
                messagebox.showerror("错误", f"未找到型号 {current_model} 的数据")
                return

            # 获取cntrl.csv数据 - 获取控件定义和SEND标记
            cntrl_data = self.data_manager.get_program_table(program_no, 'cntrl')
            if not cntrl_data:
                cntrl_data = self.data_manager.get_table_by_name(f'prg{program_no}/cntrl.csv')
            if not cntrl_data:
                cntrl_data = self.data_manager.get_table_by_name('cntrl.csv')

            if not cntrl_data:
                messagebox.showerror("错误", "未找到cntrl.csv数据")
                return

            # 获取relation.csv数据用于处理关系表达式
            relation_data = self.data_manager.get_program_table(program_no, 'relation')
            if not relation_data:
                relation_data = self.data_manager.get_table_by_name(f'prg{program_no}/relation.csv')
            if not relation_data:
                relation_data = self.data_manager.get_table_by_name('relation.csv')

            # 收集需要发送的宏变量
            send_macros = []
            non_numeric_macros = []  # 记录非数值的宏变量

            for cntrl_row in cntrl_data:
                macro = cntrl_row.get('MACRO', '')
                send_flag = cntrl_row.get('SENDFLG', '0')
                
                # 检查是否需要发送（SENDFLG为1）
                if send_flag == '1' and macro:
                    if macro in load_row:
                        raw_value = load_row[macro]
                        
                        # 处理关系表达式（如果值以"relation"开头）
                        processed_value = self._process_relation_value(raw_value, load_row, relation_data)
                        
                        # 检查处理后的值是否为数值（允许整数和浮点数）
                        if self._is_numeric(processed_value):
                            send_macros.append((macro, processed_value))
                        else:
                            # 如果处理后的值不是数值，使用默认值0
                            # 这样可以确保尽可能多的宏变量被发送
                            self.logger.info(f"宏变量 {macro} 的值 '{processed_value}' 不是数值，使用默认值 0")
                            send_macros.append((macro, "0"))
                    else:
                        # 宏变量在load_row中不存在，使用默认值0
                        # 这样可以确保尽可能多的宏变量被发送
                        self.logger.info(f"宏变量 {macro} 在load数据中缺失，使用默认值 0")
                        send_macros.append((macro, "0"))  # 使用默认值0

            # 如果有非数值的宏变量，可以选择性地处理
            if non_numeric_macros:
                # 不再完全终止处理，而是记录问题并继续
                self.logger.warning(f"以下宏变量的值不是数值，将被跳过: {non_numeric_macros}")
                # 可以在错误消息中告知用户，但程序继续处理其他宏变量

            # 如果没有任何需要发送的宏变量
            if not send_macros:
                messagebox.showinfo("提示", "没有找到有效的可发送宏变量")
                return

            # 将宏变量写入macro.txt文件
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)  # 创建output目录（如果不存在）
            macro_file_path = output_dir / "macro.txt"
            
            with open(macro_file_path, 'w', encoding='utf-8') as f:
                for macro, value in send_macros:
                    # 去除宏变量名开头的"#"字符
                    clean_macro = macro.lstrip('#')
                    f.write(f"{clean_macro}={value}\n")

            messagebox.showinfo("成功", f"宏变量已成功写入 {macro_file_path}\n共发送 {len(send_macros)} 个宏变量")
            
        except Exception as e:
            self.logger.error(f"发送数据失败: {e}")
            messagebox.showerror("错误", f"发送数据失败: {e}")

    def _process_relation_value(self, value, load_row, relation_data):
        """处理关系表达式，返回计算后的数值"""
        if not value or not value.startswith("relation"):
            # 检查是否是宏变量（#开头）
            if value and value.startswith('#'):
                # 如果是宏变量，获取其值并进行define映射
                actual_value = load_row.get(value)
                if actual_value and str(actual_value).startswith('define'):
                    # 将 "define" 值映射到对应的参数编号
                    try:
                        param_num = int(value[1:])  # 去掉 '#' 获取数字部分
                        return param_num
                    except ValueError:
                        return actual_value  # 如果转换失败，返回原值
                else:
                    return actual_value
            # 不是关系表达式，直接返回原值
            return value

        if not relation_data:
            # 无法找到relation数据，返回原值
            return value

        # 查找对应的关系定义
        for relation_row in relation_data:
            if relation_row.get('DEFINE', '') == value:  # DEFINE列包含关系名称如relationLWJ
                # 找到关系定义，需要根据条件计算结果
                try:
                    # 简化处理，查找满足条件的结果
                    result = self._calculate_relation_result(relation_row, load_row)
                    if result is not None:
                        # 如果结果是宏变量（#开头），获取其值并进行define映射
                        if str(result).startswith('#'):
                            actual_value = load_row.get(result)
                            if actual_value and str(actual_value).startswith('define'):
                                # 将 "define" 值映射到对应的参数编号
                                try:
                                    param_num = int(result[1:])  # 去掉 '#' 获取数字部分
                                    result = param_num
                                except ValueError:
                                    result = actual_value  # 如果转换失败，使用原值
                            else:
                                result = actual_value
                        # 如果结果本身仍然是relation表达式，递归处理
                        elif str(result).startswith("relation"):
                            return self._process_relation_value(result, load_row, relation_data)
                        return result
                except Exception as e:
                    self.logger.warning(f"计算关系表达式 {value} 失败: {e}")
                    continue

        # 如果没有找到或计算失败，返回原值
        return value

    def _calculate_relation_result(self, relation_row, load_row):
        """根据关系定义和当前load数据计算关系表达式的结果"""
        relation_name = relation_row.get('DEFINE', '')
        result_value = relation_row.get('VALUE')  # VALUE列包含结果值

        if not relation_name or result_value is None:
            return result_value

        # 获取参数和条件信息
        # relation.csv的格式: DEFINE, VALUE, PARAM1, OPERATOR1, VALUE1, LOGIC, PARAM2, OPERATOR2, VALUE2, ...
        values_list = list(relation_row.values())
        if len(values_list) < 2:
            return result_value

        # 从第3个值开始是条件 (索引2及以后)
        condition_params = values_list[2:] if len(values_list) > 2 else []

        # 评估关系条件并返回计算结果
        result = self._evaluate_relation_conditions(relation_name, condition_params, load_row, result_value)
        return result

    def _evaluate_relation_conditions(self, relation_name, condition_params, load_row, default_result_value):
        """评估关系条件并返回结果值"""
        # 从relation.csv获取所有相关规则
        program_no = "1"  # 默认程序号
        if hasattr(self, 'TB_Prg_var') and self.TB_Prg_var:
            try:
                program_no = self.TB_Prg_var.get() or "1"
            except:
                program_no = "1"  # 如果无法获取，使用默认值
        else:
            program_no = "1"  # 如果属性不存在，使用默认值
            
        relation_data = self.data_manager.get_program_table(program_no, 'relation')
        if not relation_data:
            relation_data = self.data_manager.get_table_by_name(f'prg{program_no}/relation.csv')
        if not relation_data:
            relation_data = self.data_manager.get_table_by_name('relation.csv')

        if not relation_data:
            return default_result_value

        # 查找所有与当前关系名称匹配的规则
        matching_rules = []
        for row in relation_data:
            if row.get('DEFINE', '') == relation_name:
                matching_rules.append(row)

        # 特殊处理：对于某些relation类型，使用不同的规则选择逻辑
        if relation_name.startswith('relationHPN'):
            # 对于relationHPN，找到满足条件的规则中参数编号最大的那个（只考虑较小的参数编号，如#1-#99）
            best_result_value = None
            best_param_number = -1
            
            for rule in matching_rules:
                result_value = rule.get('VALUE')
                values_list = list(rule.values())
                if len(values_list) < 3:  # 至少需要DEFINE, VALUE, 和第一个条件参数
                    if len(values_list) >= 2:  # 如果只有DEFINE和VALUE，直接返回VALUE
                        return values_list[1]
                    continue

                # 条件从第3个元素开始 (索引2)
                condition_params = values_list[2:]
                
                try:
                    # 解析并评估条件
                    condition_met = self._check_relation_conditions(condition_params, load_row)
                    if condition_met:
                        # 检查结果值是否是参数编号（以#开头）
                        if str(result_value).startswith('#'):
                            try:
                                param_num = int(result_value[1:])
                                # 只考虑较小的参数编号（如#1-#99），避免#550这样的大编号影响结果
                                if param_num <= 99 and param_num > best_param_number:
                                    best_param_number = param_num
                                    best_result_value = result_value
                            except ValueError:
                                # 如果无法解析为数字，继续
                                continue
                        elif best_result_value is None:
                            # 如果当前结果不是#开头的参数，但还没有找到参数类型的返回值
                            best_result_value = result_value
                except Exception as e:
                    self.logger.warning(f"评估关系条件时出错: {e}")
                    continue
            
            if best_result_value is not None:
                return best_result_value
        else:
            # 对于其他relation类型，保持原有逻辑（返回第一个满足条件的规则）
            for rule in matching_rules:
                result_value = rule.get('VALUE')
                values_list = list(rule.values())
                if len(values_list) < 3:  # 至少需要DEFINE, VALUE, 和第一个条件参数
                    if len(values_list) >= 2:  # 如果只有DEFINE和VALUE，直接返回VALUE
                        return values_list[1]
                    continue

                # 条件从第3个元素开始 (索引2)
                condition_params = values_list[2:]
                
                try:
                    # 解析并评估条件
                    condition_met = self._check_relation_conditions(condition_params, load_row)
                    if condition_met:
                        return result_value  # 返回满足条件的结果值
                except Exception as e:
                    self.logger.warning(f"评估关系条件时出错: {e}")
                    continue

        # 如果没有规则满足，返回原始值或默认值
        return default_result_value

    def _check_relation_conditions(self, condition_params, load_row):
        """检查关系条件是否满足，支持 and/or 逻辑"""
        if not condition_params:
            return True  # 没有条件则认为满足

        # 解析条件: [param1, operator, value1, logic, param2, operator, value2, ...]
        # 或者 [logic, param1, operator, value1, logic, param2, operator, value2, ...]
        # 检查第一个元素是否为逻辑运算符
        i = 0
        # 如果第一个元素是逻辑运算符（and/or），则跳过它，从第二个元素开始解析条件
        if condition_params and condition_params[0] in ['and', 'or']:
            i = 1

        total_result = True
        first_condition = True

        while i < len(condition_params):
            if not condition_params[i]:  # 跳过空值
                i += 1
                continue

            # 获取参数、操作符和比较值
            param_name = condition_params[i]
            if i + 1 >= len(condition_params):
                break
            operation = condition_params[i + 1]
            if i + 2 >= len(condition_params):
                break
            param_value = condition_params[i + 2]

            if param_name and param_name.startswith('#') and param_value:
                # 从load_row获取实际参数值
                actual_param_value = load_row.get(param_name)
                
                # 处理 "define" 值的映射
                if actual_param_value and str(actual_param_value).startswith('define'):
                    # 将 "define" 值映射到对应的参数编号
                    # 例如: '#1' -> 'defineH' -> 1, '#8' -> 'defineNK' -> 8
                    try:
                        param_num = int(param_name[1:])  # 去掉 '#' 获取数字部分
                        actual = param_num
                    except ValueError:
                        actual = 0  # 如果转换失败，使用0
                elif actual_param_value and self._is_numeric(actual_param_value):
                    actual = float(actual_param_value)
                else:
                    actual = 0  # 非数值默认为0

                if self._is_numeric(param_value):
                    expected = float(param_value)

                    # 执行比较
                    condition_result = False
                    if operation == '<':
                        condition_result = actual < expected
                    elif operation == '<=':
                        condition_result = actual <= expected
                    elif operation == '>':
                        condition_result = actual > expected
                    elif operation == '>=':
                        condition_result = actual >= expected
                    elif operation in ['=', '==', '===']:
                        condition_result = actual == expected
                    elif operation == '!=':
                        condition_result = actual != expected
                    else:
                        # 未知操作符，条件不满足
                        condition_result = False
                else:
                    condition_result = False
            else:
                condition_result = False

            # 如果这是第一个条件，设置总结果，否则根据逻辑运算符合并
            if first_condition:
                total_result = condition_result
                first_condition = False
            else:
                # 检查前一个逻辑运算符 (在当前条件之前的元素)
                logic_op = condition_params[i - 1] if i > 0 else 'and'
                if logic_op == 'and':
                    total_result = total_result and condition_result
                elif logic_op == 'or':
                    total_result = total_result or condition_result

            # 移动到下一个条件组（通常是3个元素：参数、操作符、值 + 1个可选的逻辑运算符）
            if i + 3 < len(condition_params) and condition_params[i + 3] in ['and', 'or']:
                # 有逻辑运算符，跳过4个元素（参数、操作符、值、逻辑运算符）
                i += 4
            else:
                # 没有逻辑运算符，跳过3个元素（参数、操作符、值）
                i += 3

        return total_result

    def _is_numeric(self, value):
        """检查值是否为数值（整数或浮点数）"""
        if value is None:
            return False
        try:
            float(str(value).strip())
            return True
        except ValueError:
            return False
        
    def _change_operator(self):
        """更改操作员"""
        # TODO: 实现操作员更改功能
        messagebox.showinfo("操作员", "操作员更改功能待实现")
        
    def _change_program(self):
        """切换程序"""
        # TODO: 实现程序切换功能
        messagebox.showinfo("程序切换", "程序切换功能待实现")
