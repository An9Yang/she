#!/usr/bin/env python3
"""
Second Self 环境配置向导
帮助用户创建和配置.env文件
"""
import os
import sys
from pathlib import Path
import shutil

def create_env_file():
    """创建.env文件"""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if env_path.exists():
        print("⚠️  .env 文件已存在")
        response = input("是否要覆盖现有配置？(y/N): ").lower()
        if response != 'y':
            return False
    
    # 复制模板文件
    if env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("✅ 已创建 .env 文件")
        return True
    else:
        print("❌ 找不到 .env.example 模板文件")
        return False

def update_env_value(key: str, value: str):
    """更新.env文件中的值"""
    env_path = Path(__file__).parent / ".env"
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    if not updated:
        # 添加新配置
        lines.append(f"\n{key}={value}\n")
    
    with open(env_path, 'w') as f:
        f.writelines(lines)

def setup_mongodb():
    """配置MongoDB"""
    print("\n=== MongoDB Atlas 配置 ===")
    print("请在MongoDB Atlas创建集群并获取连接字符串")
    print("格式: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority")
    
    mongodb_url = input("\n请输入MongoDB Atlas连接字符串: ").strip()
    
    if mongodb_url:
        update_env_value("MONGODB_URL", mongodb_url)
        print("✅ MongoDB配置已保存")
        return True
    else:
        print("⚠️  跳过MongoDB配置")
        return False

def setup_azure_openai():
    """配置Azure OpenAI"""
    print("\n=== Azure OpenAI 配置 ===")
    print("需要在Azure Portal创建OpenAI资源")
    
    use_azure = input("\n是否使用Azure OpenAI？(Y/n): ").lower() != 'n'
    
    if use_azure:
        update_env_value("USE_AZURE_OPENAI", "true")
        
        endpoint = input("Azure OpenAI Endpoint (如 https://your-resource.openai.azure.com/): ").strip()
        api_key = input("Azure OpenAI API Key: ").strip()
        
        if endpoint and api_key:
            update_env_value("AZURE_OPENAI_ENDPOINT", endpoint)
            update_env_value("AZURE_OPENAI_KEY", api_key)
            
            # 部署名称
            print("\n请输入部署名称（如果不确定，可以使用默认值）")
            chat_deployment = input("Chat模型部署名 [o3]: ").strip() or "o3"
            embedding_deployment = input("Embedding模型部署名 [text-embedding-ada-002]: ").strip() or "text-embedding-ada-002"
            
            update_env_value("AZURE_OPENAI_CHAT_DEPLOYMENT", chat_deployment)
            update_env_value("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", embedding_deployment)
            
            # 禁用mock embeddings
            use_mock = input("\n是否使用Mock Embeddings（仅用于测试）？(y/N): ").lower() == 'y'
            update_env_value("USE_MOCK_EMBEDDINGS", "true" if use_mock else "false")
            
            print("✅ Azure OpenAI配置已保存")
            return True
    
    print("⚠️  将使用Mock实现")
    update_env_value("USE_AZURE_OPENAI", "false")
    update_env_value("USE_MOCK_EMBEDDINGS", "true")
    return False

def setup_secret_key():
    """配置密钥"""
    print("\n=== 安全密钥配置 ===")
    
    import secrets
    secret_key = secrets.token_urlsafe(32)
    update_env_value("SECRET_KEY", secret_key)
    print("✅ 已生成安全密钥")

def main():
    """主函数"""
    print("🚀 Second Self 环境配置向导")
    print("=" * 50)
    
    # 创建.env文件
    if not create_env_file():
        return
    
    # 配置各项服务
    setup_secret_key()
    mongodb_ok = setup_mongodb()
    azure_ok = setup_azure_openai()
    
    # 总结
    print("\n" + "=" * 50)
    print("✅ 配置完成！")
    print(f"- MongoDB Atlas: {'已配置' if mongodb_ok else '未配置'}")
    print(f"- Azure OpenAI: {'已配置' if azure_ok else '使用Mock'}")
    
    print("\n下一步:")
    print("1. 运行 python check_env_config.py 验证配置")
    print("2. 运行 ./start_services.sh 启动服务")
    print("3. 运行 python test_api_endpoints.py 测试API")

if __name__ == "__main__":
    main()