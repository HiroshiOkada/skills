---
name: xlsx
description: "スプレッドシートファイルが主要な入力または出力である場合はいつでも、このスキルを使用してください。これには、ユーザーが以下のことを望むあらゆるタスクが含まれます：既存の .xlsx, .xlsm, .csv, または .tsv ファイルを開く、読む、編集する、または修正する（例：列の追加、数式の計算、フォーマット、チャート作成、乱雑なデータのクリーニング）；スクラッチから、または他のデータソースから新しいスプレッドシートを作成する；または表形式のファイル形式間で変換する。特に、ユーザーがスプレッドシートファイルを名前またはパスで参照し（「ダウンロードにあるxlsx」のようにカジュアルであっても）、それに対して何かを行うか、それから何かを生成することを望む場合にトリガーします。また、乱雑な表形式データファイル（不正な行、間違ったヘッダー、ジャンクデータ）を適切なスプレッドシートにクリーニングまたは再構築する場合にもトリガーします。成果物はスプレッドシートファイルでなければなりません。表形式データが含まれていても、主要な成果物がWord文書、HTMLレポート、スタンドアロンPythonスクリプト、データベースパイプライン、またはGoogle Sheets API統合である場合はトリガーしないでください。"
license: Proprietary. LICENSE.txt has complete terms
---

# 出力の要件

## すべてのExcelファイル

### 専門的なフォント
- ユーザーから別の指示がない限り、すべての成果物に一貫した専門的なフォント（例：Arial, Times New Roman）を使用してください

### ゼロ数式エラー
- すべてのExcelモデルは、ゼロ数式エラー（#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?）で提供されなければなりません

### 既存のテンプレートの保持（テンプレート更新時）
- ファイルを変更するときは、既存のフォーマット、スタイル、および規則を研究し、正確に一致させてください
- 確立されたパターンを持つファイルに標準化されたフォーマットを押し付けないでください
- 既存のテンプレート規則は常にこれらのガイドラインをオーバーライドします

## 財務モデル

### 色分け基準
ユーザーまたは既存のテンプレートによって特に述べられていない限り

#### 業界標準の色規則
- **青いテキスト (RGB: 0,0,255)**: ハードコードされた入力、およびシナリオのためにユーザーが変更する数値
- **黒いテキスト (RGB: 0,0,0)**: すべての数式と計算
- **緑のテキスト (RGB: 0,128,0)**: 同じワークブック内の他のワークシートからのリンク
- **赤いテキスト (RGB: 255,0,0)**: 他のファイルへの外部リンク
- **黄色の背景 (RGB: 255,255,0)**: 注意が必要な主要な仮定または更新が必要なセル

### 数値フォーマット基準

#### 必須フォーマットルール
- **年**: テキスト文字列としてフォーマット（例："2,024" ではなく "2024"）
- **通貨**: $#,##0 フォーマットを使用；ヘッダーで常に単位を指定（"Revenue ($mm)"）
- **ゼロ**: パーセンテージを含め、すべてのゼロを "-" にするために数値フォーマットを使用（例："$#,##0;($#,##0);-"）
- **パーセンテージ**: 0.0% フォーマット（小数点1桁）をデフォルトにする
- **倍率**: バリュエーション倍率（EV/EBITDA, P/E）には 0.0x としてフォーマット
- **負の数**: マイナス -123 ではなく括弧 (123) を使用

### 数式構築ルール

#### 仮定の配置
- すべての仮定（成長率、マージン、倍率など）を別々の仮定セルに配置してください
- 数式ではハードコードされた値の代わりにセル参照を使用してください
- 例：=B5*1.05 ではなく =B5*(1+$B$6) を使用

#### 数式エラー防止
- すべてのセル参照が正しいことを確認してください
- 範囲内のオフバイワンエラーをチェックしてください
- すべての予測期間で一貫した数式を確認してください
- エッジケース（ゼロ値、負の数）でテストしてください
- 意図しない循環参照がないことを確認してください

