---
name: webapp-testing
description: Playwrightを使用してローカルWebアプリケーションと対話し、テストするためのツールキット。フロントエンド機能の検証、UI動作のデバッグ、ブラウザのスクリーンショットのキャプチャ、およびブラウザログの表示をサポートします。
license: Complete terms in LICENSE.txt
---

# Webアプリケーションテスト

ローカルWebアプリケーションをテストするには、ネイティブのPython Playwrightスクリプトを作成してください。

**利用可能なヘルパースクリプト**:
- `scripts/with_server.py` - サーバーライフサイクルを管理します（複数のサーバーをサポート）

**常に最初に `--help` でスクリプトを実行して**使用法を確認してください。最初にスクリプトを実行してみて、カスタマイズされたソリューションが絶対に必要であるとわかるまで、ソースを読まないでください。これらのスクリプトは非常に大きくなる可能性があるため、コンテキストウィンドウを汚染します。これらは、コンテキストウィンドウに取り込むのではなく、ブラックボックススクリプトとして直接呼び出されるために存在します。

## 決定木: アプローチの選択

```
ユーザータスク → 静的HTMLですか？
    ├─ はい → セレクタを特定するためにHTMLファイルを直接読む
    │         ├─ 成功 → セレクタを使用してPlaywrightスクリプトを書く
    │         └─ 失敗/不完全 → 動的として扱う（以下）
    │
    └─ いいえ（動的Webアプリ） → サーバーはすでに実行中ですか？
        ├─ いいえ → 実行: python scripts/with_server.py --help
        │          その後、ヘルパーを使用 + 簡素化されたPlaywrightスクリプトを書く
        │
        └─ はい → 偵察してから行動:
            1. ナビゲートして networkidle を待つ
            2. スクリーンショットを撮るかDOMを検査する
            3. レンダリングされた状態からセレクタを特定する
            4. 発見されたセレクタでアクションを実行する
```

## 例: with_server.py の使用

サーバーを起動するには、最初に `--help` を実行し、その後ヘルパーを使用してください：

**シングルサーバー:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**マルチサーバー（例：バックエンド + フロントエンド）:**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

自動化スクリプトを作成するには、Playwrightロジックのみを含めます（サーバーは自動的に管理されます）：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # 常にヘッドレスモードでchromiumを起動
    page = browser.new_page()
    page.goto('http://localhost:5173') # サーバーはすでに実行中で準備完了
    page.wait_for_load_state('networkidle') # 重要: JSが実行されるのを待つ
    # ... あなたの自動化ロジック
    browser.close()
```

## 偵察してから行動パターン

1. **レンダリングされたDOMを検査する**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. 検査結果から**セレクタを特定する**

3. 発見されたセレクタを使用して**アクションを実行する**

## 一般的な落とし穴

❌ 動的アプリで `networkidle` を待つ前にDOMを検査**しない**でください
✅ 検査の前に `page.wait_for_load_state('networkidle')` を**待って**ください

## ベストプラクティス

- **バンドルされたスクリプトをブラックボックスとして使用する** - タスクを達成するために、`scripts/` で利用可能なスクリプトの1つが役立つかどうかを検討してください。これらのスクリプトは、コンテキストウィンドウを散らかすことなく、一般的で複雑なワークフローを確実に処理します。使用法を確認するには `--help` を使用し、直接呼び出してください。
- 同期スクリプトには `sync_playwright()` を使用する
- 完了したら常にブラウザを閉じる
- 記述的なセレクタを使用する: `text=`, `role=`, CSSセレクタ, またはID
- 適切な待機を追加する: `page.wait_for_selector()` または `page.wait_for_timeout()`

## リファレンスファイル

- **examples/** - 一般的なパターンを示す例:
  - `element_discovery.py` - ページ上のボタン、リンク、入力を発見する
  - `static_html_automation.py` - ローカルHTMLに file:// URL を使用する
  - `console_logging.py` - 自動化中にコンソールログをキャプチャする
