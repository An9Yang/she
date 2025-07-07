"""配置模块测试"""
import pytest
import os
from unittest.mock import patch

from backend.core.config import Settings, settings


class TestConfig:
    """配置测试类"""
    
    @pytest.mark.unit
    def test_settings_instance(self):
        """测试设置实例"""
        assert settings is not None
        assert isinstance(settings, Settings)
    
    @pytest.mark.unit
    def test_default_settings(self):
        """测试默认设置"""
        test_settings = Settings()
        
        # 测试默认值
        assert test_settings.APP_NAME == "Second Self"
        assert test_settings.VERSION == "0.1.0"
        assert test_settings.DATABASE_NAME == "secondself"
        assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert test_settings.ALGORITHM == "HS256"
    
    @pytest.mark.unit
    def test_environment_variables(self, mock_env_vars):
        """测试环境变量加载"""
        # 创建新的设置实例以测试环境变量
        test_settings = Settings()
        
        assert test_settings.SECRET_KEY == mock_env_vars["SECRET_KEY"]
        assert test_settings.DATABASE_URL == mock_env_vars["DATABASE_URL"]
        assert test_settings.AZURE_OPENAI_API_KEY == mock_env_vars["AZURE_OPENAI_API_KEY"]
        assert test_settings.AZURE_OPENAI_ENDPOINT == mock_env_vars["AZURE_OPENAI_ENDPOINT"]
    
    @pytest.mark.unit
    def test_cors_origins(self):
        """测试CORS来源配置"""
        test_settings = Settings()
        
        assert isinstance(test_settings.CORS_ORIGINS, list)
        assert "http://localhost:3000" in test_settings.CORS_ORIGINS
        assert "http://localhost:3001" in test_settings.CORS_ORIGINS
    
    @pytest.mark.unit
    def test_file_upload_settings(self):
        """测试文件上传设置"""
        test_settings = Settings()
        
        assert test_settings.MAX_UPLOAD_SIZE == 10 * 1024 * 1024  # 10MB
        assert isinstance(test_settings.ALLOWED_EXTENSIONS, set)
        assert ".txt" in test_settings.ALLOWED_EXTENSIONS
        assert ".json" in test_settings.ALLOWED_EXTENSIONS
        assert ".csv" in test_settings.ALLOWED_EXTENSIONS
    
    @pytest.mark.unit
    def test_settings_validation(self):
        """测试设置验证"""
        # 测试缺少必需的环境变量
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):
                # 某些必需的环境变量可能会导致验证失败
                Settings()
    
    @pytest.mark.unit
    def test_mongodb_uri_format(self):
        """测试MongoDB URI格式"""
        test_settings = Settings()
        
        assert test_settings.DATABASE_URL.startswith("mongodb://") or \
               test_settings.DATABASE_URL.startswith("mongodb+srv://")
    
    @pytest.mark.unit
    def test_azure_openai_settings(self):
        """测试Azure OpenAI设置"""
        test_settings = Settings()
        
        assert hasattr(test_settings, 'AZURE_OPENAI_API_KEY')
        assert hasattr(test_settings, 'AZURE_OPENAI_ENDPOINT')
        assert hasattr(test_settings, 'AZURE_OPENAI_DEPLOYMENT')
        assert hasattr(test_settings, 'AZURE_OPENAI_API_VERSION')
        
        # 验证API版本格式
        assert test_settings.AZURE_OPENAI_API_VERSION.count('-') == 2
    
    @pytest.mark.unit
    def test_settings_immutability(self):
        """测试设置不可变性"""
        original_value = settings.APP_NAME
        
        # 尝试修改设置
        with pytest.raises(Exception):
            settings.APP_NAME = "New Name"
        
        # 验证值未改变
        assert settings.APP_NAME == original_value
    
    @pytest.mark.unit
    def test_env_file_loading(self, tmp_path):
        """测试.env文件加载"""
        # 创建临时.env文件
        env_file = tmp_path / ".env"
        env_file.write_text("""
SECRET_KEY=test-secret-from-file
DATABASE_URL=mongodb://test-from-file:27017
AZURE_OPENAI_API_KEY=test-key-from-file
""")
        
        # 使用临时.env文件路径
        with patch.dict(os.environ, {"ENV_FILE": str(env_file)}):
            test_settings = Settings(_env_file=str(env_file))
            
            assert test_settings.SECRET_KEY == "test-secret-from-file"
            assert test_settings.DATABASE_URL == "mongodb://test-from-file:27017"
    
    @pytest.mark.unit
    def test_production_settings(self):
        """测试生产环境设置"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            test_settings = Settings()
            
            # 在生产环境中应该有更严格的设置
            assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 60
            assert len(test_settings.SECRET_KEY) >= 32  # 足够长的密钥