# 開発ワークフロー

## 目的

このドキュメントは、Minecraft Server Dashboardプロジェクトの開発ワークフロー、Git運用、コラボレーションプロセスを定義します。

## ブランチ戦略

Git FlowとGitHub Flowの**ハイブリッドアプローチ**を採用し、安定したリリースを保ちながら継続的な開発を行います。

### ブランチタイプ

#### `main` - 本番ブランチ
- **目的**: 常にデプロイ可能、最新リリースを表す
- **保護**: ブランチ保護有効
- **直接コミット**: ❌ 禁止
- **マージ元**: `develop`のみ（プルリクエスト経由）
- **タグ付け**: 全てのマージでGitHub Releaseを作成

#### `develop` - 開発ブランチ
- **目的**: 進行中の開発の統合ブランチ
- **保護**: ブランチ保護なし（柔軟性を重視）
- **直接コミット**: ❌ 非推奨
- **マージ元**: `feature/*`, `fix/*`, `refactor/*`など
- **派生元**: 全ての機能ブランチの基点

#### `feature/*` - 機能ブランチ
- **目的**: 新機能や機能強化
- **派生元**: `develop`
- **命名**: `feature/簡潔な説明` (例: `feature/user-authentication`)
- **寿命**: 短命（マージ後削除）
- **例**: `feature/server-status-dashboard`

#### `fix/*` - バグ修正ブランチ
- **目的**: バグ修正（緊急修正を含む）
- **派生元**: `develop`
- **命名**: `fix/簡潔な説明` (例: `fix/login-error`)
- **寿命**: 短命（マージ後削除）
- **注意**: 緊急のhotfixでも`develop`から派生し、迅速なリリースを実施

#### `refactor/*` - リファクタリングブランチ
- **目的**: 機能変更を伴わないコードリファクタリング
- **派生元**: `develop`
- **命名**: `refactor/簡潔な説明`
- **寿命**: 短命（マージ後削除）

#### `docs/*` - ドキュメントブランチ
- **目的**: ドキュメントの更新
- **派生元**: `develop`
- **命名**: `docs/簡潔な説明`
- **寿命**: 短命（マージ後削除）

#### `test/*` - テスト改善ブランチ
- **目的**: テストの追加や改善
- **派生元**: `develop`
- **命名**: `test/簡潔な説明`
- **寿命**: 短命（マージ後削除）

### ブランチ命名規則

**形式**: `<タイプ>/<簡潔な説明>`

**ルール**:
- 小文字を使用
- 単語の区切りはハイフンを使用
- 簡潔だが説明的に
- Issue番号をブランチ名に含めない（代わりにPRでリンク）

**例**:
- ✅ `feature/websocket-notifications`
- ✅ `fix/memory-leak-logs`
- ✅ `refactor/api-error-handling`
- ❌ `feature/issue-123` (Issue番号を含めない)
- ❌ `Feature/WebSocket-Notifications` (小文字を使用)
- ❌ `new_feature` (タイプのプレフィックスを使用)

## コミットメッセージ規約

**Conventional Commits**仕様を使用します。

### 形式

```
<type>(<scope>): <description>

[任意のbody]

[任意のfooter]
```

### タイプ

- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメントの変更
- **style**: コードスタイルの変更（フォーマット、セミコロンの欠落など）
- **refactor**: リファクタリング（機能変更やバグ修正を伴わない）
- **perf**: パフォーマンス改善
- **test**: テストの追加や更新
- **build**: ビルドシステムや外部依存関係の変更
- **ci**: CI/CD設定の変更
- **chore**: srcやtestファイルを変更しないその他の変更

### スコープ（任意）

スコープはコードベースのどの部分が影響を受けるかを指定します：
- `api`: バックエンドAPI
- `ui`: フロントエンドUI
- `db`: データベース
- `auth`: 認証
- `server`: サーバー管理ロジック
- など

### 例

```
feat(api): add server status endpoint

WebSocketを介したリアルタイムサーバーステータス監視を実装。
Closes #123
```

```
fix(ui): resolve memory leak in dashboard component

ダッシュボードがイベントリスナーを適切にクリーンアップしていなかった問題を修正。
```

```
docs: update API documentation for v2 endpoints
```

