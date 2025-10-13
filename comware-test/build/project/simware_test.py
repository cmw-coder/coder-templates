import os
import subprocess
import time
import requests
import json
import shutil
from threading import Timer
import datetime
from threading import Thread
import getpass

# SVN配置信息
SVN_URL = "http://10.153.3.214/comware-test-script/50.多环境移植/AIGC/simware_test"
USERNAME = getpass.getuser()

# SVN上传专用账号
SVN_UPLOAD_USERNAME = "l31810"
SVN_UPLOAD_PASSWORD = "Mayday673*"

def configure_svn_no_password_store():
    """配置SVN不存储明文密码"""
    svn_config_dir = os.path.expanduser('~/.subversion')
    servers_file = os.path.join(svn_config_dir, 'servers')
    
    # 确保.subversion目录存在
    os.makedirs(svn_config_dir, exist_ok=True)
    
    # 写入配置
    with open(servers_file, 'w') as f:
        f.write("[global]\n")
        f.write("store-plaintext-passwords = no\n")
        f.write("store-passwords = no\n")

def create_user_dir_if_not_exists(username):
    """检查并创建用户目录（如果不存在）"""
    user_dir_url = f"{SVN_URL}/{username}"
    
    # 检查目录是否存在 - 使用当前用户账号
    try:
        subprocess.run([
            'svn', 'ls', '--non-interactive', '--no-auth-cache',
            '--username', SVN_UPLOAD_USERNAME, '--password', SVN_UPLOAD_PASSWORD,
            user_dir_url
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 目录已存在
        return True
    except subprocess.CalledProcessError:
        # 目录不存在，尝试创建 - 使用当前用户账号
        try:
            subprocess.run([
                'svn', 'mkdir', '--non-interactive', '--no-auth-cache',
                '--username', SVN_UPLOAD_USERNAME, '--password', SVN_UPLOAD_PASSWORD,
                '-m', f"Create user directory for {username}", user_dir_url
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to create user directory: {e}")
            return False

def create_timestamp_dir():
    """创建时间戳目录"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    username = getpass.getuser()
    
    # 首先确保用户目录存在 - 使用当前用户账号
    if not create_user_dir_if_not_exists(username):
        return None
    
    dir_url = f"{SVN_URL}/{username}/{timestamp}"
    
    try:
        # 创建时间戳目录 - 使用当前用户账号
        subprocess.run([
            'svn', 'mkdir', '--username', SVN_UPLOAD_USERNAME, '--password', SVN_UPLOAD_PASSWORD,
            '-m', f"Create timestamp directory {timestamp}", dir_url
        ], check=True)
        return dir_url
    except subprocess.CalledProcessError as e:
        print(f"Failed to create timestamp directory: {e}")
        return None

def upload_files_to_svn(svn_dir):
    """上传当前目录所有文件到SVN（仅排除本脚本文件），使用专用SVN账号"""
    current_dir = os.getcwd()
    current_script = os.path.basename(__file__)  # 获取当前脚本文件名
    
    # 确保有__init__.py文件（如果需要的话）
    init_file = os.path.join(current_dir, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, 'a').close()
        print("Created empty __init__.py file")

    # 收集需要处理的文件
    files_to_upload = []
    renamed_files = []  # 存储重命名记录 [(old_path, new_path)]
    
    for root, _, files in os.walk(current_dir):
        # 跳过__pycache__目录
        if "__pycache__" in root.split(os.sep):
            continue
        
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, current_dir)
            
            # 排除条件：仅排除当前脚本文件
            if file == current_script:
                continue
                
            # 特别处理.py文件（除conftest.py和__init__.py外）
            if (file.endswith('.py') and 
                file not in ['conftest.py', '__init__.py'] and
                not file.startswith('test_')):
                
                # 重命名为test_前缀
                new_name = f"test_{file}"
                new_path = os.path.join(root, new_name)
                
                try:
                    os.rename(filepath, new_path)
                    print(f"Renamed: {file} -> {new_name}")
                    renamed_files.append((filepath, new_path))
                    files_to_upload.append(new_path)
                except Exception as e:
                    print(f"Failed to rename {file}: {e}")
                    files_to_upload.append(filepath)  # 仍上传原文件
            else:
                files_to_upload.append(filepath)

    if not files_to_upload:
        print("No files to upload.")
        return False

    try:
        # 创建临时目录并复制文件
        temp_dir = os.path.join(current_dir, "temp_upload")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        os.makedirs(temp_dir)
        
        for src in files_to_upload:
            rel_path = os.path.relpath(src, current_dir)
            dst = os.path.join(temp_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        
        # 执行SVN导入 - 使用专用SVN账号
        subprocess.run([
            'svn', 'import', temp_dir, svn_dir,
            '--username', SVN_UPLOAD_USERNAME,
            '--password', SVN_UPLOAD_PASSWORD,
            '-m', f"Upload files from {current_dir}"
        ], check=True)
        
        print(f"All files uploaded to {svn_dir} successfully.")
        return True
        
    except Exception as e:
        print(f"Upload failed: {e}")
        # 尝试恢复重命名的文件
        for old_path, new_path in renamed_files:
            try:
                os.rename(new_path, old_path)
                print(f"Restored original name: {os.path.basename(new_path)}")
            except Exception as restore_error:
                print(f"Failed to restore {new_path}: {restore_error}")
        return False
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def upload_single_file_to_svn(file_path, svn_dir):
    """上传单个文件到SVN目录，使用专用SVN账号"""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return False
    
    try:
        # 创建临时工作目录
        temp_dir = os.path.join(os.path.dirname(file_path), "temp_single_upload")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        file_name = os.path.basename(file_path)
        svn_file_url = f"{svn_dir.rstrip('/')}/{file_name}"
        
        # 检查SVN中是否已存在该文件 - 使用专用SVN账号
        try:
            subprocess.run(
                ['svn', 'info', svn_file_url, 
                 '--username', SVN_UPLOAD_USERNAME,
                 '--password', SVN_UPLOAD_PASSWORD],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            file_exists_in_svn = True
        except subprocess.CalledProcessError:
            file_exists_in_svn = False
        
        if file_exists_in_svn:
            # 文件已存在，执行更新操作 - 使用专用SVN账号
            print(f"File {file_name} exists in SVN, updating content...")
            
            # 检出包含该文件的目录
            subprocess.run([
                'svn', 'checkout', svn_dir, temp_dir,
                '--username', SVN_UPLOAD_USERNAME,
                '--password', SVN_UPLOAD_PASSWORD,
                '--depth', 'empty'
            ], check=True)
            
            # 复制新文件覆盖检出的文件
            dst = os.path.join(temp_dir, file_name)
            shutil.copy2(file_path, dst)
            
            # 提交更改
            subprocess.run([
                'svn', 'commit', '-m', f"Update file {file_name}", 
                '--username', SVN_UPLOAD_USERNAME,
                '--password', SVN_UPLOAD_PASSWORD,
            ], check=True, cwd=temp_dir)
            
            print(f"File {file_name} updated in {svn_dir} successfully.")
        else:
            # 文件不存在，执行导入操作 - 使用专用SVN账号
            print(f"File {file_name} does not exist in SVN, importing new file...")
            
            # 复制文件到临时目录
            dst = os.path.join(temp_dir, file_name)
            shutil.copy2(file_path, dst)
            
            # 执行SVN导入
            subprocess.run([
                'svn', 'import', temp_dir, svn_dir,
                '--username', SVN_UPLOAD_USERNAME,
                '--password', SVN_UPLOAD_PASSWORD,
                '-m', f"Upload file {file_name}"
            ], check=True)
            
            print(f"File {file_name} uploaded to {svn_dir} successfully.")
        
        return True
        
    except Exception as e:
        print(f"Operation failed: {e}")
        return False
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

class restClient:
    base_url = "http://10.111.8.68:8000/aigc"
    _COMMON_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) RDTestClient/0.6.2025042918 Chrome/108.0.5359.215 Electron/22.3.6 Safari/537.36",
    }
    def promoteScripts(self, path, output_path):
        url = f"{self.base_url}/promote_scripts"
        try:
            response = requests.post(
                url,
                headers=self._COMMON_HEADERS,
                json={
                    "scriptspath": path
                },
                timeout=2000,
                proxies={"http": None, "https": None}  # 关键点：强制禁用代理
            )
            response.raise_for_status()
            response_data = response.json()
            print("####################################################")
            print(response_data)
            return_info = response_data.get('return_info')

            try:
                print(output_path)
                
                # Process the return_info for better readability
                formatted_content = str(return_info)
                
                # Replace escaped newlines with actual newlines
                formatted_content = formatted_content.replace('\\n', '\n')
                
                # Replace any other escaped characters if needed (like \\t)
                formatted_content = formatted_content.replace('\\t', '\t')
                
                # Remove extra quotes if they exist at start/end
                if formatted_content.startswith("'") and formatted_content.endswith("'"):
                    formatted_content = formatted_content[1:-1]
                elif formatted_content.startswith('"') and formatted_content.endswith('"'):
                    formatted_content = formatted_content[1:-1]
                
                print(formatted_content)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted_content)

            except IOError as write_error:
                # File write failed, attempt to write error info to same file
                error_data = {
                    'status': 'error',
                    'message': f'文件写入失败: {str(write_error)}',
                    'original_response': response_data
                }
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(error_data, f, indent=4, ensure_ascii=False)
                except IOError:
                    print("无法将任何数据写入输出文件")
            return response
        except requests.exceptions.RequestException as e:
            print(f"脚本验证失败: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"错误详情: {e.response.text}")
            raise

if __name__ == "__main__":
    username = getpass.getuser()
    create_user_dir_if_not_exists(username)
    # 1. 创建时间戳目录
    svn_target_dir = create_timestamp_dir()
    if not svn_target_dir:
        exit(1)
    print("上传的svn目录为:",svn_target_dir)
    # 2. 上传文件
    if not upload_files_to_svn(svn_target_dir):
        exit(1)
    #本地创建simware_test.jsonl
    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, "simware_test.jsonl")

    client = restClient()
    client.promoteScripts(svn_target_dir, output_path)
    # 文件生成后上传到SVN
    if os.path.exists(output_path):
        upload_single_file_to_svn(output_path, svn_target_dir)
