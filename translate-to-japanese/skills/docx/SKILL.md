---
name: docx
description: "ユーザーがWord文書（.docxファイル）を作成、読み取り、編集、または操作したい場合はいつでもこのスキルを使用します。トリガーには、「Word doc」、「word document」、「.docx」、または目次、見出し、ページ番号、またはレターヘッドのようなフォーマットを持つプロフェッショナルな文書を作成する要求が含まれます。また、.docxファイルからコンテンツを抽出または再編成したり、ドキュメントに画像を挿入または置換したり、Wordファイルで検索と置換を実行したり、変更履歴やコメントを操作したり、コンテンツを洗練されたWordドキュメントに変換したりする場合にも使用します。ユーザーが「レポート」、「メモ」、「手紙」、「テンプレート」、またはWordまたは.docxファイルとしての同様の成果物を求める場合、このスキルを使用します。PDF、スプレッドシート、Googleドキュメント、またはドキュメント生成に関係のない一般的なコーディングタスクには使用しないでください。"
license: Proprietary. LICENSE.txt has complete terms
---

# DOCX 作成、編集、および分析

## 概要

.docxファイルはXMLファイルを含むZIPアーカイブです。

## クイックリファレンス

| タスク | アプローチ |
|------|----------|
| コンテンツの読み取り/分析 | `pandoc` または生のXMLのために解凍 |
| 新しいドキュメントの作成 | `docx-js` を使用 - 下記の「新しいドキュメントの作成」を参照 |
| 既存のドキュメントの編集 | 解凍 → XML編集 → 再パック - 下記の「既存のドキュメントの編集」を参照 |

### .doc から .docx への変換

レガシーな `.doc` ファイルは編集前に変換する必要があります：

```bash
python scripts/office/soffice.py --headless --convert-to docx document.doc
```

### コンテンツの読み取り

```bash
# 変更履歴付きのテキスト抽出
pandoc --track-changes=all document.docx -o output.md

# 生のXMLアクセス
python scripts/office/unpack.py document.docx unpacked/
```

### 画像への変換

```bash
python scripts/office/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

### 変更履歴の承認

すべての変更履歴が承認されたクリーンなドキュメントを作成するには（LibreOfficeが必要です）：

```bash
python scripts/accept_changes.py input.docx output.docx
```

---

## 新しいドキュメントの作成

JavaScriptで.docxファイルを生成し、検証します。インストール：`npm install -g docx`

### セットアップ
```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak } = require('docx');

const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer));
```

### 検証
ファイル作成後、検証します。検証に失敗した場合、解凍し、XMLを修正し、再パックします。
```bash
python scripts/office/validate.py doc.docx
```

### ページサイズ

```javascript
// 重要: docx-jsのデフォルトはA4であり、USレターではありません
// 一貫した結果のために常にページサイズを明示的に設定してください
sections: [{
  properties: {
    page: {
      size: {
        width: 12240,   // 8.5インチ (DXA単位)
        height: 15840   // 11インチ (DXA単位)
      },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1インチのマージン
    }
  },
  children: [/* content */]
}]
```

**一般的なページサイズ (DXA単位, 1440 DXA = 1インチ):**

| 用紙 | 幅 | 高さ | コンテンツ幅 (1" マージン) |
|-------|-------|--------|---------------------------|
| US Letter | 12,240 | 15,840 | 9,360 |
| A4 (default) | 11,906 | 16,838 | 9,026 |

**横向き (Landscape):** docx-jsは内部で幅/高さを入れ替えるため、縦向きの寸法を渡し、入れ替えを処理させます：
```javascript
size: {
  width: 12240,   // 短い辺を幅として渡す
  height: 15840,  // 長い辺を高さとして渡す
  orientation: PageOrientation.LANDSCAPE  // docx-jsがXMLでそれらを入れ替えます
},
// コンテンツ幅 = 15840 - 左マージン - 右マージン (長い辺を使用)
```

### スタイル (組み込み見出しの上書き)

Arialをデフォルトフォントとして使用します（普遍的にサポートされています）。読みやすさのためにタイトルは黒のままにします。

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 12pt default
    paragraphStyles: [
      // 重要: 組み込みスタイルを上書きするには正確なIDを使用してください
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }, // TOCにはoutlineLevelが必要
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Title")] }),
    ]
  }]
});
```

