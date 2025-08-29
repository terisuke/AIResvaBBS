#!/usr/bin/env python3
"""
APIコスト試算スクリプト
各APIの料金を基に、運用コストを試算
"""
import json
from typing import Dict

# 2025年8月時点の料金（USD per 1M tokens）
API_PRICING = {
    "grok": {
        "models": {
            "grok-3-mini": {"input": 0.10, "output": 0.20},
            "grok-2-latest": {"input": 5.00, "output": 10.00}
        }
    },
    "openai": {
        "models": {
            "gpt-5-mini": {"input": 0.30, "output": 1.25},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60}
        }
    },
    "anthropic": {
        "models": {
            "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
            "claude-opus-4-1-20250805": {"input": 15.00, "output": 75.00},
            "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00}
        }
    },
    "google": {
        "models": {
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30}
        }
    }
}

class CostEstimator:
    def __init__(self):
        # デフォルトモデル（フォールバックの最初のモデル）
        self.default_models = {
            "grok": "grok-3-mini",
            "openai": "gpt-5-mini",
            "anthropic": "claude-sonnet-4-20250514",
            "google": "gemini-2.5-flash"
        }
        
        # キャラクター別の使用API
        self.character_apis = {
            "Grok": "grok",
            "GPT君": "openai",
            "Claude先輩": "anthropic",
            "Gemini": "google",
            "名無しさん": "random"  # ランダムに選択
        }
        
        # 平均トークン数（推定）
        self.avg_input_tokens = 150  # プロンプト + システムプロンプト
        self.avg_output_tokens = 50  # レスポンス
    
    def calculate_post_cost(self, api_type: str, model: str = None) -> float:
        """1レスあたりのコストを計算（USD）"""
        if model is None:
            model = self.default_models.get(api_type)
        
        if api_type not in API_PRICING or model not in API_PRICING[api_type]["models"]:
            return 0.0
        
        pricing = API_PRICING[api_type]["models"][model]
        
        # コスト計算（USD）
        input_cost = (self.avg_input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.avg_output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def calculate_thread_cost(self, num_posts: int = 100) -> Dict[str, float]:
        """スレッドあたりのコストを計算"""
        costs = {}
        total_cost = 0.0
        
        # 各キャラクターの投稿割合（推定）
        character_distribution = {
            "Grok": 0.15,      # スレ主なので最初は多め
            "GPT君": 0.20,
            "Claude先輩": 0.20,
            "Gemini": 0.20,
            "名無しさん": 0.25  # 少し多め
        }
        
        for character, ratio in character_distribution.items():
            posts_by_character = int(num_posts * ratio)
            
            if character == "名無しさん":
                # 名無しさんは3つのAPIをランダムに使用
                api_cost = 0
                for api in ["openai", "anthropic", "google"]:
                    api_cost += self.calculate_post_cost(api) * (posts_by_character / 3)
                costs[character] = api_cost
            else:
                api_type = self.character_apis[character]
                post_cost = self.calculate_post_cost(api_type)
                costs[character] = post_cost * posts_by_character
            
            total_cost += costs[character]
        
        costs["TOTAL"] = total_cost
        return costs
    
    def generate_report(self):
        """コスト試算レポートを生成"""
        report = []
        report.append("=" * 70)
        report.append("API COST ESTIMATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # 1レスあたりのコスト
        report.append("【1レスあたりのAPIコスト】")
        report.append(f"（入力: {self.avg_input_tokens} tokens, 出力: {self.avg_output_tokens} tokens）")
        report.append("")
        
        for api_type, model in self.default_models.items():
            cost = self.calculate_post_cost(api_type, model)
            report.append(f"  {api_type.upper()} ({model}):")
            report.append(f"    ${cost:.6f} per post")
            report.append(f"    ${cost * 1000:.3f} per 1,000 posts")
        report.append("")
        
        # スレッドあたりのコスト
        report.append("【スレッドあたりのコスト】")
        
        for thread_size in [100, 500, 1000]:
            report.append(f"\n  ◆ {thread_size}レススレッド:")
            costs = self.calculate_thread_cost(thread_size)
            
            for character, cost in costs.items():
                if character != "TOTAL":
                    report.append(f"    {character}: ${cost:.4f}")
            report.append(f"    {'─' * 20}")
            report.append(f"    合計: ${costs['TOTAL']:.4f}")
        
        report.append("")
        
        # 日間・月間コスト試算
        report.append("【運用コスト試算】")
        report.append("（想定: 100レススレッド）")
        report.append("")
        
        thread_cost = self.calculate_thread_cost(100)["TOTAL"]
        
        scenarios = [
            ("低利用", 10, "1日10スレッド"),
            ("中利用", 50, "1日50スレッド"),
            ("高利用", 200, "1日200スレッド")
        ]
        
        for scenario_name, daily_threads, description in scenarios:
            daily_cost = thread_cost * daily_threads
            monthly_cost = daily_cost * 30
            
            report.append(f"  ◆ {scenario_name}シナリオ（{description}）:")
            report.append(f"    日間コスト: ${daily_cost:.2f}")
            report.append(f"    月間コスト: ${monthly_cost:.2f}")
            report.append(f"    年間コスト: ${monthly_cost * 12:.2f}")
            report.append("")
        
        # 予算内チェック
        report.append("【月額$50予算での運用可能量】")
        max_threads = 50 / thread_cost
        max_daily = max_threads / 30
        report.append(f"  最大スレッド数: {max_threads:.0f} スレッド/月")
        report.append(f"  1日あたり: {max_daily:.1f} スレッド")
        report.append("")
        
        # コスト削減提案
        report.append("【コスト削減提案】")
        report.append("  1. より安価なモデルの優先使用:")
        report.append("     - OpenAI: gpt-4o-mini ($0.15/$0.60)")
        report.append("     - Gemini: gemini-1.5-flash ($0.075/$0.30)")
        report.append("  2. レス文字数の最適化（短文を基本に）")
        report.append("  3. キャッシュ機能の実装（同じ話題の再利用）")
        report.append("  4. オフピーク時間帯の活用")
        report.append("  5. 無料枠の最大活用:")
        report.append("     - Google: 月間無料枠あり")
        report.append("     - OpenAI: 初回クレジットの活用")
        report.append("")
        
        # 警告事項
        report.append("【⚠️ 注意事項】")
        report.append("  - 上記は推定値です。実際の使用量により変動します")
        report.append("  - APIの料金は変更される可能性があります")
        report.append("  - エラーリトライによる追加コストが発生する可能性があります")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def save_detailed_data(self):
        """詳細データをJSON形式で保存"""
        data = {
            "pricing": API_PRICING,
            "default_models": self.default_models,
            "token_estimates": {
                "avg_input_tokens": self.avg_input_tokens,
                "avg_output_tokens": self.avg_output_tokens
            },
            "cost_per_post": {},
            "thread_costs": {}
        }
        
        # 各APIのコスト
        for api_type, model in self.default_models.items():
            data["cost_per_post"][api_type] = {
                "model": model,
                "cost_usd": self.calculate_post_cost(api_type, model)
            }
        
        # スレッドサイズ別コスト
        for size in [100, 500, 1000]:
            data["thread_costs"][f"{size}_posts"] = self.calculate_thread_cost(size)
        
        with open("cost_estimation_data.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        return data

def main():
    """メイン処理"""
    estimator = CostEstimator()
    
    # レポート生成
    report = estimator.generate_report()
    
    # ファイルに保存
    with open("cost_estimation_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    
    # コンソールに表示
    print(report)
    
    # 詳細データを保存
    estimator.save_detailed_data()
    
    print("\nFiles saved:")
    print("  - cost_estimation_report.txt")
    print("  - cost_estimation_data.json")

if __name__ == "__main__":
    main()