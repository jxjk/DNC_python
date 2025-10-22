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
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("DNC 参数计算系统")
        self.root.geometry("1200x800")
        
        # 状态变量
        self.current_data = []
        self.error_messages = []
        
        # 创建界面
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建顶部控制区域
        self._create_control_area()
        
        # 创建数据显示区域
        self._create_data_display_area()
        
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
        """创建控制区域"""
        control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 输入文件选择
        ttk.Label(control_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W)
        self.input_file_var = tk.StringVar()
        self.input_file_entry = ttk.Entry(control_frame, textvariable=self.input_file_var, width=50)
        self.input_file_entry.grid(row=0, column=1, padx=(5, 5), sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="浏览...", command=self._browse_input_file).grid(row=0, column=2, padx=(0, 10))
        
        # 处理按钮
        ttk.Button(control_frame, text="处理输入文件", command=self._process_input_file).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(control_frame, text="清空结果", command=self._clear_results).grid(row=0, column=4)
        
        # 搜索框
        ttk.Label(control_frame, text="搜索产品:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=1, column=1, padx=(5, 5), pady=(10, 0), sticky=(tk.W, tk.E))
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        ttk.Button(control_frame, text="搜索", command=self._search_products).grid(row=1, column=2, pady=(10, 0))
        
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
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def _setup_layout(self):
        """设置布局"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
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
            # 加载配置
            if not self.config_manager.load_config():
                self.logger.warning("配置文件加载失败，使用默认配置")
                
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