### リスト (Unicodeビュレットを決して使用しない)

```javascript
// ❌ 間違い - ビュレット文字を手動で挿入しないでください
new Paragraph({ children: [new TextRun("• Item")] })  // BAD
new Paragraph({ children: [new TextRun("\u2022 Item")] })  // BAD

// ✅ 正解 - LevelFormat.BULLETでナンバリング設定を使用してください
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Bullet item")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 },
        children: [new TextRun("Numbered item")] }),
    ]
  }]
});

// ⚠️ 各参照は独立したナンバリングを作成します
// 同じ参照 = 続く (1,2,3 その後 4,5,6)
// 異なる参照 = 再開する (1,2,3 その後 1,2,3)
```

### テーブル

**重要: テーブルには二重の幅が必要です** - テーブルの `columnWidths` と各セルの `width` の両方を設定します。両方がないと、一部のプラットフォームでテーブルが正しくレンダリングされません。

```javascript
// 重要: 一貫したレンダリングのために常にテーブル幅を設定してください
// 重要: 黒い背景を防ぐためにShadingType.CLEAR（SOLIDではない）を使用してください
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  width: { size: 9360, type: WidthType.DXA }, // 常にDXAを使用（パーセンテージはGoogle Docsで壊れます）
  columnWidths: [4680, 4680], // テーブル幅の合計と一致する必要があります (DXA: 1440 = 1インチ)
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: 4680, type: WidthType.DXA }, // 各セルにも設定
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, // CLEARを使用、SOLIDではない
          margins: { top: 80, bottom: 80, left: 120, right: 120 }, // セルパディング（内部、幅に追加されない）
          children: [new Paragraph({ children: [new TextRun("Cell")] })]
        })
      ]
    })
  ]
})
```

**テーブル幅の計算:**

常に `WidthType.DXA` を使用してください - `WidthType.PERCENTAGE` はGoogle Docsで壊れます。

```javascript
// テーブル幅 = columnWidthsの合計 = コンテンツ幅
// US Letter 1インチマージン: 12240 - 2880 = 9360 DXA
width: { size: 9360, type: WidthType.DXA },
columnWidths: [7000, 2360]  // テーブル幅の合計と一致する必要があります
```

**幅のルール:**
- **常に `WidthType.DXA` を使用** - 決して `WidthType.PERCENTAGE` を使用しない（Google Docsと互換性がない）
- テーブル幅は `columnWidths` の合計と等しくなければならない
- セルの `width` は対応する `columnWidth` と一致しなければならない
- セルの `margins` は内部パディングであり、セル幅に追加されるのではなく、コンテンツ領域を縮小する
- 全幅テーブルの場合：コンテンツ幅を使用（ページ幅から左右のマージンを引いたもの）

### 画像

```javascript
// 重要: typeパラメータは必須です
new Paragraph({
  children: [new ImageRun({
    type: "png", // 必須: png, jpg, jpeg, gif, bmp, svg
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150 },
    altText: { title: "Title", description: "Desc", name: "Name" } // 3つすべて必須
  })]
})
```

### 改ページ

