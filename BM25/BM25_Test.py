import re
from rank_bm25 import BM25Okapi

# 1. 定義 n-gram 分詞器 (字元級)
def get_char_ngrams(text, n=3):
    """
    將文字轉換為長度為 n 的字元序列。
    例如: "Apple" -> ["App", "ppl", "ple"]
    """
    # 清理非字母數字字元並轉小寫
    text = re.sub(r'[^\w\s]', '', text).lower()
    # 產生 n-grams
    return [text[i:i+n] for i in range(len(text) - n + 1)]

# 2. 原始資料 (模擬資料庫)
# 包含欄位：id, part_name, description
dataset = [
    {"id": 1, "name": "Resistor 10k", "desc": "Electronic component R10K-001"},
    {"id": 2, "name": "Capacitor 47uF", "desc": "Power filter CAP-47U-F"},
    {"id": 3, "name": "Transistor NPN", "desc": "Signal amplifier TRA-NPN-99"},
    {"id": 4, "name": "Resistor 1k", "desc": "Small resistor R1K-005"},
]

# 3. 準備索引資料
# 我們將 name 與 desc 合併作為搜尋目標，並轉換成 n-gram tokens
corpus = []
for data in dataset:
    combined_text = f"{data['name']} {data['desc']}"
    # 使用 3-gram
    tokens = get_char_ngrams(combined_text, n=3)
    corpus.append(tokens)

# 4. 初始化 BM25 
bm25 = BM25Okapi(corpus)

# 5. 執行搜尋
def search(query, top_n=2):
    print(f"--- 搜尋關鍵字: '{query}' ---")
    
    # 搜尋詞也必須進行相同的 n-gram 處理
    query_tokens = get_char_ngrams(query, n=3)
    
    # 取得各筆資料的分數
    scores = bm25.get_scores(query_tokens)
    
    # 根據分數排序並回傳結果
    results = sorted(zip(range(len(dataset)), scores), key=lambda x: x[1], reverse=True)
    
    for idx, score in results[:top_n]:
        if score > 0:
            match = dataset[idx]
            print(f"【命中】 ID: {match['id']}")
            print(f" 欄位名稱: {match['name']}")
            print(f" 詳細內容: {match['desc']}")
            print(f" 相關得分: {score:.4f}\n")
        else:
            print("查無相關資料。")

# 測試：輸入稍微打錯的關鍵字 (例如把 Resistor 打成 Resister)
search("Resister 10k")

# 測試：搜尋零件編號片段
search("R1K")