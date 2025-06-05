import os
import json
import logging

class Config:
    """配置管理类，用于保存和加载应用配置"""
    
    def __init__(self, config_file='app_config.json'):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件名，默认为app_config.json
        """
        # 获取应用根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # 配置文件路径
        self.config_path = os.path.join(self.base_dir, config_file)
        # 默认配置
        self.default_config = {
            'swapface': {
                'char': '',
                'input_path': '',
                'output_path': '',
                'copy_on_error': True
            }
        }
        # 当前配置
        self.config = self.load_config()
        
    def load_config(self):
        """
        加载配置文件，如果不存在则创建默认配置
        
        Returns:
            dict: 加载的配置
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保包含所有默认配置项
                    for section, values in self.default_config.items():
                        if section not in config:
                            config[section] = {}
                        for key, value in values.items():
                            if key not in config[section]:
                                config[section][key] = value
                    return config
            else:
                # 如果配置文件不存在，则创建默认配置
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置，如果为None则保存当前配置
        """
        try:
            if config is None:
                config = self.config
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
    
    def get(self, section, key, default=None):
        """
        获取配置项
        
        Args:
            section: 配置节
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except:
            return default
    
    def set(self, section, key, value):
        """
        设置配置项
        
        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
    
    def set_section(self, section, values):
        """
        设置整个配置节
        
        Args:
            section: 配置节名
            values: 配置节值字典
        """
        self.config[section] = values
        self.save_config()
    
    def get_section(self, section):
        """
        获取整个配置节
        
        Args:
            section: 配置节名
            
        Returns:
            dict: 配置节字典
        """
        return self.config.get(section, {})

# 创建全局配置实例
config = Config()
