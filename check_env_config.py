#!/usr/bin/env python3
"""
安全检查环境配置（不显示敏感信息）
"""
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "backend"))

def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """掩码敏感信息"""
    if not value:
        return "NOT_SET"
    if len(value) <= visible_chars:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars)

def check_mongodb_config():
    """检查MongoDB配置"""
    print("\n=== MongoDB配置检查 ===")
    
    # 检查环境变量
    mongodb_url = os.getenv("MONGODB_URL", "")
    
    if not mongodb_url:
        print("❌ MONGODB_URL 未设置")
        return False
    
    # 解析连接字符串
    if "mongodb+srv://" in mongodb_url:
        print("✅ 使用MongoDB Atlas (mongodb+srv://)")
        # 提取主机信息
        try:
            host_part = mongodb_url.split("@")[1].split("/")[0]
            print(f"   主机: {host_part}")
        except:
            print("   主机: [解析失败]")
    elif "localhost" in mongodb_url or "127.0.0.1" in mongodb_url:
        print("⚠️  使用本地MongoDB (localhost)")
    else:
        print("✅ 使用远程MongoDB")
    
    # 测试连接
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        print("\n测试MongoDB连接...")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ MongoDB连接成功！")
        
        # 列出数据库
        dbs = client.list_database_names()
        print(f"   可用数据库: {dbs}")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError:
        print("❌ MongoDB连接超时")
        return False
    except Exception as e:
        print(f"❌ MongoDB连接失败: {type(e).__name__}")
        return False

def check_azure_openai_config():
    """检查Azure OpenAI配置"""
    print("\n=== Azure OpenAI配置检查 ===")
    
    use_azure = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
    use_mock = os.getenv("USE_MOCK_EMBEDDINGS", "true").lower() == "true"
    
    print(f"USE_AZURE_OPENAI: {use_azure}")
    print(f"USE_MOCK_EMBEDDINGS: {use_mock}")
    
    if not use_azure:
        print("⚠️  未启用Azure OpenAI")
        return False
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    key = os.getenv("AZURE_OPENAI_KEY", "")
    chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
    
    print(f"\nEndpoint: {mask_sensitive(endpoint, 20) if endpoint else 'NOT_SET'}")
    print(f"API Key: {mask_sensitive(key, 8) if key else 'NOT_SET'}")
    print(f"Chat Deployment: {chat_deployment or 'NOT_SET'}")
    print(f"Embedding Deployment: {embedding_deployment or 'NOT_SET'}")
    
    all_set = all([endpoint, key, chat_deployment, embedding_deployment])
    
    if all_set:
        print("\n✅ 所有Azure OpenAI配置已设置")
    else:
        print("\n❌ Azure OpenAI配置不完整")
    
    return all_set

def check_env_file():
    """检查.env文件"""
    print("\n=== 环境文件检查 ===")
    
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if env_path.exists():
        print("✅ .env 文件存在")
        print(f"   大小: {env_path.stat().st_size} bytes")
        
        # 统计配置数量
        with open(env_path, 'r') as f:
            lines = f.readlines()
            config_lines = [l for l in lines if l.strip() and not l.strip().startswith('#') and '=' in l]
            print(f"   配置项数量: {len(config_lines)}")
    else:
        print("❌ .env 文件不存在")
        
        if env_example_path.exists():
            print("   提示: 请复制 .env.example 为 .env 并填写配置")
    
    return env_path.exists()

def main():
    """主函数"""
    print("Second Self 环境配置检查工具")
    print("=" * 50)
    
    # 检查环境文件
    env_exists = check_env_file()
    
    if not env_exists:
        print("\n请先创建 .env 文件！")
        return
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 检查各项配置
    mongodb_ok = check_mongodb_config()
    azure_ok = check_azure_openai_config()
    
    # 总结
    print("\n" + "=" * 50)
    print("配置检查总结:")
    print(f"- MongoDB: {'✅ 正常' if mongodb_ok else '❌ 需要修复'}")
    print(f"- Azure OpenAI: {'✅ 正常' if azure_ok else '❌ 需要修复'}")
    
    if not mongodb_ok:
        print("\nMongoDB修复建议:")
        print("1. 确保已在MongoDB Atlas创建集群")
        print("2. 获取连接字符串 (mongodb+srv://...)")
        print("3. 在.env中设置 MONGODB_URL")
    
    if not azure_ok:
        print("\nAzure OpenAI修复建议:")
        print("1. 在Azure Portal创建OpenAI资源")
        print("2. 部署chat和embedding模型")
        print("3. 在.env中设置所有Azure配置")
        print("4. 设置 USE_MOCK_EMBEDDINGS=false")

if __name__ == "__main__":
    main()