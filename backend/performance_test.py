#!/usr/bin/env python3
"""
APIパフォーマンス測定スクリプト
各APIの応答時間を測定し、ボトルネックを特定
"""
import asyncio
import time
import statistics
from typing import Dict, List
from ai_clients import AIClientFactory
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTester:
    def __init__(self):
        self.results: Dict[str, List[float]] = {
            "grok": [],
            "openai": [],
            "anthropic": [],
            "google": []
        }
        self.test_prompts = [
            "こんにちは、調子はどう？",
            "プログラミングについて語ってください",
            "今日の天気について一言",
            "AIの未来についてどう思う？",
            "好きな食べ物は何？"
        ]
    
    async def test_api(self, api_type: str, iterations: int = 5):
        """特定のAPIをテスト"""
        logger.info(f"Testing {api_type} API...")
        
        client = None
        if api_type == "grok":
            from ai_clients import GrokClient
            client = GrokClient()
        elif api_type == "openai":
            from ai_clients import OpenAIClient
            client = OpenAIClient()
        elif api_type == "anthropic":
            from ai_clients import AnthropicClient
            client = AnthropicClient()
        elif api_type == "google":
            from ai_clients import GeminiClient
            client = GeminiClient()
        
        if not client:
            logger.error(f"Unknown API type: {api_type}")
            return
        
        for i in range(iterations):
            prompt = self.test_prompts[i % len(self.test_prompts)]
            
            try:
                start_time = time.time()
                response = await client.generate_response(
                    prompt=prompt,
                    system_prompt="あなたは2ch掲示板の住人です。短く返答してください。",
                    max_tokens=50
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                self.results[api_type].append(response_time)
                
                logger.info(f"  [{api_type}] Test {i+1}/{iterations}: {response_time:.2f}s")
                logger.debug(f"    Response: {response[:50]}...")
                
                # API負荷を避けるため少し待機
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"  [{api_type}] Error in test {i+1}: {str(e)}")
                self.results[api_type].append(-1)  # エラーの場合
    
    async def run_tests(self):
        """全APIをテスト"""
        logger.info("=== Performance Testing Started ===\n")
        
        # 各APIを順番にテスト
        for api_type in ["grok", "openai", "anthropic", "google"]:
            await self.test_api(api_type, iterations=5)
            await asyncio.sleep(2)  # API間で待機
        
        logger.info("\n=== Performance Testing Completed ===")
    
    def generate_report(self):
        """パフォーマンスレポートを生成"""
        report = []
        report.append("=" * 60)
        report.append("API PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        total_times = []
        
        for api_type, times in self.results.items():
            valid_times = [t for t in times if t > 0]  # エラーを除外
            
            if valid_times:
                avg_time = statistics.mean(valid_times)
                min_time = min(valid_times)
                max_time = max(valid_times)
                median_time = statistics.median(valid_times)
                
                total_times.extend(valid_times)
                
                report.append(f"【{api_type.upper()} API】")
                report.append(f"  Average: {avg_time:.3f}s")
                report.append(f"  Median:  {median_time:.3f}s")
                report.append(f"  Min:     {min_time:.3f}s")
                report.append(f"  Max:     {max_time:.3f}s")
                report.append(f"  Success: {len(valid_times)}/{len(times)}")
                report.append("")
            else:
                report.append(f"【{api_type.upper()} API】")
                report.append(f"  ❌ All tests failed")
                report.append("")
        
        # 全体統計
        if total_times:
            overall_avg = statistics.mean(total_times)
            report.append("【OVERALL STATISTICS】")
            report.append(f"  Average response time: {overall_avg:.3f}s")
            report.append(f"  Target: < 0.500s")
            report.append(f"  Status: {'✅ PASS' if overall_avg < 0.5 else '❌ NEEDS IMPROVEMENT'}")
            report.append("")
            
            # ボトルネック分析
            report.append("【BOTTLENECK ANALYSIS】")
            slowest_api = max(self.results.items(), 
                            key=lambda x: statistics.mean([t for t in x[1] if t > 0]) if any(t > 0 for t in x[1]) else 0)
            fastest_api = min(self.results.items(), 
                            key=lambda x: statistics.mean([t for t in x[1] if t > 0]) if any(t > 0 for t in x[1]) else float('inf'))
            
            report.append(f"  Slowest API: {slowest_api[0].upper()}")
            report.append(f"  Fastest API: {fastest_api[0].upper()}")
            report.append("")
            
            # 改善提案
            report.append("【IMPROVEMENT RECOMMENDATIONS】")
            if overall_avg > 0.5:
                report.append("  1. Consider using faster models:")
                report.append("     - OpenAI: Use gpt-4o-mini instead of gpt-4o")
                report.append("     - Anthropic: Use claude-3-haiku for speed")
                report.append("     - Gemini: Use gemini-1.5-flash")
                report.append("  2. Implement response streaming for better UX")
                report.append("  3. Add caching for common responses")
                report.append("  4. Consider parallel API calls where possible")
            else:
                report.append("  ✅ Performance is within target range")
                report.append("  - Consider implementing caching for further improvement")
                report.append("  - Monitor performance during peak usage")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename="performance_report.txt"):
        """レポートをファイルに保存"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {filename}")
        return report

async def main():
    """メイン処理"""
    tester = PerformanceTester()
    
    # テスト実行
    await tester.run_tests()
    
    # レポート生成と表示
    report = tester.save_report()
    print("\n" + report)
    
    # 詳細データをJSONで保存
    import json
    with open("performance_data.json", 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    logger.info("Detailed data saved to performance_data.json")

if __name__ == "__main__":
    asyncio.run(main())