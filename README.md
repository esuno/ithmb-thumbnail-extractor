# iOS ITHMB Thumbnail Extractor

iOS デバイスから取得した ITHMB ファイル（iTunes Thumbnail）から、サムネイル画像を抽出するPythonスクリプトです。

## 概要

ITHMB ファイルは iOS デバイス（iPhone、iPad、iPod）が保存するサムネイル画像の集合です。通常のヘッダー情報を持たない生のバイナリフォーマットであり、このツールはそこから個別の画像を抽出します。

## 機能

- ✅ ITHMB ファイルから複数のサムネイル画像を抽出
- ✅ RGB / RGBA / BGR カラーモードに対応
- ✅ 複数のデバイス向けサムネイルサイズに対応
- ✅ 自動サイズ検出機能
- ✅ PNG形式での出力（連番命名）
- ✅ エラーハンドリング機能
- ✅ コマンドラインインターフェース

## インストール

### 必要な環境

- Python 3.13.2以上
- Pillow（PIL）ライブラリ

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/esuno/ithmb-thumbnail-extractor.git
cd ithmb-thumbnail-extractor

# 依存ライブラリのインストール
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```bash
# デフォルト設定で抽出（160x120 RGB）
python ithmb_extractor.py image.ithmb

# カスタムサイズで抽出
python ithmb_extractor.py image.ithmb -w 320 -H 240

# RGBA形式で抽出
python ithmb_extractor.py image.ithmb -m RGBA

# BGR形式で抽出
python ithmb_extractor.py image.ithmb -m BGR

# 自動サイズ検出で抽出
python ithmb_extractor.py image.ithmb --auto-detect

# 出力ディレクトリを指定
python ithmb_extractor.py image.ithmb -o ./thumbnails

# 出力を抑制（静かモード）
python ithmb_extractor.py image.ithmb -q
```

### コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| `-w, --width` | サムネイルの幅（ピクセル） | 160 |
| `-H, --height` | サムネイルの高さ（ピクセル） | 120 |
| `-m, --mode` | カラーモード（RGB/RGBA/BGR） | RGB |
| `-o, --output` | 出力ディレクトリ | 現在のディレクトリ |
| `--auto-detect` | ファイルからサイズを自動検出 | 無効 |
| `--list-sizes` | 既知のサイズ一覧を表示 | - |
| `-q, --quiet` | 出力を抑制 | 無効 |

### サポートされているサムネイルサイズ

| デバイス | サイズ | カラーモード |
|---------|--------|-----------|
| iPhone / iPad | 160×120 | RGB |
| iPhone 4+ / iPad 2+ | 320×240 | RGB |
| iPod Video | 158×118 | RGB |
| iPod Nano | 130×88 | RGB |

```bash
# 既知のサイズを一覧表示
python ithmb_extractor.py --list-sizes
```

## 使用例

### 例1：標準的なiPhoneのサムネイルを抽出

```bash
python ithmb_extractor.py ~/Documents/image.ithmb -o ./extracted_thumbs
```

結果：
```
Extracting ITHMB file: ~/Documents/image.ithmb
Parameters: 160x120, RGB, 3 bytes/pixel
File size: 576000 bytes
Output directory: ./extracted_thumbs

✓ Extracted: thumb_0001.png
✓ Extracted: thumb_0002.png
✓ Extracted: thumb_0003.png
...
✓ Extracted: thumb_0100.png

Extraction complete: 100 images extracted.
```

### 例2：ファイルサイズから自動検出

```bash
python ithmb_extractor.py photo_data.ithmb --auto-detect -o ./output
```

### 例3：Pythonコードとして使用

```python
from ithmb_extractor import IthmhExtractor

# エクストラクター初期化
extractor = IthmhExtractor(
    'image.ithmb',
    width=160,
    height=120,
    color_mode='RGB',
    output_dir='./thumbnails'
)

# 抽出実行
count = extractor.extract(verbose=True)
print(f"Successfully extracted {count} images")
```

## 仕様

### ITHMB ファイル形式

ITHMB ファイルはシンプルな構造：

```
[Thumbnail 1 - Raw Pixel Data] [Thumbnail 2 - Raw Pixel Data] ...
```

- **ファイルヘッダ**: なし
- **サムネイルフォーマット**: 生のピクセルデータ（RGB/RGBA/BGR）
- **ピクセルレイアウト**: 左上から右、下方向に並ぶ（通常の画像データ順）

### 出力ファイル名

抽出されたサムネイルは以下の形式で命名されます：

```
thumb_0001.png
thumb_0002.png
thumb_0003.png
...
thumb_9999.png
```

## トラブルシューティング

### 画像が歪んでいる場合

1. **カラーモードを確認**: RGB / RGBA / BGR から試してください
   ```bash
   python ithmb_extractor.py image.ithmb -m RGBA
   ```

2. **サイズを確認**: 異なるデバイスは異なるサイズのサムネイルを使用します
   ```bash
   python ithmb_extractor.py image.ithmb -w 320 -H 240
   ```

3. **自動検出を試す**:
   ```bash
   python ithmb_extractor.py image.ithmb --auto-detect
   ```

### ファイルが見つからない場合

```bash
# ファイルパスが正しいか確認
python ithmb_extractor.py ./path/to/image.ithmb
```

### ディスク容量不足

ITHMB ファイルが大きい場合、出力画像も多数生成されます。十分なディスク容量を確認してください。

## 計算例

**ファイルサイズからの画像数推定**:

- 160×120 RGB: `160 × 120 × 3 = 57,600 bytes/image`
- 320×240 RGB: `320 × 240 × 3 = 230,400 bytes/image`

例：2.3MB のファイル → `2,300,000 ÷ 57,600 ≈ 40 images`

## ライセンス

MIT License

## 貢献

バグ報告や機能リクエストは Issue でお願いします。

## 参考資料

- [Wikipedia: ITHMB](https://en.wikipedia.org/wiki/ITHMB)
- [FileInfo: ITHMB Extension](https://fileinfo.com/extension/ithmb)

---

**注意**: このツールを使用する前に、元のファイルのバックアップを取ってください。
