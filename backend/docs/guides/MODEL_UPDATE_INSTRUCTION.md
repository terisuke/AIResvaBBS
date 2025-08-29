# 🔄 モデル更新指示書 - 最新AIモデルへのアップグレード

## 📅 発行日: 2025年8月29日

### 🎯 対象: バックエンドチーム

## 1. 更新が必要な理由

現在の実装は正常に動作していますが、使用しているAIモデルが古いバージョンです。
最新モデルに更新することで、以下のメリットが得られます：

- **性能向上**: より高品質なレスポンス生成
- **速度改善**: 推論速度の向上
- **コスト最適化**: 新モデルは効率的な価格設定

## 2. 更新対象ファイル

**`backend/ai_clients.py`** の以下の行を更新してください：

### 現在のコード（Line 58, 88, 108, 123）:

```python
# Line 58 (GrokClient)
chat = self.client.chat.create(model="grok-2-latest")

# Line 88 (OpenAIClient) 
model="gpt-4o-mini",

# Line 108 (AnthropicClient)
model="claude-3-haiku-20240307",

# Line 123 (GeminiClient)
self.model = genai.GenerativeModel('gemini-1.5-flash')
```

### 更新後のコード:

```python
# Line 58 (GrokClient) - 最新のGrok Betaモデルを使用
chat = self.client.chat.create(model="grok-beta")
# 注: もし "grok-3-mini-latest" が利用可能な場合はそちらを使用

# Line 88 (OpenAIClient) - GPT-5-miniに更新
model="gpt-5-mini",

# Line 108 (AnthropicClient) - Claude Sonnet 4に更新
model="claude-sonnet-4",
# または最新版: "claude-opus-4-1-20250805" (より高性能だが高コスト)

# Line 123 (GeminiClient) - Gemini 2.5 Flashに更新
self.model = genai.GenerativeModel('gemini-2.5-flash')
```

## 3. 実装手順

### Step 1: バックアップ作成
```bash
cp backend/ai_clients.py backend/ai_clients.py.backup
```

### Step 2: モデル名の更新
上記の変更を `backend/ai_clients.py` に適用

### Step 3: APIテスト実行
```bash
cd backend
python test_api.py
```

### Step 4: 動作確認
```bash
# サーバー再起動
uvicorn main:app --reload --port 8000

# ブラウザで http://localhost:3000 にアクセスし、
# 各キャラクターが正常に発言することを確認
```

## 4. モデル選択の詳細

### Grok API
- **推奨**: `grok-beta` (最新の安定版)
- **代替**: `grok-3-mini-latest` (もし利用可能な場合)
- xAI SDKのドキュメントで最新モデル名を確認してください

### OpenAI API
- **推奨**: `gpt-5-mini` (コスト効率が良い)
- **代替**: `gpt-5` (より高性能だが高コスト)
- **参考**: GPT-5は2025年8月7日にリリースされた最新モデルファミリー

### Anthropic API
- **推奨**: `claude-sonnet-4` (バランスが良い)
- **代替**: `claude-opus-4-1-20250805` (最高性能、2025年8月5日リリース)
- **注**: claude-3-haikuは旧世代モデルです

### Google Gemini API
- **推奨**: `gemini-2.5-flash` (高速・低コスト)
- **代替**: `gemini-2.5-pro` (より高性能)

## 5. 注意事項

### ⚠️ API互換性の確認
各APIプロバイダーのドキュメントを確認し、モデル名が正しいことを確認してください：

- [OpenAI Models](https://platform.openai.com/docs/models)
- [Anthropic Models](https://docs.anthropic.com/en/docs/about-claude/models)
- [Google AI Models](https://ai.google.dev/gemini-api/docs/models)
- [xAI Documentation](https://x.ai/api)

### 💰 コスト影響
新モデルは性能が向上していますが、料金体系が異なる場合があります：

| モデル | 入力料金 | 出力料金 |
|-------|---------|---------|
| gpt-5-mini | $0.30/1M tokens | $1.25/1M tokens |
| claude-sonnet-4 | $3/1M tokens | $15/1M tokens |
| gemini-2.5-flash | $0.075/1M tokens | $0.30/1M tokens |

### 🔧 フォールバック設定
もし新モデルでエラーが発生した場合、以下のフォールバック設定を使用：

```python
# backend/ai_clients.py に追加
MODEL_FALLBACKS = {
    "grok": ["grok-beta", "grok-2-latest"],
    "openai": ["gpt-5-mini", "gpt-4o-mini"],
    "anthropic": ["claude-sonnet-4", "claude-3-5-sonnet-20240620"],
    "google": ["gemini-2.5-flash", "gemini-1.5-flash"]
}
```

## 6. テストチェックリスト

更新後、以下のテストを実行してください：

- [ ] 各APIの接続テスト（test_api.py）
- [ ] Grokがスレ主として正常に発言
- [ ] GPT君が丁寧な口調で返答
- [ ] Claude先輩が論理的に分析
- [ ] Geminiが創造的な視点を追加
- [ ] 名無しさんがランダムにAPI選択
- [ ] レス生成速度が2秒以内
- [ ] エラーハンドリングが機能

## 7. 完了報告

更新完了後、以下の情報をSlackで報告してください：

```
【モデル更新完了】
✅ 更新したモデル:
- Grok: [使用したモデル名]
- OpenAI: gpt-5-mini
- Anthropic: [使用したモデル名]
- Gemini: [使用したモデル名]

✅ テスト結果:
- 全API接続: OK/NG
- レス生成: OK/NG
- 平均応答時間: X.X秒

📝 備考:
[あれば記載]
```

---

**質問がある場合**: Slack #ai-resuba-dev チャンネルでお問い合わせください。

**期限**: 本日中に更新をお願いします。

---

*プロダクトマネジメントチーム*
*2025年8月29日*
