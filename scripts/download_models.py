from model_manager import ModelManager
import sys

def main():
    model_manager = ModelManager()
    
    # 验证现有模型
    missing_models = model_manager.verify_models()
    if not missing_models:
        print("All models are already downloaded and verified.")
        sys.exit(0)
        
    print(f"Missing models: {', '.join(missing_models)}")
    
    # 下载缺失的模型
    print("Starting model download...")
    model_manager.download_models()
    
    # 清理临时文件
    model_manager.cleanup_temp_files()
    
    # 最终验证
    missing_models = model_manager.verify_models()
    if missing_models:
        print(f"Error: Some models are still missing: {', '.join(missing_models)}")
        sys.exit(1)
    else:
        print("All models successfully downloaded and verified.")

if __name__ == "__main__":
    main()
