import os
import json
from pathlib import Path
# from app import mechanization
from itertools import combinations

def run_CRW4(batchName, batch): # 秉榮: 修改此處，加入 batchName 參數
    """
    模擬呼叫封閉式軟體 CRW4 進行反應計算，
    實際應用中請改成呼叫 CRW4 的 API 或其他介面。
    """
    mechanization.automate(batch, batchName) # 秉榮: 修改此處，加入 batchName 參數
    print(f"執行 CRW4 批次，包含 {len(batch)} 筆資料，前3筆：{batch[:3]}")

def split_list(data, chunk_size):
    """將 data 切分成每個大小不超過 chunk_size 的子清單"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def split_group_with_labels(group, label, sub_chunk_size):
    """
    將一組資料依 sub_chunk_size 切分，並標記上半部與下半部
    若只有一個子組，則只會回傳 {label: subgroup}；若有兩個，則回傳
    {label: first_half, label+"'": second_half}
    """
    subs = split_list(group, sub_chunk_size)
    result = {}
    if not subs:
        return result
    if len(subs) == 1:
        result[label] = subs[0]
    else:
        result[label] = subs[0]
        result[label + "'"] = subs[1]
    return result

DONE_FILE = Path("algo_done.txt")  # 一行一個 batch_name 的進度檔

def read_done():
    """讀取已完成批次集合（若檔案不存在回傳空集合）"""
    if not DONE_FILE.exists():
        return set()
    lines = DONE_FILE.read_text(encoding="utf-8").splitlines()
    result = set()  # 儲存不重複的 batch_id
    for line in lines:
        data = line.strip() # 移除前後空白、換行符號
        if data == "":      # 空行就略過
            continue
        result.add(data)
    return result

def mark_done(batch_name):
    """成功才把 batch_id 追加一行到 done.txt"""
    with DONE_FILE.open("a", encoding="utf-8") as f:
        f.write(batch_name + "\n")

def should_skip(batch_name, done_set):
    """該批次若已在 done.txt 就略過"""
    return batch_name in done_set

def main():
    # 1. 讀取 JSON 檔案，抽取 success_item 並取出 CAS 號碼列表
    json_path = r"/Users/howardhung/Vscode/CRW4-automation-new/record_test/SDS_911058_001_20251021.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # success_item 格式預期為 [ {"10141-05-6": "COBALT NITRATE"}, ... ]
    success_items = data.get("success_item", [])
    cas_list = []
    for item in success_items:
        # 從字典取出 key（CAS 號碼）
        cas_list.extend(list(item.keys()))
    
    print(f"從 JSON 中抽取到 {len(cas_list)} 筆 CAS 號碼。")
    
    # 2. 將 CAS 清單分成 4 組（例如 400 筆資料分成 4 組，每組 100 筆）
    max_batch_size = 100
    groups = split_list(cas_list, max_batch_size)
    # 給每組設定字母標籤：A、B、C、D…
    group_labels = [chr(ord('A') + i) for i in range(len(groups))]
    
    # A.json, B.json, ...
    output_base = r"/Users/howardhung/Vscode/CRW4-automation-new/record_test/"
    for label, group in zip(group_labels, groups):
        print(f"組 {label} 有 {len(group)} 筆資料")
        file_name = f"{output_base}{label}.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(group, f, ensure_ascii=False, indent=4)
    
    # 讀取前次進度
    done = read_done()
    print(f"\n前次完成批次數：{len(done)}")

    print("\n=== 組內反應計算 ===")
    # 每組內部配對：直接將每組的資料送入 CRW4
    for label, group in zip(group_labels, groups):
        if should_skip(label, done):
            print(f"[SKIP] 組內 {label}（已完成）")
            continue
        print(f"處理組 {label} 內部配對")
        try:
            # run_CRW4(label, group) # 秉榮: 修改此處，加入 batchName 參數
            mark_done(label)  # 成功才進行記錄
        except Exception as e:
            print(f"[ERR] 組內 {label} 發生錯誤：{e}")
            return 

    print("\n=== 組間反應計算 ===")
    # 3. 組間反應計算：任兩組之間所有配對
    # 每次 CRW4 最多 100 筆，因此將每組拆分成上半部與下半部 (50 筆一組)
    sub_chunk_size = max_batch_size // 2  # 50 筆
    for (i, group_A), (j, group_B) in combinations(enumerate(groups), 2):
        label_A = group_labels[i]
        label_B = group_labels[j]
        
        # 將 group_A 與 group_B 分別拆分並標記為上半部與下半部
        subs_A = split_group_with_labels(group_A, label_A, sub_chunk_size)
        subs_B = split_group_with_labels(group_B, label_B, sub_chunk_size)
        
        # 子組間兩兩配對，並依照子組標籤印出
        for sub_label_A, sub_group_A in subs_A.items():
            for sub_label_B, sub_group_B in subs_B.items():
                batch = sub_group_A + sub_group_B
                combine_sub_label_name = f"{sub_label_A}_{sub_label_B}"
                if(should_skip(combine_sub_label_name, done)):
                    print(f"[SKIP] 組間 {combine_sub_label_name}（已完成）")
                    continue
                print(f"處理組 {sub_label_A} 與組 {sub_label_B} 的子組配對 (共 {len(batch)} 筆)")
                try: 
                    # run_CRW4(f"{combine_sub_label_name}", batch) # 秉榮: 修改此處，加入 batchName 參數
                    mark_done(f"{combine_sub_label_name}")  # 成功才記錄（新增）
                except Exception as e:
                    print(f"[ERR ] 組間 {combine_sub_label_name} 發生錯誤：{e}")

if __name__ == "__main__":
    main()