```
refactor(auth): simplify JWT token validation logic
```

### コミットメッセージのルール

- 命令形を使用（"add"であり、"added"や"adds"ではない）
- 1行目は72文字以内
- 説明の最初の文字は大文字
- 説明の最後にピリオドを付けない
- bodyで「何を」「なぜ」を説明し、「どのように」は説明しない
- footerでissueやPRを参照

## プルリクエストワークフロー

### プルリクエストの作成

1. **ブランチを作成** (`develop`から)
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. **適切なコミットで変更を作成**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **ブランチをdevelopと同期**
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

4. **リモートにプッシュ**
   ```bash
   git push origin feature/my-feature
   ```

5. **GitHubでプルリクエストを作成**
   - Base: `develop`
   - Title: 明確で説明的な要約
   - Description: 文脈、変更内容、テストメモ
   - 関連issueをリンク

### プルリクエストタイトル

PRタイトルはConventional Commits形式に従います：
```
<type>(<scope>): <description>
```

例: `feat(api): add server status endpoint`

### プルリクエスト説明テンプレート

```markdown
## 概要
変更の簡潔な説明

## 変更内容
- 変更1
- 変更2

## テスト方法
これらの変更をテストする方法

## 関連Issue
Closes #123
```

### ドラフトプルリクエスト

作業中には**ドラフトPR**を使用：
- アプローチへの早期フィードバック
- CI/CDチェックの検証
- チームへの作業の認知

完了したら「Ready for Review」に変更します。

## コードレビュープロセス

### マージの要件

全てのプルリクエストは以下の要件を満たす必要があります：

#### 自動チェック（必須）
- ✅ **ユニットテスト合格**（95%以上のカバレッジ維持）
- ✅ **Linter合格**（警告ゼロ）
- ✅ **型チェック合格**（strictモード）
- ✅ **ビルド成功**（エラーなし）

#### 手動レビュー（任意だが推奨）
- チームメンバーによるコードレビュー
- 大きな変更には最低1名の承認

### レビューの焦点

レビュアーは以下に焦点を当てるべきです：
1. **PHILOSOPHY.md**の原則との整合性
2. **テスタビリティ**: このコードは簡単にテストできるか？
3. **保守性**: コードは明確で適切にドキュメント化されているか？
4. **アーキテクチャ**: 全体設計に適合しているか？
5. **セキュリティ**: セキュリティ上の懸念はないか？

### レビュー応答時間

- 初回レビューは24-48時間以内（ベストエフォート）
- 緊急の修正の場合、チームに通知

## マージ戦略

### 方法: Squash and Merge

全てのPRは**Squash and Merge**でマージ：
- 複数のコミットを1つに統合
- `develop`と`main`でクリーンで直線的な履歴
- コミットメッセージはConventional Commitsに従う

### Squashコミットメッセージ

Squashされたコミットメッセージは：
- PRタイトルをコミットメッセージとして使用
- footerにPR番号を含める
- PR説明から重要な詳細を保持

例：
```
feat(api): add server status endpoint (#123)

WebSocketを介したリアルタイムサーバーステータス監視を実装。
```

### マージ後

- **機能ブランチを削除**（GitHubで自動）
- **関連issueをクローズ**（"Closes #123"使用時は自動）

## リリースプロセス

### `develop`から`main`へ

1. **リリース準備**
   - 意図した全機能が`develop`にマージされていることを確認
   - `develop`で全てのCIチェックが合格していることを確認
   - 必要に応じてバージョン番号を更新

2. **リリースPR作成**
   ```
   From: develop
   To: main
   Title: "release: version X.Y.Z"
   ```

3. **レビューとマージ**
   - 全ての自動チェックが合格していること
   - changelog/リリースノートをレビュー
   - Squash and mergeで`main`にマージ

4. **GitHub Releaseを作成**
   - Tag: `vX.Y.Z`
   - Title: `Version X.Y.Z`
   - Description: リリースノート（機能、修正、破壊的変更）
   - 該当する場合はバイナリを添付

5. **リリース後**
   - デプロイを確認
   - 問題を監視

### Hotfixプロセス

緊急の本番修正の場合：

