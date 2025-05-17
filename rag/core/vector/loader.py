import importlib
import pkgutil
import logging
from pathlib import Path
from typing import Dict
from core.vector.plugins.interface import FileAnalyzerPlugin
from langchain_core.embeddings import Embeddings
from dao.sqlite.document import Document

logger = logging.getLogger(__name__)

class PluginManager:
    
    def __init__(self):
        self.plugin_dict: Dict[str, FileAnalyzerPlugin] = {}
        
    def _get_plugin(self, plugin_name: str, embeddings: Embeddings) -> FileAnalyzerPlugin:
        """安全加载插件并处理依赖"""
        plugin_dir = Path(__file__).parent / "plugins"
        
        # 确保是有效Python包
        if not (plugin_dir / "__init__.py").exists():
            (plugin_dir / "__init__.py").touch(exist_ok=True)
        
        try:
            module = importlib.import_module(
                f"{__package__}.plugins.{plugin_name}"  # 动态获取当前包名
            )
            logger.debug(f"成功导入插件模块: {plugin_name}")
        except Exception as e:
            logger.error(f"导入插件模块 {plugin_name} 失败: {str(e)}")
            raise ModuleNotFoundError(f"导入插件模块 {plugin_name} 失败")

        # 扫描有效插件类
        for cls in self._find_plugin_classes(module):
            try:
                if issubclass(cls, FileAnalyzerPlugin):
                    self.plugin_dict[plugin_name] = cls(embeddings)
                    break
            except Exception as e:
                logger.error(f"初始化插件 {cls.__name__} 失败: {str(e)}")
                raise Exception(f"初始化插件 {cls.__name__} 失败")
        
        return self.plugin_dict[plugin_name]

    def _find_plugin_classes(self, module) -> list:
        """查找模块中有效的插件类"""
        return [
            obj for _, obj in vars(module).items()
            if self._is_valid_plugin_class(obj)
        ]

    def _is_valid_plugin_class(self, obj) -> bool:
        """验证是否为有效插件类"""
        return (
            isinstance(obj, type) and
            issubclass(obj, FileAnalyzerPlugin) and
            obj is not FileAnalyzerPlugin
        )

    def _validate_formats(self, plugin: FileAnalyzerPlugin) -> list:
        """验证插件返回的格式有效性"""
        formats = plugin.supported_formats()
        if not formats:
            logger.warning(f"插件 {type(plugin).__name__} 未声明支持格式")
        return [fmt.lower() for fmt in formats]

    def get_plugin(self, doc: Document, embeddings: Embeddings) -> FileAnalyzerPlugin:
        file_format = Path(doc.doc_name).suffix.replace(".", "")
        if self.plugin_dict.get(file_format):
            return self.plugin_dict[file_format]
        return self._get_plugin(file_format, embeddings)
    
    @property
    def supported_formats(self) -> list:
        """获取所有支持格式"""
        return list(self.plugin_dict.keys())