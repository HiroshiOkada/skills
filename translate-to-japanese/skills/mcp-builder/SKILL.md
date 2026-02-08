---
name: mcp-builder
description: 適切に設計されたツールを通じてLLMが外部サービスと対話できるようにする高品質なMCP（Model Context Protocol）サーバーを作成するためのガイド。Python（FastMCP）またはNode/TypeScript（MCP SDK）のいずれかで外部APIまたはサービスを統合するためにMCPサーバーを構築する場合に使用します。
license: Complete terms in LICENSE.txt
---

# MCPサーバー開発ガイド

## 概要

適切に設計されたツールを通じてLLMが外部サービスと対話できるようにするMCP（Model Context Protocol）サーバーを作成します。MCPサーバーの品質は、LLMが現実世界のタスクをどれだけうまく達成できるかによって測定されます。

---

# プロセス

## 🚀 ハイレベルワークフロー

高品質なMCPサーバーの作成には、4つの主要なフェーズが含まれます：

### フェーズ1: 深い調査と計画

#### 1.1 現代のMCPデザインを理解する

**APIカバレッジ vs ワークフローツール:**
包括的なAPIエンドポイントカバレッジと専門的なワークフローツールのバランスを取ります。ワークフローツールは特定のタスクに便利であり、包括的なカバレッジはエージェントに操作を構成する柔軟性を与えます。パフォーマンスはクライアントによって異なります。基本的なツールを組み合わせるコード実行から利益を得るクライアントもあれば、より高レベルのワークフローでうまく機能するクライアントもあります。不確実な場合は、包括的なAPIカバレッジを優先してください。

**ツールの命名と発見可能性:**
明確で記述的なツール名は、エージェントが適切なツールを迅速に見つけるのに役立ちます。一貫したプレフィックス（例：`github_create_issue`, `github_list_repos`）とアクション指向の命名を使用してください。

**コンテキスト管理:**
エージェントは、簡潔なツールの説明と結果をフィルタリング/ページネーションする機能から利益を得ます。焦点を絞った関連データを返すツールを設計してください。一部のクライアントはコード実行をサポートしており、エージェントがデータを効率的にフィルタリングおよび処理するのに役立ちます。

**アクション可能なエラーメッセージ:**
エラーメッセージは、具体的な提案と次のステップでエージェントを解決策に導くべきです。

#### 1.2 MCPプロトコルドキュメントを研究する

**MCP仕様をナビゲートする:**

サイトマップから始めて関連ページを見つけます：`https://modelcontextprotocol.io/sitemap.xml`

次に、マークダウン形式のために`.md`サフィックスを持つ特定のページを取得します（例：`https://modelcontextprotocol.io/specification/draft.md`）。

レビューすべき主要ページ：
- 仕様の概要とアーキテクチャ
- トランスポートメカニズム（ストリーム可能なHTTP、stdio）
- ツール、リソース、およびプロンプト定義

#### 1.3 フレームワークドキュメントを研究する

**推奨スタック:**
- **言語**: TypeScript (高品質なSDKサポートと多くの実行環境での良好な互換性。加えて、AIモデルはTypeScriptコードの生成が得意であり、その広範な使用、静的型付け、および優れたリンティングツールの恩恵を受けます)
- **トランスポート**: リモートサーバー用のストリーム可能なHTTP、ステートレスJSONを使用（ステートフルなセッションやストリーミング応答とは対照的に、スケーリングと保守が簡単）。ローカルサーバー用のstdio。

**フレームワークドキュメントを読み込む:**
- **MCPベストプラクティス**: [📋 ベストプラクティスを表示](./reference/mcp_best_practices.md) - コアガイドライン

**TypeScript用（推奨）:**
- **TypeScript SDK**: WebFetchを使用して `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` を読み込む
- [⚡ TypeScriptガイド](./reference/node_mcp_server.md) - TypeScriptパターンと例

**Python用:**
- **Python SDK**: WebFetchを使用して `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` を読み込む
- [🐍 Pythonガイド](./reference/python_mcp_server.md) - Pythonパターンと例

#### 1.4 実装を計画する

**APIを理解する:**
サービスのAPIドキュメントをレビューして、主要なエンドポイント、認証要件、およびデータモデルを特定します。必要に応じてウェブ検索とWebFetchを使用してください。

**ツールの選択:**
包括的なAPIカバレッジを優先してください。最も一般的な操作から始めて、実装するエンドポイントをリストします。

---

### フェーズ2: 実装

#### 2.1 プロジェクト構造のセットアップ

プロジェクトのセットアップについては、言語別のガイドを参照してください：
- [⚡ TypeScriptガイド](./reference/node_mcp_server.md) - プロジェクト構造、package.json、tsconfig.json
- [🐍 Pythonガイド](./reference/python_mcp_server.md) - モジュール構成、依存関係

#### 2.2 コアインフラストラクチャの実装

共有ユーティリティを作成します：
- 認証付きAPIクライアント
- エラー処理ヘルパー
- 応答フォーマット（JSON/Markdown）
- ページネーションサポート

#### 2.3 ツールの実装

各ツールについて：