#### ハードコードのドキュメント要件
- コメントするか、そばのセルに（テーブルの終わりの場合）。フォーマット: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"
- 例:
  - "Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"
  - "Source: Company 10-Q, Q2 2025, Exhibit 99.1, [SEC EDGAR URL]"
  - "Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"
  - "Source: FactSet, 8/20/2025, Consensus Estimates Screen"

# XLSX 作成、編集、および分析

## 概要

ユーザーは .xlsx ファイルのコンテンツを作成、編集、または分析するように求める場合があります。タスクに応じて異なるツールとワークフローが利用可能です。

## 重要な要件

**数式再計算のためにLibreOfficeが必要**: `scripts/recalc.py` スクリプトを使用して数式値を再計算するために、LibreOfficeがインストールされていると想定できます。スクリプトは最初の実行時にLibreOfficeを自動的に構成します（Unixソケットが制限されているサンドボックス環境を含む）。

## データの読み取りと分析

### pandasによるデータ分析
データ分析、視覚化、および基本操作には、強力なデータ操作機能を提供する **pandas** を使用してください：

```python
import pandas as pd

# Excelを読む
df = pd.read_excel('file.xlsx')  # デフォルト: 最初のシート
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # すべてのシートをdictとして

# 分析
df.head()      # データプレビュー
df.info()      # 列情報
df.describe()  # 統計

# Excelを書く
df.to_excel('output.xlsx', index=False)
```

## Excelファイルワークフロー

## 重要: ハードコードされた値ではなく数式を使用する

**Pythonで値を計算してハードコードするのではなく、常にExcelの数式を使用してください。** これにより、スプレッドシートが動的で更新可能な状態に保たれます。

### ❌ 間違い - 計算された値のハードコード
```python
# 悪い: Pythonで計算して結果をハードコード
total = df['Sales'].sum()
sheet['B10'] = total  # 5000をハードコード

# 悪い: Pythonで成長率を計算
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # 0.15をハードコード

# 悪い: 平均のためのPython計算
avg = sum(values) / len(values)
sheet['D20'] = avg  # 42.5をハードコード
```

### ✅ 正解 - Excel数式の使用
```python
# 良い: Excelに合計を計算させる
sheet['B10'] = '=SUM(B2:B9)'

# 良い: Excel数式としての成長率
sheet['C5'] = '=(C4-C2)/C2'

# 良い: Excel関数を使用した平均
sheet['D20'] = '=AVERAGE(D2:D19)'
```

これはすべての計算に適用されます - 合計、パーセンテージ、比率、差など。ソースデータが変更されたときにスプレッドシートが再計算できる必要があります。

## 一般的なワークフロー
1. **ツールを選択**: データにはpandas、数式/フォーマットにはopenpyxl
2. **作成/ロード**: 新しいワークブックを作成するか既存のファイルをロード
3. **変更**: データ、数式、およびフォーマットを追加/編集
4. **保存**: ファイルに書き込み
5. **数式を再計算（数式を使用する場合は必須）**: scripts/recalc.py スクリプトを使用
   ```bash
   python scripts/recalc.py output.xlsx
   ```
6. **エラーを確認して修正**:
   - スクリプトはエラー詳細を含むJSONを返します
   - `status` が `errors_found` の場合、特定のエラータイプと場所について `error_summary` を確認してください
   - 特定されたエラーを修正し、再度再計算してください
   - 修正すべき一般的なエラー:
     - `#REF!`: 無効なセル参照
     - `#DIV/0!`: ゼロ除算
     - `#VALUE!`: 数式内の間違ったデータ型
     - `#NAME?`: 認識されない数式名

### 新しいExcelファイルの作成

```python
# 数式とフォーマットにopenpyxlを使用
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# データ追加
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# 数式追加
sheet['B2'] = '=SUM(A1:A10)'

# フォーマット
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# 列幅
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### 既存のExcelファイルの編集

```python
# 数式とフォーマットを保持するためにopenpyxlを使用
from openpyxl import load_workbook

# 既存ファイルをロード
wb = load_workbook('existing.xlsx')
sheet = wb.active  # または特定のシートのために wb['SheetName']

