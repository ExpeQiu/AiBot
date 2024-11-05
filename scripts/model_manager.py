import os
import requests
import bz2
import shutil
import hashlib
from tqdm import tqdm
from config.model_config import MODEL_CONFIG, MODEL_DIRS
from modules.utils.logger import Logger

class ModelManager:
    def __init__(self):
        self.logger = Logger.get_logger("ModelManager")
        self._create_model_dirs()
        
    def _create_model_dirs(self):
        """创建模型目录"""
        for dir_path in MODEL_DIRS:
            os.makedirs(dir_path, exist_ok=True)
            
    def _download_file(self, url, dest_path, desc=None):
        """下载文件并显示进度条"""
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(dest_path, 'wb') as file, tqdm(
                desc=desc,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    pbar.update(size)
                    
            return True
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
            return False
            
    def _extract_bz2(self, source_path, dest_path):
        """解压bz2文件"""
        try:
            with bz2.BZ2File(source_path) as source, open(dest_path, 'wb') as dest:
                shutil.copyfileobj(source, dest)
            os.remove(source_path)  # 删除压缩文件
            return True
        except Exception as e:
            self.logger.error(f"Error extracting {source_path}: {str(e)}")
            return False
            
    def download_models(self):
        """下载所有必需的模型"""
        for category, models in MODEL_CONFIG.items():
            self.logger.info(f"Processing {category} models...")
            
            for model_name, model_info in models.items():
                dest_path = model_info['path']
                
                # 检查模型是否已存在
                if os.path.exists(dest_path):
                    self.logger.info(f"Model {model_name} already exists")
                    continue
                    
                # 下载模型
                temp_path = dest_path + '.downloading'
                success = self._download_file(
                    model_info['url'],
                    temp_path,
                    f"Downloading {model_name}"
                )
                
                if not success:
                    continue
                    
                # 处理bz2压缩文件
                if model_info['url'].endswith('.bz2'):
                    success = self._extract_bz2(temp_path, dest_path)
                else:
                    os.rename(temp_path, dest_path)
                    
                if success:
                    self.logger.info(f"Successfully downloaded {model_name}")
                    
    def verify_models(self):
        """验证所有模型文件是否存在且完整"""
        missing_models = []
        
        for category, models in MODEL_CONFIG.items():
            for model_name, model_info in models.items():
                if not os.path.exists(model_info['path']):
                    missing_models.append(model_name)
                    
        return missing_models
        
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_dir = 'models/temp'
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                self.logger.error(f"Error deleting {file_path}: {str(e)}")