**入力スキーマ:**
- Zod (TypeScript) または Pydantic (Python) を使用
- 制約と明確な説明を含める
- フィールドの説明に例を追加

**出力スキーマ:**
- 構造化データのために可能な場合は `outputSchema` を定義
- ツール応答で `structuredContent` を使用（TypeScript SDK機能）
- クライアントがツールの出力を理解し処理するのを助ける

**ツールの説明:**
- 機能の簡潔な要約
- パラメータの説明
- 戻り値の型スキーマ

**実装:**
- I/O操作のためのAsync/await
- アクション可能なメッセージを伴う適切なエラー処理
- 該当する場合のページネーションサポート
- 最新のSDKを使用する場合、テキストコンテンツと構造化データの両方を返す

**アノテーション:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### フェーズ3: レビューとテスト

#### 3.1 コード品質

以下をレビューします：
- 重複コードなし（DRY原則）
- 一貫したエラー処理
- 完全な型カバレッジ
- 明確なツールの説明

#### 3.2 ビルドとテスト

**TypeScript:**
- `npm run build` を実行してコンパイルを確認
- MCP Inspectorでテスト: `npx @modelcontextprotocol/inspector`

**Python:**
- 構文を確認: `python -m py_compile your_server.py`
- MCP Inspectorでテスト

詳細なテストアプローチと品質チェックリストについては、言語別のガイドを参照してください。

---

### フェーズ4: 評価の作成

MCPサーバーを実装した後、その有効性をテストするための包括的な評価を作成します。

**完全な評価ガイドラインについては、[✅ 評価ガイド](./reference/evaluation.md)を読み込んでください。**

#### 4.1 評価の目的を理解する

LLMが現実的で複雑な質問に答えるためにMCPサーバーを効果的に使用できるかどうかをテストするために評価を使用します。

#### 4.2 10個の評価質問を作成する

効果的な評価を作成するために、評価ガイドで概説されているプロセスに従ってください：

1. **ツール検査**: 利用可能なツールをリストし、その機能を理解する
2. **コンテンツ探索**: 読み取り専用操作を使用して利用可能なデータを探索する
3. **質問生成**: 10個の複雑で現実的な質問を作成する
4. **回答検証**: 自分で各質問を解いて回答を検証する

#### 4.3 評価要件

各質問が以下であることを確認してください：
- **独立的**: 他の質問に依存しない
- **読み取り専用**: 非破壊的な操作のみが必要
- **複雑**: 複数のツール呼び出しと深い探索が必要
- **現実的**: 人間が気にする実際のユースケースに基づいている
- **検証可能**: 文字列比較で検証できる単一の明確な答え
- **安定的**: 答えが時間とともに変わらない

#### 4.4 出力フォーマット

この構造を持つXMLファイルを作成します：

```xml
<evaluation>
  <qa_pair>
    <question>動物のコードネームを持つAIモデルの立ち上げに関する議論を見つけてください。あるモデルはASL-X形式を使用する特定の安全指定を必要としました。斑点のある野生の猫にちなんで名付けられたモデルのために決定されていたXの数字は何ですか？</question>
    <answer>3</answer>
  </qa_pair>
<!-- その他のqa_pairs... -->
</evaluation>
```

---

# リファレンスファイル

## 📚 ドキュメントライブラリ

開発中に必要に応じてこれらのリソースを読み込んでください：

### コアMCPドキュメント（最初に読み込む）
- **MCPプロトコル**: `https://modelcontextprotocol.io/sitemap.xml` のサイトマップから始め、`.md` サフィックスを持つ特定のページを取得
- [📋 MCPベストプラクティス](./reference/mcp_best_practices.md) - 以下を含む普遍的なMCPガイドライン：
  - サーバーとツールの命名規則
  - 応答フォーマットガイドライン（JSON vs Markdown）
  - ページネーションのベストプラクティス
  - トランスポート選択（ストリーム可能なHTTP vs stdio）
  - セキュリティとエラー処理の標準

### SDKドキュメント（フェーズ1/2中に読み込む）
- **Python SDK**: `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` から取得
- **TypeScript SDK**: `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` から取得

### 言語別実装ガイド（フェーズ2中に読み込む）
- [🐍 Python実装ガイド](./reference/python_mcp_server.md) - 以下を含む完全なPython/FastMCPガイド：
  - サーバー初期化パターン
  - Pydanticモデルの例
  - `@mcp.tool` によるツール登録
  - 完全な動作例
  - 品質チェックリスト

- [⚡ TypeScript実装ガイド](./reference/node_mcp_server.md) - 以下を含む完全なTypeScriptガイド：
  - プロジェクト構造
  - Zodスキーマパターン
  - `server.registerTool` によるツール登録
  - 完全な動作例
  - 品質チェックリスト

### 評価ガイド（フェーズ4中に読み込む）
- [✅ 評価ガイド](./reference/evaluation.md) - 以下を含む完全な評価作成ガイド：
  - 質問作成ガイドライン
  - 回答検証戦略
  - XMLフォーマット仕様
  - 質問と回答の例
  - 提供されたスクリプトでの評価の実行
