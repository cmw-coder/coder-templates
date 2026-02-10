import re
from typing import List, Tuple, Dict
import xml.etree.ElementTree as ET


def find_rpc_xml_segments(text: str) -> List[Tuple[str, int, int]]:
    """
    查找被<rpc>标签包围的XML片段

    Args:
        text: 输入字符串

    Returns:
        List[Tuple[str, int, int]]: 每个元素为(rpc_xml_content, start_index, end_index)
    """
    rpc_segments = []

    # 匹配<rpc>开始标签（可能带属性）
    rpc_start_pattern = r'<rpc\s*(?:\s+[^>]*)?>'

    i = 0
    while i < len(text):
        # 查找下一个<rpc>开始标签
        start_match = re.search(rpc_start_pattern, text[i:], re.IGNORECASE)
        if not start_match:
            break

        start_pos = i + start_match.start()

        # 查找对应的</rpc>结束标签
        end_pattern = r'</rpc\s*>'
        end_match = re.search(end_pattern, text[start_pos:], re.IGNORECASE)

        if end_match:
            end_pos = start_pos + end_match.end()
            rpc_content = text[start_pos:end_pos]

            # 验证是否是有效的XML
            if is_valid_xml(rpc_content):
                rpc_segments.append((rpc_content, start_pos, end_pos))
                i = end_pos  # 移动到当前RPC片段的末尾
            else:
                i = start_pos + 1  # 如果不是有效XML，移动一个字符继续搜索
        else:
            i = start_pos + 1  # 没有找到结束标签，移动一个字符继续搜索

    return rpc_segments


def is_valid_xml(xml_string: str) -> bool:
    """
    检查字符串是否是有效的XML

    Args:
        xml_string: 要检查的XML字符串

    Returns:
        bool: 是否是有效的XML
    """
    try:
        ET.fromstring(xml_string)
        return True
    except ET.ParseError:
        return False


def extract_rpc_xml_content(text: str) -> List[str]:
    """
    提取被<rpc>标签包围的XML内容

    Args:
        text: 输入字符串

    Returns:
        List[str]: 所有RPC XML片段的列表
    """
    segments = find_rpc_xml_segments(text)
    return [segment[0] for segment in segments]


def extract_rpc_with_details(text: str) -> List[Dict]:
    """
    提取RPC XML片段及其详细信息

    Args:
        text: 输入字符串

    Returns:
        List[Dict]: 包含RPC片段和详细信息的字典列表
    """
    segments = find_rpc_xml_segments(text)
    result = []

    for xml_content, start, end in segments:
        # 提取RPC标签的属性（如果有）
        attributes = extract_rpc_attributes(xml_content)

        # 提取RPC内部的内容（去掉外层的rpc标签）
        inner_content = extract_inner_xml(xml_content, 'rpc')

        result.append({
            'full_rpc': xml_content,
            'inner_content': inner_content,
            'start_position': start,
            'end_position': end,
            'attributes': attributes,
            'length': len(xml_content)
        })

    return result


def extract_rpc_attributes(rpc_xml: str) -> Dict[str, str]:
    """
    提取<rpc>标签的属性

    Args:
        rpc_xml: RPC XML字符串

    Returns:
        Dict[str, str]: 属性名和值的字典
    """
    attributes = {}

    # 匹配<rpc>开始标签及其属性
    start_tag_match = re.search(r'<rpc\s+([^>]*)>', rpc_xml, re.IGNORECASE)
    if start_tag_match:
        attr_string = start_tag_match.group(1)
        # 匹配属性名和值
        attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        attr_matches = re.findall(attr_pattern, attr_string)

        for name, value in attr_matches:
            attributes[name] = value

    return attributes


def extract_inner_xml(xml_string: str, tag_name: str) -> str:
    """
    提取指定标签内部的XML内容

    Args:
        xml_string: 完整的XML字符串
        tag_name: 标签名

    Returns:
        str: 内部XML内容
    """
    pattern = f'<{tag_name}[^>]*>(.*?)</{tag_name}>'
    match = re.search(pattern, xml_string, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()
    return ""


def parse_rpc_operations(rpc_content: str) -> List[Dict]:
    """
    解析RPC内容中的操作（如edit-config, get-config等）

    Args:
        rpc_content: RPC内部内容

    Returns:
        List[Dict]: 操作信息列表
    """
    operations = []

    # 常见的NETCONF RPC操作
    rpc_operations = ['get-config', 'edit-config', 'get', 'copy-config',
                      'delete-config', 'lock', 'unlock', 'close-session',
                      'kill-session']

    for operation in rpc_operations:
        pattern = f'<{operation}[^>]*>(.*?)</{operation}>'
        matches = re.findall(pattern, rpc_content, re.IGNORECASE | re.DOTALL)

        for match in matches:
            operations.append({
                'operation': operation,
                'content': match.strip(),
                'full_element': f'<{operation}>...'
            })

    return operations


def read_file_with_fallback(filepath: str) -> str or None:
    """
    以健壮的方式读取一个未知编码格式的文件。
    """
    encodings_to_try = ['utf-8', 'gbk', 'windows-1252', 'latin-1']

    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                # print(f"INFO: 成功使用 '{encoding}' 编码读取文件。")
                return f.read()
        except UnicodeDecodeError:
            continue

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            # print(f"WARNING: 常用编码均失败。尝试使用 'utf-8' 并替换无效字符。")
            return f.read()
    except Exception as e:
        print(f"ERROR: 读取文件时发生无法处理的错误: {e}")
        return None


# --- 主执行逻辑 ---
if __name__ == "__main__":

    file_to_process = r"D:\netconf_test_point_code\Certainty\B75\40.02_LAN\40.02.99_Netconf\H3C-BRAS\IPV4-IPOE_1_0_1\test_netconf_BRAS_BrasInterfaces_IPoEAuthFailurePolicy_1_1_2.py"

    try:
        print(f"已成功创建示例文件: '{file_to_process}'")

        # 2. 读取文件内容
        print(f"\n--- 开始处理文件: {file_to_process} ---")
        content = read_file_with_fallback(file_to_process)

        if content:
            print("=== 提取所有RPC XML片段 ===")
            rpc_list = extract_rpc_xml_content(content)
            print(rpc_list[0])
            for i, rpc in enumerate(rpc_list, 1):
                print(f"RPC片段 {i}:")
                print(rpc)
                print("-" * 50)

            print("\n=== 提取RPC详细信息 ===")
            rpc_details = extract_rpc_with_details(content)
            for detail in rpc_details:
                print(f"位置: {detail['start_position']}-{detail['end_position']}")
                print(f"长度: {detail['length']} 字符")
                print(f"属性: {detail['attributes']}")
                print(f"内部内容:")
                print(detail['inner_content'][:200] + "..." if len(detail['inner_content']) > 200 else detail[
                    'inner_content'])

                # 解析操作
                operations = parse_rpc_operations(detail['inner_content'])
                if operations:
                    print("包含的操作:")
                    for op in operations:
                        print(f"  - {op['operation']}")

                print("=" * 60)

            print("\n=== 验证XML有效性 ===")
            for i, rpc in enumerate(rpc_list, 1):
                is_valid = is_valid_xml(rpc)
                print(f"RPC片段 {i} 有效性: {is_valid}")

    except Exception as e:
        print(f"程序执行时发生错误: {e}")