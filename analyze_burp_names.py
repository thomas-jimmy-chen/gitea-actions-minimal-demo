"""分析 Burp Suite 資料中的用戶姓名位置"""
import xml.etree.ElementTree as ET
import base64
import re

tree = ET.parse('D:/Dev/eebot/20251230-bu.txt')
root = tree.getroot()

print("=" * 60)
print("分析 Burp Suite 資料中的用戶姓名位置")
print("=" * 60)

for item in root.findall('item'):
    path_elem = item.find('path')
    path = path_elem.text if path_elem is not None else ''

    if path == '/user/index':
        response = item.find('response')
        if response is not None and response.text:
            raw = base64.b64decode(response.text)

            parts = raw.split(b'\r\n\r\n', 1)
            if len(parts) == 2:
                body = parts[1]

                # 搜尋 CurrentName 的位置
                idx = body.find(b'CurrentName')
                if idx != -1:
                    snippet = body[idx:idx+100]
                    print("\n=== CurrentName 位置 ===")
                    print("Raw bytes:", snippet)
                    print("UTF-8 解碼:", snippet.decode('utf-8', errors='replace'))

                # 搜尋 userName
                idx2 = body.find(b'userName')
                if idx2 != -1:
                    snippet2 = body[idx2:idx2+80]
                    print("\n=== userName 位置 ===")
                    print("Raw bytes:", snippet2)
                    print("UTF-8 解碼:", snippet2.decode('utf-8', errors='replace'))

                # 搜尋 window.analyticsData 完整區塊
                match = re.search(rb'window\.analyticsData\s*=\s*\{[^}]+\}', body)
                if match:
                    print("\n=== window.analyticsData 完整區塊 ===")
                    content = match.group()
                    print("UTF-8 解碼:", content.decode('utf-8', errors='replace'))

        break

# 同時檢查其他可能有姓名的 API
print("\n" + "=" * 60)
print("檢查其他 API 端點中的姓名資訊")
print("=" * 60)

name_apis = []
for item in root.findall('item'):
    path_elem = item.find('path')
    path = path_elem.text if path_elem is not None else ''
    response = item.find('response')

    if response is not None and response.text:
        try:
            raw = base64.b64decode(response.text)
            parts = raw.split(b'\r\n\r\n', 1)
            if len(parts) == 2:
                body = parts[1]
                # 檢查是否包含 "name" 字段和非 ASCII 字符（可能是中文姓名）
                if b'"name"' in body and any(b > 127 for b in body):
                    # 解碼 JSON 響應看看
                    try:
                        import json
                        text = body.decode('utf-8', errors='replace')
                        if text.strip().startswith('{') or text.strip().startswith('['):
                            data = json.loads(text)
                            # 搜尋 name 字段
                            def find_names(obj, path=""):
                                results = []
                                if isinstance(obj, dict):
                                    for k, v in obj.items():
                                        if k in ('name', 'userName', 'user_name', 'realName'):
                                            if isinstance(v, str) and len(v) > 0:
                                                results.append((path + "." + k, v))
                                        elif isinstance(v, (dict, list)):
                                            results.extend(find_names(v, path + "." + k))
                                elif isinstance(obj, list):
                                    for i, item in enumerate(obj[:3]):  # 只檢查前3個
                                        results.extend(find_names(item, f"{path}[{i}]"))
                                return results

                            names = find_names(data)
                            if names:
                                name_apis.append((path, names[:5]))  # 只保留前5個
                    except:
                        pass
        except:
            pass

# 印出結果
for api_path, names in name_apis[:20]:  # 只印前20個API
    print(f"\n{api_path}:")
    for field_path, value in names:
        print(f"  {field_path}: {value}")
