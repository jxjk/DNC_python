import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from ..data.models import Product, GeometryParameters, CalculationResult

class CalculationEngine:
    """计算引擎，负责执行各种几何计算和参数计算"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.precision = 4  # 计算精度
        
    def calculate_geometry(self, product: Product, input_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """计算产品几何参数"""
        try:
            # 获取产品参数
            product_params = product.parameters
            geometry_params = GeometryParameters()
            
            # 解析基本几何参数
            self._parse_basic_parameters(product_params, geometry_params)
            
            # 执行几何计算
            self._perform_geometry_calculations(geometry_params)
            
            # 应用输入参数（如果有）
            if input_params:
                self._apply_input_parameters(input_params, geometry_params)
                
            # 转换为字典格式
            result = geometry_params.to_dict()
            
            self.logger.info(f"几何计算完成: {product.product_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"几何计算失败 {product.product_type}: {e}")
            return {}
            
    def _parse_basic_parameters(self, product_params: Dict[str, Any], geometry: GeometryParameters):
        """解析基本几何参数"""
        try:
            # 从产品参数中提取几何信息
            # 这里需要根据实际的CSV数据结构来解析
            geometry.length = self._safe_float(product_params.get('LENGTH'))
            geometry.width = self._safe_float(product_params.get('WIDTH'))
            geometry.height = self._safe_float(product_params.get('HEIGHT'))
            geometry.diameter = self._safe_float(product_params.get('DIAMETER'))
            geometry.radius = self._safe_float(product_params.get('RADIUS'))
            geometry.angle = self._safe_float(product_params.get('ANGLE'))
            
        except Exception as e:
            self.logger.warning(f"解析基本参数失败: {e}")
            
    def _perform_geometry_calculations(self, geometry: GeometryParameters):
        """执行几何计算"""
        try:
            # 体积计算
            if geometry.length and geometry.width and geometry.height:
                geometry.volume = self._round(geometry.length * geometry.width * geometry.height)
                
            # 表面积计算
            if geometry.length and geometry.width and geometry.height:
                geometry.surface_area = self._round(
                    2 * (geometry.length * geometry.width + 
                         geometry.length * geometry.height + 
                         geometry.width * geometry.height)
                )
                
            # 圆柱体体积
            if geometry.diameter and geometry.height:
                radius = geometry.diameter / 2
                geometry.volume = self._round(math.pi * radius ** 2 * geometry.height)
                
            # 球体体积
            if geometry.radius:
                geometry.volume = self._round((4/3) * math.pi * geometry.radius ** 3)
                geometry.surface_area = self._round(4 * math.pi * geometry.radius ** 2)
                
            # 重量计算（假设密度为1）
            if geometry.volume:
                geometry.weight = self._round(geometry.volume * 1)  # 密度为1 g/cm³
                
        except Exception as e:
            self.logger.warning(f"几何计算失败: {e}")
            
    def _apply_input_parameters(self, input_params: Dict[str, Any], geometry: GeometryParameters):
        """应用输入参数"""
        try:
            # 根据输入参数更新几何参数
            if 'length' in input_params:
                geometry.length = self._safe_float(input_params['length'])
            if 'width' in input_params:
                geometry.width = self._safe_float(input_params['width'])
            if 'height' in input_params:
                geometry.height = self._safe_float(input_params['height'])
            if 'diameter' in input_params:
                geometry.diameter = self._safe_float(input_params['diameter'])
            if 'radius' in input_params:
                geometry.radius = self._safe_float(input_params['radius'])
            if 'angle' in input_params:
                geometry.angle = self._safe_float(input_params['angle'])
                
            # 重新计算
            self._perform_geometry_calculations(geometry)
            
        except Exception as e:
            self.logger.warning(f"应用输入参数失败: {e}")
            
    def calculate_batch(self, products: List[Product], input_params_list: List[Dict[str, Any]] = None) -> List[CalculationResult]:
        """批量计算"""
        results = []
        
        for i, product in enumerate(products):
            input_params = input_params_list[i] if input_params_list and i < len(input_params_list) else None
            
            try:
                calculated_params = self.calculate_geometry(product, input_params)
                
                result = CalculationResult(
                    product_type=product.product_type,
                    input_parameters=input_params or {},
                    calculated_parameters=calculated_params,
                    success=True
                )
                
            except Exception as e:
                result = CalculationResult(
                    product_type=product.product_type,
                    input_parameters=input_params or {},
                    calculated_parameters={},
                    success=False,
                    error_message=str(e)
                )
                
            results.append(result)
            
        self.logger.info(f"批量计算完成: {len(products)} 个产品")
        return results
        
    def validate_calculation(self, product_type: str, calculated_params: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证计算结果"""
        errors = []
        
        try:
            # 检查必需参数
            required_params = ['volume', 'surface_area']
            for param in required_params:
                if param in calculated_params and calculated_params[param] is not None:
                    value = calculated_params[param]
                    if value <= 0:
                        errors.append(f"参数 {param} 必须为正数")
                        
            # 检查参数一致性
            if 'volume' in calculated_params and 'surface_area' in calculated_params:
                volume = calculated_params['volume']
                surface_area = calculated_params['surface_area']
                if volume and surface_area and surface_area < volume:
                    errors.append("表面积不能小于体积")
                    
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            return False, [f"验证失败: {e}"]
            
    def calculate_dimension_tolerance(self, nominal_value: float, tolerance: str) -> Tuple[float, float]:
        """计算尺寸公差"""
        try:
            # 解析公差字符串，例如 "±0.1", "+0.1/-0.2"
            if tolerance.startswith('±'):
                tolerance_value = float(tolerance[1:])
                upper_limit = nominal_value + tolerance_value
                lower_limit = nominal_value - tolerance_value
            elif '/' in tolerance:
                upper_tolerance, lower_tolerance = tolerance.split('/')
                upper_limit = nominal_value + float(upper_tolerance.replace('+', ''))
                lower_limit = nominal_value + float(lower_tolerance.replace('-', ''))
            else:
                upper_limit = lower_limit = nominal_value
                
            return self._round(upper_limit), self._round(lower_limit)
            
        except Exception as e:
            self.logger.error(f"计算尺寸公差失败: {e}")
            return nominal_value, nominal_value
            
    def calculate_material_volume(self, geometry_params: Dict[str, Any], material_density: float = 1.0) -> float:
        """计算材料体积"""
        try:
            volume = geometry_params.get('volume', 0)
            return self._round(volume * material_density)
        except Exception as e:
            self.logger.error(f"计算材料体积失败: {e}")
            return 0.0
            
    def calculate_weight(self, volume: float, density: float) -> float:
        """计算重量"""
        try:
            return self._round(volume * density)
        except Exception as e:
            self.logger.error(f"计算重量失败: {e}")
            return 0.0
            
    def calculate_surface_area_ratio(self, surface_area: float, volume: float) -> float:
        """计算表面积体积比"""
        try:
            if volume > 0:
                return self._round(surface_area / volume)
            return 0.0
        except Exception as e:
            self.logger.error(f"计算表面积体积比失败: {e}")
            return 0.0
            
    def _safe_float(self, value: Any) -> Optional[float]:
        """安全转换为浮点数"""
        try:
            if value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
            
    def _round(self, value: float) -> float:
        """四舍五入到指定精度"""
        try:
            return round(value, self.precision)
        except (ValueError, TypeError):
            return value
            
    def set_precision(self, precision: int):
        """设置计算精度"""
        self.precision = precision
        
    def get_calculation_formulas(self) -> Dict[str, str]:
        """获取计算公式"""
        return {
            'volume_rectangular': 'length * width * height',
            'surface_area_rectangular': '2 * (length * width + length * height + width * height)',
            'volume_cylinder': 'π * (diameter/2)² * height',
            'surface_area_cylinder': '2 * π * (diameter/2) * height + 2 * π * (diameter/2)²',
            'volume_sphere': '(4/3) * π * radius³',
            'surface_area_sphere': '4 * π * radius²',
            'weight': 'volume * density'
        }
