import json
import os
import subprocess
import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
import copy
import xml.etree.ElementTree as ET
import copy
import traceback
import re
def strip_namespace(tag: str) -> str:
    """一个辅助函数，用于从带命名空间的标签中提取纯标签名。"""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag



def strip_namespace(tag: str) -> str:
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def extract_xml_by_tags(xml_string: str, tags: list) -> str:
    """
    根据指定的标签路径从XML字符串中提取子树
    
    Args:
        xml_string (str): 输入的XML字符串
        tags (list): 标签名称列表，表示要查找的路径，如 ["Configuration", "System"]
    
    Returns:
        str: 提取的XML子树字符串，或错误信息
    """
    # 检查标签列表是否为空
    if not tags:
        return None, []#"错误：标签列表不能为空。"

    try:
        # 解析XML字符串为ElementTree对象
        root = ET.fromstring(xml_string)
        # 构建子节点到父节点的映射关系，用于后续查找祖先节点
        parent_map = {c: p for p in root.iter() for c in p}

        # 获取目标标签名称（路径中的最后一个标签）
        target_tag_name = tags[-1]
        # 将输入的标签名称也转为小写，用于后续不区分大小写
        lower_target_tag_name = tags[-1].lower()
        # 查找所有具有目标标签名称的元素（忽略命名空间）, 将输入的标签路径也转为小写，用于后续不区分大小写的路径匹配

        candidates = [elem for elem in root.iter()
                      if strip_namespace(elem.tag).lower() == target_tag_name.lower()]

        # 如果没有找到目标标签，返回错误信息

        if not candidates:
            return None, []#f"错误：在XML中未找到最终标签 <{tags[-1]}> (已忽略大小写)"

        # 初始化目标节点和完整路径
        target_node = None
        full_element_path = []


        
        # 遍历所有候选节点，查找符合路径要求的节点
        # 此时最后的标签已经确定，不需要大小写
        for candidate in candidates:
            # 构建当前候选节点的祖先节点列表
            ancestors = []
            curr = candidate
            # 向上遍历到根节点，构建祖先节点链
            while curr in parent_map:
                parent = parent_map[curr]
                ancestors.insert(0, parent)  # 插入到列表开头以保持从根到父的顺序
                if parent is root: # 到达根节点则停止
                    break
                curr = parent

            # # 提取所有祖先节点的标签名（去除命名空间）
            # ancestor_tag_names = [strip_namespace(el.tag) for el in ancestors]
            # 获取祖先路径的标签名列表，并转为小写
            ancestor_tags_lower = [strip_namespace(el.tag).lower() for el in ancestors]


            # # 获取需要检查的祖先标签（除目标标签外的所有标签）
            # tags_to_check = tags[:-1]
            # 将输入的标签路径也转为小写，用于后续不区分大小写的路径匹配
            lower_tags_to_check = [tag.lower() for tag in tags[:-1]]


            # 假设路径有效
            is_valid_path = True
            # 创建祖先标签列表的副本用于搜索
            temp_ancestor_search_list = list(ancestor_tags_lower)
            try:
                # 检查祖先节点是否包含所需的所有标签
                for tag_to_find in lower_tags_to_check:
                    # 查找标签在祖先列表中的位置
                    idx = temp_ancestor_search_list.index(tag_to_find)
                    # 更新搜索列表，只保留当前位置之后的元素
                    temp_ancestor_search_list = temp_ancestor_search_list[idx + 1:]
            except ValueError:
                # index函数没有找到
                # 如果任何一个标签找不到，则路径无效
                is_valid_path = False

            # 如果找到有效路径
            if is_valid_path:
                target_node = candidate
                # 构建包含目标节点的完整路径
                path_with_target = ancestors + [target_node]
                # 查找路径起始节点的索引
                start_index = next((i for i, el in enumerate(path_with_target) if strip_namespace(el.tag) == tags[0]),
                                   -1)

                # 如果找到起始节点，则保存完整路径
                if start_index != -1:
                    full_element_path = path_with_target[start_index:]
                    break

        # 如果未找到目标节点或完整路径，返回错误信息
        if not target_node or not full_element_path:
            path_str = " -> ".join(tags)
            return None, []#f"错误：未找到符合路径 {path_str} 的元素。"

        # --- 准备工作 ---
        # 获取路径的根节点
        root_of_path = full_element_path[0]
        # 深拷贝整个结构以避免修改原始XML
        new_root = copy.deepcopy(root_of_path)

        # 创建路径上所有节点的集合，用于快速判断节点是否在路径上
        golden_path_nodes = set(full_element_path)

        # --- 修正后的修剪逻辑 ---
        def prune_tree(original_node, copied_node):
            """
            递归修剪树结构，只保留路径上的节点和其内容
            
            Args:
                original_node: 原始XML树中的节点
                copied_node: 拷贝树中的对应节点
            """
            # 【关键修复】：如果当前节点就是最终目标节点，
            # 则保留其所有内容（因为是深拷贝来的），不再向下修剪。
            if original_node == target_node:
                return None, []#"original_node == target_node"

            # 获取原始节点的所有子节点
            original_children = list(original_node)

            # 存储需要删除的子节点
            children_to_remove = []

            # 遍历拷贝节点的所有子节点
            for i, copied_child in enumerate(list(copied_node)):
                # 获取对应的原始子节点
                original_child = original_children[i]

                # 判断子节点是否在目标路径上
                if original_child in golden_path_nodes:
                    # 如果子节点在路径上（它是目标节点或目标的祖先），递归处理
                    prune_tree(original_child, copied_child)
                elif len(list(copied_child)) > 0:
                    # 如果子节点不在路径上，且是容器（有子节点），标记删除
                    # 例如：BRAS下的 <AccessLog>
                    children_to_remove.append(copied_child)
                # 如果是叶子节点且不在路径上，默认保留（根据需求）

            # 执行删除操作，移除不在路径上的容器节点
            for child in children_to_remove:
                copied_node.remove(child)

        # 开始修剪树结构
        prune_tree(root_of_path, new_root)


        # --- 命名空间处理 ---
        # 提取命名空间URI
        namespace_uri = ''
        if '}' in new_root.tag:
            namespace_uri = new_root.tag.split('}')[0][1:]

        # 这里使用一个临时的 context manager 来注册命名空间，
        # 防止污染全局 ElementTree 设置，影响后续可能的其他XML处理
        try:
            # 如果存在命名空间，则注册它
            if namespace_uri:
                ET.register_namespace('', namespace_uri)

            # 对XML树进行格式化缩进
            ET.indent(new_root, space="  ")
            # 生成最终的XML字符串
            xml_str = ET.tostring(new_root, encoding='unicode', short_empty_elements=False)
            # print("xx",xml_str)
        finally:
            # 可选：清理注册的命名空间，保持环境整洁 (ElementTree并没有提供简单的unregister方法，
            # 通常在脚本运行结束时自动释放。对于简单脚本，不清理也可)
            pass

        return xml_str, [strip_namespace(element.tag) for element in full_element_path]

    except ET.ParseError as e:
        # 处理XML解析错误
        print(f"XML解析错误: {e} {xml_string}")
        return None, []#f"XML解析错误: {e}"
    except Exception as e:
        # 处理其他未知错误
        print(f"发生未知错误: {e}\n{traceback.format_exc()}")
        return None, []#f"发生未知错误: {e}\n{traceback.format_exc()}"