```javascript
// 重要: PageBreakはParagraphの中になければなりません
new Paragraph({ children: [new PageBreak()] })

// または pageBreakBefore を使用
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

### 目次

```javascript
// 重要: 見出しはHeadingLevelのみを使用しなければなりません - カスタムスタイル不可
new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" })
```

### ヘッダー/フッター

```javascript
sections: [{
  properties: {
    page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } // 1440 = 1インチ
  },
  headers: {
    default: new Header({ children: [new Paragraph({ children: [new TextRun("Header")] })] })
  },
  footers: {
    default: new Footer({ children: [new Paragraph({
      children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
    })] })
  },
  children: [/* content */]
}]
```

### docx-js の重要なルール

- **ページサイズを明示的に設定する** - docx-jsのデフォルトはA4; USドキュメントにはUS Letter (12240 x 15840 DXA) を使用
- **横向き: 縦向きの寸法を渡す** - docx-jsは内部で幅/高さを入れ替える; 短い辺を `width`、長い辺を `height` として渡し、`orientation: PageOrientation.LANDSCAPE` を設定する
- **`\n` を決して使用しない** - 別のParagraph要素を使用する
- **Unicodeビュレットを決して使用しない** - ナンバリング設定で `LevelFormat.BULLET` を使用する
- **PageBreakはParagraph内にある必要がある** - スタンドアロンは無効なXMLを作成する
- **ImageRunは `type` を必要とする** - 常にpng/jpgなどを指定する
- **常にDXAでテーブル `width` を設定する** - `WidthType.PERCENTAGE` を決して使用しない（Google Docsで壊れる）
- **テーブルには二重の幅が必要** - `columnWidths` 配列とセルの `width` の両方が一致する必要がある
- **テーブル幅 = columnWidthsの合計** - DXAの場合、正確に合計されることを確認する
- **常にセルマージンを追加する** - 読みやすいパディングのために `margins: { top: 80, bottom: 80, left: 120, right: 120 }` を使用する
- **`ShadingType.CLEAR` を使用する** - テーブルのシェーディングにSOLIDを決して使用しない
- **TOCはHeadingLevelのみを必要とする** - 見出し段落にカスタムスタイルを使用しない
- **組み込みスタイルを上書きする** - 正確なIDを使用する: "Heading1", "Heading2" など
- **`outlineLevel` を含める** - TOCに必要（H1は0, H2は1など）

---

## 既存のドキュメントの編集

**3つのステップすべてを順番に実行してください。**

### ステップ1: 解凍
```bash
python scripts/office/unpack.py document.docx unpacked/
```
XMLを抽出し、整形し、隣接するランをマージし、スマートクォートをXMLエンティティ（`&#x201C;` など）に変換して、編集に耐えられるようにします。ランのマージをスキップするには `--merge-runs false` を使用してください。

### ステップ2: XMLの編集

`unpacked/word/` 内のファイルを編集します。パターンの詳細については、以下のXMLリファレンスを参照してください。

ユーザーが別の名前の使用を明示的に要求しない限り、変更履歴とコメントには**著者として「Claude」を使用してください**。

**文字列置換には編集ツールを直接使用してください。Pythonスクリプトを書かないでください。** スクリプトは不必要な複雑さをもたらします。編集ツールは正確に何が置き換えられているかを示します。

**重要: 新しいコンテンツにはスマートクォートを使用してください。** アポストロフィや引用符を含むテキストを追加する場合は、XMLエンティティを使用してスマートクォートを生成してください：
```xml
<!-- プロフェッショナルなタイポグラフィにはこれらのエンティティを使用してください -->
<w:t>Here&#x2019;s a quote: &#x201C;Hello&#x201D;</w:t>
```
| エンティティ | 文字 |
|--------|-----------|
| `&#x2018;` | ‘ (左シングル) |
| `&#x2019;` | ’ (右シングル / アポストロフィ) |
| `&#x201C;` | “ (左ダブル) |
| `&#x201D;` | ” (右ダブル) |

**コメントの追加:** 複数のXMLファイルにまたがるボイラープレートを処理するために `comment.py` を使用してください（テキストは事前にエスケープされたXMLである必要があります）：
```bash
python scripts/comment.py unpacked/ 0 "Comment text with &amp; and &#x2019;"
python scripts/comment.py unpacked/ 1 "Reply text" --parent 0  # コメント0への返信
python scripts/comment.py unpacked/ 0 "Text" --author "Custom Author"  # カスタム著者名
```
その後、document.xmlにマーカーを追加します（XMLリファレンスのコメントを参照）。

### ステップ3: パック
```bash
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```
自動修復を行い検証し、XMLを凝縮し、DOCXを作成します。検証をスキップするには `--validate false` を使用してください。

**自動修復が修正するもの:**
- `durableId` >= 0x7FFFFFFF (有効なIDを再生成)
- 空白を含む `<w:t>` の `xml:space="preserve"` 欠落

**自動修復が修正しないもの:**
- 不正な形式のXML、無効な要素のネスト、関係の欠落、スキーマ違反

### 一般的な落とし穴

