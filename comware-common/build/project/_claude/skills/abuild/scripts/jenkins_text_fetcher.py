import requests
from requests.auth import HTTPBasicAuth
import os
import sys


class JenkinsTextFetcher:
    def __init__(self, jenkins_url=None, api_token=None, username=None):
        """
        初始化Jenkins文本获取器
        """
        self.jenkins_url = jenkins_url or os.getenv('JENKINS_SERVER_URL', 'http://10.153.3.174:8080')
        self.api_token = api_token or os.getenv('JENKINS_API_TOKEN', '11c7798a2446cc8acb1f871ad486a4b8ff')
        self.username = username or 'g29624'

        # 确保URL格式正确
        if not self.jenkins_url.endswith('/'):
            self.jenkins_url += '/'

    def fetch_text_content(self, url_path):
        """
        获取指定URL的文本内容

        参数:
        - url_path: 相对于Jenkins服务器的路径，如 "job/my-job/consoleText"
        """
        # 构建完整URL
        if url_path.startswith('/'):
            url_path = url_path[1:]
        full_url = f"{self.jenkins_url}{url_path}"

        try:
            response = requests.get(
                full_url,
                auth=HTTPBasicAuth(self.username, self.api_token),
                timeout=30,
                stream=True  # 支持大文件流式下载
            )

            if response.status_code == 200:
                # 直接返回文本内容
                content = response.text
                return {
                    'success': True,
                    'content': content,
                    'status_code': 200,
                    'content_length': len(content),
                    'url': full_url
                }
            else:
                return {
                    'success': False,
                    'error': f"请求失败，状态码: {response.status_code}",
                    'status_code': response.status_code,
                    'response_text': response.text[:500] if response.text else '',  # 只取前500字符
                    'url': full_url
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"请求失败: {str(e)}",
                'status_code': None,
                'url': full_url
            }

    def fetch_and_save_text(self, url_path, save_path=None):
        """
        获取文本内容并可选地保存到文件
        """
        result = self.fetch_text_content(url_path)

        if result['success'] and save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                result['saved_to'] = save_path
            except Exception as e:
                result['save_error'] = str(e)

        return result

    def test_connection(self):
        """
        测试Jenkins连接
        """
        test_url = "api/json"
        return self.fetch_text_content(test_url)


def main():
    """
    命令行主函数
    """
    if len(sys.argv) < 2:
        print("使用方法: python jenkins_text_fetcher.py <URL路径> [保存文件路径]")
        print("\n示例:")
        print("  # 获取控制台输出并显示")
        print("  python jenkins_text_fetcher.py job/my-job/lastBuild/consoleText")
        print("  \n  # 获取内容并保存到文件")
        print("  python jenkins_text_fetcher.py job/my-job/lastBuild/consoleText output.txt")
        print("  \n  # 测试连接")
        print("  python jenkins_text_fetcher.py test_connection")
        sys.exit(1)

    url_path = sys.argv[1]
    save_path = sys.argv[2] if len(sys.argv) > 2 else None

    fetcher = JenkinsTextFetcher()

    if url_path == "test_connection":
        print("正在测试Jenkins连接...")
        result = fetcher.test_connection()
    else:
        print(f"正在获取: {url_path}")
        if save_path:
            result = fetcher.fetch_and_save_text(url_path, save_path)
        else:
            result = fetcher.fetch_text_content(url_path)

    # 输出结果
    print("\n" + "=" * 50)
    if result['success']:
        print("✓ 操作成功")
        print(f"状态码: {result['status_code']}")
        print(f"内容长度: {result.get('content_length', 0)} 字符")

        if 'saved_to' in result:
            print(f"内容已保存到: {result['saved_to']}")

        # 显示内容（如果未保存到文件且内容不长）
        if not save_path and result.get('content'):
            content = result['content']
            # if len(content) <= 1000:  # 只显示前1000字符
            #     print(f"\n内容预览:\n{'-' * 20}")
            #     print(content)
            # else:
            #     print(f"\n内容过长 ({len(content)} 字符)，前1000字符预览:\n{'-' * 20}")
            #     print(content[:1000] + "...")
            print(content)
    else:
        print("✗ 操作失败")
        print(f"错误: {result['error']}")
        if result.get('status_code'):
            print(f"状态码: {result['status_code']}")
        if result.get('response_text'):
            print(f"响应内容: {result['response_text']}")


# 便捷函数
def fetch_jenkins_text(url_path, save_to_file=None):
    """
    便捷函数：一行代码获取Jenkins文本内容
    """
    fetcher = JenkinsTextFetcher()
    if save_to_file:
        return fetcher.fetch_and_save_text(url_path, save_to_file)
    else:
        return fetcher.fetch_text_content(url_path)


if __name__ == "__main__":
    main()