# --- 主程序部分保持不变 ---
if __name__ == "__main__":
    xml_file_path = r"D:\yang\V9xml\H3C-vlan-config@2025-07-17.xml"
    try:
        # with open(xml_file_path, 'r', encoding='utf-8-sig') as xml_file:
        #     xml_data = xml_file.read()
        xml_data = """
        <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="100">
                      <get>
                        <filter type="subtree">
                          <top xmlns="http://www.h3c.com/netconf/data:1.0">
                            <BRAS>
                              <BrasInterfaces>
                                <BrasInterface>
                                  <IfIndex>{TestClass.DUT1_PORT1_IFINDEX}</IfIndex>
                                  <IPoEAuthFailurePolicy>
                                    <ChastenAuthFailedTimes/>
                                    <ChastenPeriod/>
                                  </IPoEAuthFailurePolicy>
                                </BrasInterface>
                              </BrasInterfaces>
                            </BRAS>
                          </top>
                        </filter>
                      </get>
                    </rpc>
        """
        cleaned_xml = re.sub(r'\s+xc:\w+=\"[^\"]*\"', '', xml_data)

        tags_to_extract = ['BRAS', 'BrasInterfaces']
        extracted_xml = extract_xml_by_tags(cleaned_xml, tags_to_extract)
        print(extracted_xml)
    except FileNotFoundError:
        print(f"错误：找不到文件 {xml_file_path}")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")