- **`<w:r>` 要素全体を置換する**: 変更履歴を追加する場合、`<w:r>...</w:r>` ブロック全体を兄弟としての `<w:del>...<w:ins>...` に置き換えてください。ランの中に変更履歴タグを注入しないでください。
- **`<w:rPr>` フォーマットを保持する**: 元のランの `<w:rPr>` ブロックを変更履歴ランにコピーして、太字、フォントサイズなどを維持してください。

---

## XML リファレンス

### スキーマ準拠

- **`<w:pPr>` 内の要素順序**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` は最後
- **空白**: 先頭/末尾のスペースがある `<w:t>` に `xml:space="preserve"` を追加
- **RSID**: 8桁の16進数でなければなりません（例：`00AB1234`）

### 変更履歴

**挿入:**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

**削除:**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

**`<w:del>` 内部**: `<w:t>` の代わりに `<w:delText>` を、`<w:instrText>` の代わりに `<w:delInstrText>` を使用してください。

**最小限の編集** - 変更されるものだけをマークする:
```xml
<!-- "30 days" を "60 days" に変更 -->
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Claude" w:date="...">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Claude" w:date="...">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

**段落/リストアイテム全体の削除** - 段落からすべてのコンテンツを削除する場合、段落マークも削除済みとしてマークして、次の段落とマージされるようにします。`<w:del/>` を `<w:pPr><w:rPr>` 内に追加します：
```xml
<w:p>
  <w:pPr>
    <w:numPr>...</w:numPr>  <!-- リスト番号があれば -->
    <w:rPr>
      <w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z"/>
    </w:rPr>
  </w:pPr>
  <w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
    <w:r><w:delText>Entire paragraph content being deleted...</w:delText></w:r>
  </w:del>
</w:p>
```
`<w:pPr><w:rPr>` 内に `<w:del/>` がないと、変更を受け入れたときに空の段落/リストアイテムが残ります。

**他の著者の挿入の拒否** - 削除を彼らの挿入の中にネストします：
```xml
<w:ins w:author="Jane" w:id="5">
  <w:del w:author="Claude" w:id="10">
    <w:r><w:delText>their inserted text</w:delText></w:r>
  </w:del>
</w:ins>
```

**他の著者の削除の復元** - 後に挿入を追加します（彼らの削除を変更しないでください）：
```xml
<w:del w:author="Jane" w:id="5">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="10">
  <w:r><w:t>deleted text</w:t></w:r>
</w:ins>
```

### コメント

`comment.py`（ステップ2を参照）を実行した後、document.xmlにマーカーを追加します。返信の場合、`--parent` フラグを使用し、マーカーを親の中にネストします。

**重要: `<w:commentRangeStart>` と `<w:commentRangeEnd>` は `<w:r>` の兄弟であり、決して `<w:r>` の中ではありません。**

```xml
<!-- コメントマーカーはw:pの直接の子であり、決してw:rの中ではありません -->
<w:commentRangeStart w:id="0"/>
<w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted</w:delText></w:r>
</w:del>
<w:r><w:t> more text</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>

<!-- ネストされた返信1を持つコメント0 -->
<w:commentRangeStart w:id="0"/>
  <w:commentRangeStart w:id="1"/>
  <w:r><w:t>text</w:t></w:r>
  <w:commentRangeEnd w:id="1"/>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="1"/></w:r>
```

### 画像

1. 画像ファイルを `word/media/` に追加
2. 関係を `word/_rels/document.xml.rels` に追加:
```xml
<Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
```
3. コンテンツタイプを `[Content_Types].xml` に追加:
```xml
<Default Extension="png" ContentType="image/png"/>
```
4. document.xml内で参照:
```xml
<w:drawing>
  <wp:inline>
    <wp:extent cx="914400" cy="914400"/>  <!-- EMUs: 914400 = 1インチ -->
    <a:graphic>
      <a:graphicData uri=".../picture">
        <pic:pic>
          <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

---

## 依存関係

- **pandoc**: テキスト抽出
- **docx**: `npm install -g docx` (新しいドキュメント)
- **LibreOffice**: PDF変換 (`scripts/office/soffice.py` 経由でサンドボックス環境用に自動構成)
- **Poppler**: 画像用 `pdftoppm`