1. **fixブランチを作成**（`main`ではなく`develop`から）
   ```bash
   git checkout develop
   git checkout -b fix/critical-bug
   ```

2. **修正を実装してテスト**
   - 変更を最小限に焦点を絞る
   - テストで修正をカバーすることを確認

3. **`develop`へのPRを作成**
   - 緊急/hotfixとしてマーク
   - 必要に応じて迅速なレビュー

4. **`develop`へのマージ後**
   - 直ちに`main`へのリリースPRを作成
   - 緊急GitHub Releaseを作成

## ブランチ保護ルール

### `main`ブランチ

- ✅ マージ前にプルリクエストを要求
- ✅ ステータスチェックの合格を要求：
  - ユニットテスト
  - Linter
  - 型チェック
  - ビルド
- ✅ マージ前に会話の解決を要求
- ✅ 上記設定のバイパスを許可しない
- ❌ 承認を要求：任意（自動チェックに依存）
- ❌ 直線的な履歴を要求：不要（squash mergeを使用）

### `develop`ブランチ

- ブランチ保護なし（柔軟性を重視）
- 全てのマージは依然としてCIチェックの合格が必要（PRプロセス経由で強制）

## 継続的インテグレーション (CI/CD)

### 自動チェック

全てのブランチへのプッシュ時に実行：

1. **ユニットテスト**
   - 全てのテストスイートを実行
   - 最低95%のカバレッジを検証
   - カバレッジの変更を報告

2. **Linter**
   - ESLint（JavaScript/TypeScript）
   - Pylint/Flake8（Python）
   - 警告ゼロポリシー

3. **型チェック**
   - TypeScript: strictモード
   - Python: mypy with strict設定

4. **ビルド**
   - バックエンドビルド
   - フロントエンドビルド
   - Dockerイメージビルド（該当する場合）

### CI設定

- **プラットフォーム**: GitHub Actions（推奨）
- **実行対象**: 全てのブランチ、全てのPR
- **Fail fast**: 最初の失敗で停止
- **キャッシュ**: より高速な実行のために依存関係をキャッシュ

### ワークフロー例

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: npm test -- --coverage
      - name: Check coverage
        run: npm run coverage:check

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linter
        run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Type check
        run: npm run typecheck

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: npm run build
```

## 依存関係管理

### 自動依存関係更新

**Dependabot**（または類似ツール）を使用した自動依存関係更新：

- **スケジュール**: 週次
- **自動マージ**: パッチおよびマイナーアップデート（CI合格後）
- **手動レビュー**: メジャーバージョンアップデート
- **セキュリティ更新**: 即座、高優先度

### Dependabot設定

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

## ベストプラクティス

### すべきこと ✅

- ブランチは短命に保つ（可能なら1週間以内）
- 明確なメッセージで頻繁にコミット
- コンフリクトを避けるため定期的に`develop`をrebase
- 全ての新コードにテストを書く
- コード変更と共にドキュメントを更新
- マージ後はブランチを削除
- 早期フィードバックのためにドラフトPRを使用

### してはいけないこと ❌

- `main`や`develop`に直接コミットしない
- 共有ブランチにforce pushしない
- CIチェックが合格せずにマージしない
- 未解決の会話がある状態でマージしない
- 古くなったブランチを開いたままにしない
- シークレットや機密データをコミットしない
- テストを書くことをスキップしない

## トラブルシューティング

### マージコンフリクト

```bash
# 最新のdevelopでブランチを更新
git fetch origin
git rebase origin/develop

# コンフリクトを解決
# コンフリクトしたファイルを編集
git add <resolved-files>
git rebase --continue

# Force push（機能ブランチでは安全）
git push --force-with-lease
```

### CI チェック失敗

1. **最新の変更をpull**してローカルでチェックを実行
2. **問題を修正**して新しいコミットを作成
3. **プッシュ**してPRを更新
4. CIが自動的に再実行される

### 誤って間違ったブランチにコミット

```bash
# まだプッシュしていない場合
git reset HEAD~1  # 最後のコミットを取り消し、変更は保持
git stash         # 変更を保存
git checkout correct-branch
git stash pop     # 変更を適用

# 既にプッシュ済みの場合
# 正しいブランチから新しいPRを作成
```

---

**最終更新日**: 2025-12-25