# 複数のシートを扱う
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# セルを変更
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # 位置2に行を挿入
sheet.delete_cols(3)  # 列3を削除

# 新しいシートを追加
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## 数式の再計算

openpyxlで作成または変更されたExcelファイルには、文字列としての数式が含まれていますが、計算された値は含まれていません。数式を再計算するには、提供された `scripts/recalc.py` スクリプトを使用してください：

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

例:
```bash
python scripts/recalc.py output.xlsx 30
```

スクリプトは：
- 最初の実行時にLibreOfficeマクロを自動的にセットアップします
- すべてのシートのすべての数式を再計算します
- すべてのセルをスキャンしてExcelエラー（#REF!, #DIV/0! など）を確認します
- 詳細なエラーの場所とカウントを含むJSONを返します
- LinuxとmacOSの両方で動作します

## 数式検証チェックリスト

数式が正しく機能することを確認するためのクイックチェック：

### 必須検証
- [ ] **2-3のサンプル参照をテスト**: フルモデルを構築する前に正しい値を引いているか確認
- [ ] **列マッピング**: Excel列が一致することを確認（例：列64 = BL, BKではない）
- [ ] **行オフセット**: Excel行は1インデックスであることを覚えておく（DataFrame行5 = Excel行6）

### 一般的な落とし穴
- [ ] **NaN処理**: `pd.notna()` でnull値を確認
- [ ] **右端の列**: FYデータはしばしば列50+にある
- [ ] **複数の一致**: 最初だけでなくすべての出現を検索
- [ ] **ゼロ除算**: 数式で `/` を使用する前に分母を確認 (#DIV/0!)
- [ ] **間違った参照**: すべてのセル参照が意図したセルを指しているか確認 (#REF!)
- [ ] **クロスシート参照**: シートをリンクするために正しい形式 (Sheet1!A1) を使用

### 数式テスト戦略
- [ ] **小さく始める**: 広く適用する前に2-3のセルで数式をテスト
- [ ] **依存関係を確認**: 数式で参照されるすべてのセルが存在することを確認
- [ ] **エッジケースをテスト**: ゼロ、負、および非常に大きな値を含める

### scripts/recalc.py 出力の解釈
スクリプトはエラー詳細を含むJSONを返します：
```json
{
  "status": "success",           // または "errors_found"
  "total_errors": 0,              // 総エラー数
  "total_formulas": 42,           // ファイル内の数式数
  "error_summary": {              // エラーが見つかった場合のみ存在
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## ベストプラクティス

### ライブラリ選択
- **pandas**: データ分析、一括操作、および単純なデータエクスポートに最適
- **openpyxl**: 複雑なフォーマット、数式、およびExcel固有の機能に最適

### openpyxlでの作業
- セルインデックスは1ベースです（row=1, column=1 はセルA1を指します）
- 計算された値を読むには `data_only=True` を使用します：`load_workbook('file.xlsx', data_only=True)`
- **警告**: `data_only=True` で開いて保存すると、数式は値に置き換えられ、永久に失われます
- 大きなファイルの場合：読み取りには `read_only=True`、書き込みには `write_only=True` を使用してください
- 数式は保持されますが評価されません - 値を更新するには scripts/recalc.py を使用してください

### pandasでの作業
- 推論の問題を避けるためにデータ型を指定します：`pd.read_excel('file.xlsx', dtype={'id': str})`
- 大きなファイルの場合、特定の列を読みます：`pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- 日付を適切に処理します：`pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## コードスタイルガイドライン
**重要**: Excel操作用のPythonコードを生成する場合：
- 不要なコメントなしで、最小限で簡潔なPythonコードを書いてください
- 冗長な変数名と冗長な操作を避けてください
- 不要なprintステートメントを避けてください

**Excelファイル自体について**:
- 複雑な数式や重要な仮定を持つセルにコメントを追加してください
- ハードコードされた値のデータソースを文書化してください
- 主要な計算とモデルセクションのメモを含めてください
