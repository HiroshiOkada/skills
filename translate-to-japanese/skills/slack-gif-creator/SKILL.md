---
name: slack-gif-creator
description: Slack向けに最適化されたアニメーションGIFを作成するための知識とユーティリティ。制約、検証ツール、およびアニメーションの概念を提供します。ユーザーが「Slack用にXがYをしているGIFを作って」のようなSlack用のアニメーションGIFを要求した場合に使用します。
license: Complete terms in LICENSE.txt
---

# Slack GIF Creator

Slack向けに最適化されたアニメーションGIFを作成するためのユーティリティと知識を提供するツールキット。

## Slack要件

**寸法:**
- 絵文字GIF: 128x128 (推奨)
- メッセージGIF: 480x480

**パラメータ:**
- FPS: 10-30 (低いほどファイルサイズが小さくなる)
- 色数: 48-128 (少ないほどファイルサイズが小さくなる)
- 持続時間: 絵文字GIFの場合は3秒未満に保つ

## コアワークフロー

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

# 1. ビルダーを作成
builder = GIFBuilder(width=128, height=128, fps=10)

# 2. フレームを生成
for i in range(12):
    frame = Image.new('RGB', (128, 128), (240, 248, 255))
    draw = ImageDraw.Draw(frame)

    # PILプリミティブを使用してアニメーションを描画
    # (円, 多角形, 線など)

    builder.add_frame(frame)

# 3. 最適化して保存
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## グラフィックスの描画

### ユーザーアップロード画像の操作
ユーザーが画像をアップロードした場合、以下を望んでいるかどうかを検討します：
- **直接使用する**（例：「これをアニメーション化して」、「これをフレームに分割して」）
- **インスピレーションとして使用する**（例：「これのようなものを作って」）

PILを使用して画像を読み込んで操作します：
```python
from PIL import Image

uploaded = Image.open('file.png')
# 直接使用するか、色/スタイルの参照として使用する
```

### スクラッチからの描画
スクラッチからグラフィックスを描画する場合、PIL ImageDrawプリミティブを使用します：

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(frame)

# 円/楕円
draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)

# 星, 三角形, 任意の多角形
points = [(x1, y1), (x2, y2), (x3, y3), ...]
draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)

# 線
draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)

# 長方形
draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
```

**使用しないこと:** 絵文字フォント（プラットフォーム間で信頼性がない）や、事前にパッケージ化されたグラフィックスがこのスキルに存在すると仮定すること。

### グラフィックスを良く見せる

グラフィックスは基本的ではなく、洗練され創造的であるべきです。方法は以下の通りです：

**太い線を使用する** - アウトラインと線には常に `width=2` 以上を設定してください。細い線（width=1）は途切れ途切れで素人っぽく見えます。

**視覚的な深さを追加する**:
- 背景にグラデーションを使用する (`create_gradient_background`)
- 複雑さのために複数の形状を重ねる（例：星の中に小さな星）

**形状をより面白くする**:
- 単純な円を描くだけではない - ハイライト、リング、またはパターンを追加する
- 星は輝きを持つことができる（後ろに大きく半透明のバージョンを描く）
- 複数の形状を組み合わせる（星 + きらめき、円 + リング）

**色に注意を払う**:
- 鮮やかで補完的な色を使用する
- コントラストを追加する（明るい形状に暗いアウトライン、暗い形状に明るいアウトライン）
- 全体的な構成を考慮する

**複雑な形状の場合**（ハート、雪の結晶など）:
- 多角形と楕円の組み合わせを使用する
- 対称性のためにポイントを慎重に計算する
- 詳細を追加する（ハートにはハイライトカーブを持たせることができ、雪の結晶には複雑な枝がある）

創造的かつ詳細に！良いSlack GIFは、プレースホルダーグラフィックスのようにではなく、洗練されて見えるべきです。

## 利用可能なユーティリティ

### GIFBuilder (`core.gif_builder`)
フレームを組み立て、Slack用に最適化します：
```python
builder = GIFBuilder(width=128, height=128, fps=10)
builder.add_frame(frame)  # PIL画像を追加
builder.add_frames(frames)  # フレームのリストを追加
builder.save('out.gif', num_colors=48, optimize_for_emoji=True, remove_duplicates=True)
```

### バリデータ (`core.validators`)
GIFがSlack要件を満たしているか確認します：
```python
from core.validators import validate_gif, is_slack_ready

# 詳細な検証
passes, info = validate_gif('my.gif', is_emoji=True, verbose=True)

# クイックチェック
if is_slack_ready('my.gif'):
    print("Ready!")
```

### イージング関数 (`core.easing`)
直線の代わりにスムーズな動き：
```python
from core.easing import interpolate

# 0.0から1.0への進行
t = i / (num_frames - 1)

# イージングを適用
y = interpolate(start=0, end=400, t=t, easing='ease_out')

# 利用可能: linear, ease_in, ease_out, ease_in_out,
#           bounce_out, elastic_out, back_out
```

### フレームヘルパー (`core.frame_composer`)
一般的なニーズのための便利関数：
```python
from core.frame_composer import (
    create_blank_frame,         # 無地の背景
    create_gradient_background,  # 垂直グラデーション
    draw_circle,                # 円のヘルパー
    draw_text,                  # 単純なテキストレンダリング
    draw_star                   # 5点星
)
```

## アニメーションの概念

### シェイク/振動
オブジェクトの位置を発振でオフセットする：
- フレームインデックスで `math.sin()` または `math.cos()` を使用
- 自然な感じのために小さなランダム変動を追加
- xおよび/またはy位置に適用

### パルス/ハートビート
オブジェクトのサイズをリズミカルにスケーリングする：
- スムーズなパルスのために `math.sin(t * frequency * 2 * math.pi)` を使用
- ハートビートの場合：2回の速いパルスの後に一時停止（正弦波を調整）
- 基本サイズの0.8から1.2の間でスケーリング

### バウンス
オブジェクトが落ちて跳ね返る：
- 着地のために `easing='bounce_out'` で `interpolate()` を使用
- 落下（加速）のために `easing='ease_in'` を使用
- 各フレームでy速度を上げることにより重力を適用

### スピン/回転
中心の周りでオブジェクトを回転させる：
- PIL: `image.rotate(angle, resample=Image.BICUBIC)`
- ワブルの場合：線形の代わりに角度に正弦波を使用

### フェードイン/アウト
徐々に現れるか消える：
- RGBA画像を作成し、アルファチャンネルを調整
- または `Image.blend(image1, image2, alpha)` を使用
- フェードイン: アルファ0から1へ
- フェードアウト: アルファ1から0へ

### クリエイティブ！
概念を組み合わせ（バウンス + 回転、パルス + スライドなど）、PILの全機能を使用してください。

## 依存関係

```bash
pip install pillow imageio numpy
```
