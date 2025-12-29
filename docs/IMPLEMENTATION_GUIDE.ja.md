# 実装ガイド

**最終更新日**: 2025-12-30

## 目的

本ドキュメントは、Minecraft Server Dashboardプロジェクトにおける機能実装のステップバイステップガイドです。タスクを受け取ってからマージまでのワークフローを定義し、コーディング前の要件理解を重視しています。

## 基本原則

1. **実装前に理解する**: コードを書く前に必ず要件を明確化し、現状を確認する
2. **API優先開発**: API実装・マージ後にUIを実装する（完全分離）
3. **不明点は質問する**: 推測で進めず、必ず明確化を求める
4. **仕様に従う**: ARCHITECTURE.mdが機能仕様の情報源
5. **テストカバレッジを重視する**: 95%を目指す（最低75%はCIで強制）

## 実装ワークフロー

### ステップ0: タスク理解と現状確認

**これは実装前の必須ステップです。**

#### 0-1. タスクの明確化

実装を開始する前に、以下を理解してください：

- [ ] **目的**: なぜこの機能が必要なのか？どの問題を解決するのか？
- [ ] **要件**: 具体的に何を実装するのか？
- [ ] **完了の定義**: 何ができたら完了とみなすのか？
- [ ] **範囲**: このタスクに含まれるもの・含まれないものは？
- [ ] **制約**: 技術的な制約や依存関係はあるか？

**重要**: 不明な点があれば、**すぐに質問してください**。推測や仮定で進めないでください。

#### 0-2. 現状の確認

**Gitブランチ状態の確認**:
```bash
# 現在のブランチを確認
git branch

# リポジトリの状態を確認
git status

# 未コミットの変更を確認
git diff
git diff --staged
```

- [ ] 現在どのブランチにいるか？
  - ❌ `main`ブランチにいる → **ストップ！mainに直接コミットしないでください**
  - ❌ 間違ったfeatureブランチにいる → 正しいブランチに切り替えるか新規作成
  - ✅ 正しいfeatureブランチにいる → 実装を進める
  - ✅ `main`にいるが新しいブランチが必要 → featureブランチを作成（下記参照）

- [ ] 未コミットの変更があるか？
  - ✅ はい、現在のタスクの変更 → 問題なし、作業を続ける
  - ❌ はい、別のタスクの変更 → まずコミットまたはstashする
  - ✅ いいえ、変更なし → クリーンな状態、開始可能

**適切なブランチの作成または切り替え**（必要な場合）:
```bash
# mainにいて新しいfeatureブランチを作成する場合
git checkout main
git pull origin main
git checkout -b feature/api-<機能名>

# 既存のブランチに切り替える場合
git checkout feature/api-<機能名>
git pull origin feature/api-<機能名>  # プッシュ済みの場合は最新を取得

# 未コミットの変更があってブランチを切り替える必要がある場合
git stash                          # 一時的に変更を保存
git checkout <対象ブランチ>
git stash pop                      # 変更を復元（該当する場合）
```

**ブランチ命名規則の参照**（WORKFLOW.mdより）:
- `feature/<簡潔な説明>` - 新機能
- `fix/<簡潔な説明>` - バグ修正
- `refactor/<簡潔な説明>` - コードリファクタリング
- `docs/<簡潔な説明>` - ドキュメント更新
- `test/<簡潔な説明>` - テスト改善

**仕様の確認**:
```bash
# ARCHITECTURE.mdで機能仕様を確認
grep -n "<機能キーワード>" docs/ARCHITECTURE.md

# 機能が既にドキュメント化されているか確認
grep -rn "<機能キーワード>" docs/
```

- [ ] この機能はARCHITECTURE.mdに仕様が記載されているか？
  - ✅ はい → 仕様に正確に従う
  - ❌ いいえ → 実装前に仕様を依頼する

**既存コードの確認**:
```bash
# 関連する実装を検索（バックエンド）
grep -rn "<機能キーワード>" api/src/

# 関連する実装を検索（フロントエンド）
grep -rn "<機能キーワード>" ui/src/

# 既存のデータベーススキーマを確認
ls -la api/alembic/versions/
```

- [ ] 類似機能が既に実装されているか？
  - ✅ はい → 既存パターンに従う（命名、構造、テスト）
  - ❌ いいえ → 新しいパターン（アーキテクチャとの整合性を確認）

**データベース状態の確認**:
```bash
# 既存マイグレーションの一覧
alembic history

# 現在のスキーマを確認
docker compose exec postgres psql -U mcadmin -d mc_dashboard -c "\dt"
```

- [ ] 必要なデータベーステーブル/カラムは存在するか？
  - ✅ はい → 既存スキーマを再利用
  - ❌ いいえ → マイグレーション作成が必要

**依存関係の確認**:

- [ ] この機能は他の機能に依存しているか？
  - ✅ はい → 依存機能が先に実装されていることを確認
  - ❌ いいえ → 実装を進める

#### 0-3. ステークホルダーとの範囲確認

確認結果に基づいて、実装範囲を確認します：

```markdown
タスク: <機能名>の実装

現状:
- ARCHITECTURE.md仕様: [あり/なし]
- 既存関連コード: [ファイル一覧]
- データベーススキーマ: [存在する/作成が必要]

提案する範囲:
1. [タスク要素1]
2. [タスク要素2]
3. [タスク要素3]

質問:
1. [質問1]
2. [質問2]

この範囲で正しいでしょうか？
```

### ステップ1: タスク分析

タスクを理解した後、実装アプローチを分析します：

#### 1-1. 実装タイプの決定

- [ ] **APIのみ**: バックエンド実装（Python/FastAPI）
- [ ] **UIのみ**: フロントエンド実装（Next.js/React/TypeScript）
- [ ] **両方**: API優先、次にUI（別ブランチ、別PR）

**重要**: APIとUIは**完全に分離**してください。同じブランチ/PRで両方を実装しないでください。

#### 1-2. データベース変更の確認

- [ ] **新規テーブルが必要**: Alembicマイグレーション作成
- [ ] **新規カラムが必要**: Alembicマイグレーション作成
- [ ] **データベース変更なし**: マイグレーション作成をスキップ
- [ ] **アプリケーションロジックのみ**: データベース作業不要

データベーススキーマ設計は**必須ステップではありません** - データベース変更が必要な場合のみ実施してください。

#### 1-3. 依存関係の特定

- [ ] この機能は先に実装すべき他の機能が必要か？
- [ ] この機能は将来の機能の依存対象になるか？
- [ ] 追加すべき外部ライブラリの依存関係はあるか？

### ステップ2: API実装（該当する場合）

**ブランチ命名**: `feature/api-<機能名>` または `fix/api-<問題説明>`

#### 2-1. ブランチ作成

```bash
git checkout main
git pull origin main
git checkout -b feature/api-user-registration
```

#### 2-2. データベースマイグレーション（必要な場合）

```bash
cd api

# マイグレーション作成
alembic revision --autogenerate -m "add users table for authentication"

# 生成されたマイグレーションを確認
cat alembic/versions/<revision-id>_add_users_table_for_authentication.py

# ローカルでマイグレーションを適用
alembic upgrade head

# スキーマを確認
docker compose exec postgres psql -U mcadmin -d mc_dashboard -c "\d users"
```

#### 2-3. APIコンポーネントの実装

**実装順序**:

1. **Pydanticモデル** (`api/src/app/schemas/`)
   - リクエストスキーマ（バリデーション）
   - レスポンススキーマ（シリアライゼーション）
   - 包括的なフィールドバリデーション追加

2. **データベースモデル** (`api/src/app/models/`) - マイグレーション作成時
   - SQLAlchemyモデル
   - リレーションシップと制約

3. **ビジネスロジック** (`api/src/app/services/`)
   - サービス層関数
   - エラーハンドリング
   - ビジネスルールバリデーション

4. **APIエンドポイント** (`api/src/app/routers/`)
   - FastAPIルートハンドラ
   - OpenAPIドキュメント
   - HTTPステータスコード

5. **単体テスト** (`api/tests/`)
   - 全サービス関数のテスト
   - 全エンドポイントのテスト
   - バリデーションとエラーケースのテスト
   - 目標: 95%カバレッジ（最低75%）

#### 2-4. コード品質チェック

```bash
cd api

# リンティング
ruff check .

# フォーマッティング
ruff format .

# 型チェック
mypy src/

# カバレッジ付きテスト実行
pytest --cov --cov-report=term-missing

# カバレッジが75%以上であることを確認
pytest --cov --cov-report=term --cov-fail-under=75
```

#### 2-5. プルリクエスト作成

```bash
# 変更をコミット
git add .
git commit -m "$(cat <<'EOF'
feat(api): add user registration endpoint

Implements POST /api/auth/register with:
- User data validation (email, password, username)
- Password hashing with bcrypt
- Admin approval workflow (pending → approved)
- Duplicate email prevention

Database migration: users, roles, permissions tables
Test coverage: 96%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# リモートにプッシュ
git push origin feature/api-user-registration
```

GitHubでPR作成:
- ベースブランチ: `main`
- タイトル: `feat(api): add user registration endpoint`
- 説明: WORKFLOW.mdのPRテンプレートに従う
- CIが通過するまで待つ
- **Squash and merge**でマージ
- マージ後にブランチを削除

### ステップ3: UI実装（該当する場合）

**重要**: UI実装は**別タスク**で**別ブランチと別PR**です。

API PRが`main`にマージされた**後**にのみUI実装を開始してください。

**ブランチ命名**: `feature/ui-<機能名>` または `fix/ui-<問題説明>`

#### 3-1. ブランチ作成

```bash
git checkout main
git pull origin main  # 最新のAPI変更を取得
git checkout -b feature/ui-registration-form
```

#### 3-2. UIコンポーネントの実装

**実装順序**:

1. **TypeScript型定義** (`ui/src/types/`)
   - APIリクエスト/レスポンス型
   - コンポーネントのProp型
   - バックエンドのPydanticスキーマと一致させる

2. **APIクライアント** (`ui/src/lib/api/`)
   - Fetchラッパー関数
   - エラーハンドリング
   - 型安全なAPI呼び出し

3. **Reactコンポーネント** (`ui/src/components/`)
   - UIコンポーネント
   - フォームバリデーション
   - エラー表示

4. **ページ統合** (`ui/src/app/`)
   - コンポーネントのページへの統合
   - ルーティング設定
   - レイアウト更新

5. **単体テスト** (`ui/src/__tests__/`)
   - コンポーネントテスト
   - APIクライアントテスト
   - ユーザーインタラクションテスト
   - 目標: 95%カバレッジ（最低75%）

#### 3-3. コード品質チェック

```bash
cd ui

# リンティング
npm run lint

# フォーマッティング
npm run format

# 型チェック
npm run type-check

# カバレッジ付きテスト実行
npm run test:coverage

# ビルド確認
npm run build
```

#### 3-4. プルリクエスト作成

```bash
# 変更をコミット
git add .
git commit -m "$(cat <<'EOF'
feat(ui): add user registration form

Implements registration form with:
- Email, password, username validation
- Password strength indicator
- Error message display
- Success confirmation

Integrates with POST /api/auth/register
Test coverage: 94%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# リモートにプッシュ
git push origin feature/ui-registration-form
```

GitHubでPR作成:
- ベースブランチ: `main`
- タイトル: `feat(ui): add user registration form`
- 説明: PRテンプレートに従う
- CIが通過するまで待つ
- **Squash and merge**でマージ
- マージ後にブランチを削除

### ステップ4: 統合と完了

#### 4-1. 統合テスト（APIとUI両方を実装した場合）

両方のPRがマージされた後:

```bash
# 最新の変更を取得
git checkout main
git pull origin main

# 全サービス起動
docker compose up -d

# 手動テスト
# 1. http://localhost:3000 を開く
# 2. 登録フローをエンドツーエンドでテスト
# 3. データベースエントリを確認
# 4. APIログでエラーを確認
```

#### 4-2. ドキュメント更新

機能がドキュメント更新を必要とする場合:

```bash
git checkout -b docs/update-registration-docs

# 関連ドキュメントを更新
# - ARCHITECTURE.md（アーキテクチャが変更された場合）
# - README.md（ユーザー向け機能の場合）
# - APIドキュメント（新しいエンドポイントの場合）

git commit -m "docs: update registration feature documentation"
git push origin docs/update-registration-docs
```

同じワークフローでPRを作成。

## 具体例: ユーザー登録API

完全な例を見ていきましょう: **「アカウント作成APIを作成してください」**

### ステップ0: タスク理解

**受信タスク**: "アカウント作成APIを作成してください"

**明確化のための質問**:

```
1. 要件の明確化:
   - 登録に必要なユーザー情報は何ですか？
     (email, password, username, display_name など)
   - 管理者承認ワークフローは必要ですか？
     (ARCHITECTURE.mdにユーザー承認ワークフローの記載があります)
   - パスワードのバリデーションルールは？
     (最小長、文字要件など)

2. 現状確認:
   - ARCHITECTURE.mdチェック: ✅ PBACシステム仕様あり
   - 既存コード: ❌ 認証コードは存在しない
   - データベース: ❌ usersテーブルなし（alembic/versions/が空）

3. 提案する範囲:
   a. データベーススキーマ（users, roles, permissionsテーブル）
   b. POST /api/auth/register エンドポイント
   c. パスワードハッシュ化とバリデーション
   d. 管理者承認ワークフロー（pending → approved）
   e. 単体テスト（95%カバレッジ）

   または、まず基本的な登録のみ実装すべきでしょうか（承認ワークフローなし）？
```

**ステークホルダーの回答**（例）:
```
まず基本的な登録から開始してください（承認ワークフローは今は不要）。
必須フィールド: email, password, username
パスワードルール: 最低8文字、英字と数字を含む
```

### ステップ1: タスク分析

- **実装タイプ**: APIのみ（UIは別タスク）
- **データベース変更**: 新規テーブルが必要（users, roles, permissions）
- **依存関係**: なし（これは認証の基盤）

### ステップ2: 実装

#### 2-1. ブランチ作成

```bash
git checkout -b feature/api-user-registration
```

#### 2-2. データベースマイグレーション作成

```bash
cd api
alembic revision --autogenerate -m "add users roles and permissions tables"
```

生成されたマイグレーションを編集して追加:
- `users` テーブル（id, email, password_hash, username, created_at など）
- `roles` テーブル（id, name, description）
- `permissions` テーブル（id, name, category, description）
- `role_permissions` テーブル（role_id, permission_id）
- `user_permissions` テーブル（user_id, permission_id, grant_type）

```bash
alembic upgrade head
```

#### 2-3. コンポーネント実装

**ファイル**: `api/src/app/schemas/auth.py`
```python
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)

class UserRegisterResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
```

**ファイル**: `api/src/app/models/user.py`
```python
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**ファイル**: `api/src/app/services/auth.py`
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def register_user(db: AsyncSession, user_data: UserRegisterRequest) -> User:
    # メールが存在するか確認
    # パスワードをハッシュ化
    # ユーザーを作成
    # ユーザーオブジェクトを返す
    pass
```

**ファイル**: `api/src/app/routers/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserRegisterResponse, status_code=201)
async def register(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # サービス関数を呼び出し
    # エラーを処理
    # レスポンスを返す
    pass
```

**ファイル**: `api/tests/test_auth.py`
```python
import pytest

@pytest.mark.asyncio
async def test_register_success():
    # 成功時の登録をテスト
    pass

@pytest.mark.asyncio
async def test_register_duplicate_email():
    # 重複メールエラーをテスト
    pass

@pytest.mark.asyncio
async def test_register_weak_password():
    # パスワードバリデーションをテスト
    pass
```

#### 2-4. 品質チェック実行

```bash
ruff check . && ruff format .
mypy src/
pytest --cov --cov-fail-under=75
```

#### 2-5. PR作成

```bash
git add .
git commit -m "$(cat <<'EOF'
feat(api): add user registration endpoint

Implements POST /api/auth/register with:
- Email, password, username validation
- Password hashing with bcrypt
- Duplicate email/username prevention
- Database schema for users, roles, permissions

Test coverage: 96%
Closes #123

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
git push origin feature/api-user-registration
```

CIが通過したらマージ。

### ステップ3: UI実装（別タスク）

**新規タスク**: "ユーザー登録フォームUIを作成してください"

```bash
git checkout main
git pull origin main
git checkout -b feature/ui-registration-form
```

上記のステップ3ワークフローに従ってフロントエンドを実装。

## 実装チェックリスト

すべての実装タスクでこのチェックリストを使用してください：

### 実装前
- [ ] 現在のGitブランチを確認（`main`にいない）
- [ ] 適切なfeatureブランチを作成または切り替え
- [ ] 他のタスクの未コミット変更がない
- [ ] タスクの目的と要件が明確
- [ ] 全ての曖昧さをステークホルダーと明確化
- [ ] ARCHITECTURE.mdで仕様を確認
- [ ] 既存の類似実装を検索
- [ ] データベーススキーマの状態を確認
- [ ] 依存関係を特定
- [ ] 実装範囲を確認

### API実装
- [ ] 最新の`main`からfeatureブランチを作成
- [ ] データベースマイグレーションを作成（必要な場合）
- [ ] バリデーション付きPydanticスキーマを実装
- [ ] データベースモデルを実装（必要な場合）
- [ ] サービス層関数を実装
- [ ] FastAPIエンドポイントを実装
- [ ] 包括的なエラーハンドリングを追加
- [ ] 単体テストを作成（≥75%カバレッジ、95%を目指す）
- [ ] リンター実行（ruff check）
- [ ] フォーマッター実行（ruff format）
- [ ] 型チェッカー実行（mypy）
- [ ] ローカルで全テストが通過
- [ ] 明確な説明でPR作成
- [ ] CI/CDが通過
- [ ] PRマージとブランチ削除

### UI実装
- [ ] API実装が`main`にマージ済み
- [ ] 最新の`main`からfeatureブランチを作成
- [ ] TypeScript型を実装
- [ ] APIクライアント関数を実装
- [ ] Reactコンポーネントを実装
- [ ] コンポーネントをページに統合
- [ ] フォームバリデーションとエラーハンドリングを追加
- [ ] 単体テストを作成（≥75%カバレッジ、95%を目指す）
- [ ] リンター実行（npm run lint）
- [ ] フォーマッター実行（npm run format）
- [ ] 型チェッカー実行（npm run type-check）
- [ ] ビルド成功（npm run build）
- [ ] ローカルで全テストが通過
- [ ] 明確な説明でPR作成
- [ ] CI/CDが通過
- [ ] PRマージとブランチ削除

### 実装後
- [ ] 統合テスト完了
- [ ] ドキュメント更新（必要な場合）
- [ ] ステークホルダーに完了を通知

## タスク優先順位付けガイド

複数のタスクがある場合、以下の順序で優先順位を付けます：

### 優先度1: データベース基盤
- データベーススキーマ設計
- コアテーブル作成（users, servers など）
- マイグレーションインフラ設定

**根拠**: 全ての機能がデータベーススキーマに依存します。

### 優先度2: 認証・認可
- ユーザー登録とログイン
- JWTトークン管理
- PBAC（Permission-Based Access Control）システム

**根拠**: ほとんどの機能が認証・認可を必要とします。

### 優先度3: コア機能
- サーバー管理（起動、停止、ステータス）
- ファイル管理（アップロード、ダウンロード、スナップショット）
- ログ閲覧

**根拠**: これらが主な価値提供機能です。

### 優先度4: サポート機能
- WebSocket通知
- 管理者によるユーザー管理
- 監査ログ

**根拠**: コア機能を強化するが、ブロッカーではない。

### 優先度5: UI/UX強化
- ダッシュボードの洗練
- レスポンシブデザイン改善
- アクセシビリティ機能

**根拠**: コア機能が安定した後に実装。

## 質問すべき場合

以下の状況では**必ず質問してください**：

### 仕様の不確実性
- [ ] 機能がARCHITECTURE.mdにドキュメント化されていない
- [ ] 仕様が既存実装と矛盾している
- [ ] 複数の有効な解釈が存在する

### 技術的不確実性
- [ ] 複数の実装アプローチが可能
- [ ] セキュリティへの影響がある（パスワード、認証、権限）
- [ ] パフォーマンス/スケーラビリティの懸念がある
- [ ] 既存の設計パターンが要件に適合しない

### 範囲の不確実性
- [ ] タスク範囲が曖昧または広すぎる
- [ ] 何が「完了」かが不明確
- [ ] API、UI、または両方を実装すべきか不明確
- [ ] 依存関係が不明確

### 良い質問の例

```markdown
質問: ユーザー登録API - 承認ワークフロー

ユーザー登録APIを実装中ですが、ARCHITECTURE.mdに「管理者承認ワークフロー」
の記載があります。これは今実装すべきでしょうか、それとも別タスクでしょうか？

選択肢:
A. 今フルワークフローを実装（ユーザーは'pending'で開始、管理者が承認）
B. 承認をスキップ（ユーザーは自動承認）
C. データベースサポートは追加するがAPIエンドポイントはまだ

どのアプローチを取るべきでしょうか？
```

```markdown
質問: パスワードバリデーションルール

タスクに「パスワードバリデーションを追加」とありますが、ルールが指定されていません。
要件は何でしょうか？

- 最小長は？
- 文字要件（大文字、数字、記号）は？
- 最大長は？
- 禁止パターン（一般的なパスワード、ユーザー名を含む）は？

OWASP推奨に従うべきでしょうか、それとも特定の要件がありますか？
```

## ベストプラクティス

### すべきこと ✅

- **まずARCHITECTURE.mdを読む** - 情報源です
- **早めに質問する** - 詰まってから質問しない
- **既存パターンに従う** - 類似機能の実装方法を確認
- **テストを先に書く** - TDDは要件を明確にします
- **PRを小さく保つ** - レビューとマージが容易
- **ドキュメントを更新** - ドキュメントとコードを同期
- **CIチェックをローカルで実行** - GitHub Actionsに依存しない

### してはいけないこと ❌

- **要件を推測しない** - 必ずステークホルダーと明確化
- **APIとUIを一緒に実装しない** - 別ブランチ、別PR
- **テストをスキップしない** - 最低75%カバレッジが強制
- **コード品質チェックをスキップしない** - リンティング、フォーマッティング、型チェックは必須
- **マイグレーションを手動作成しない** - `alembic revision --autogenerate`を使用
- **テストなしでコミットしない** - ローカルでテストを実行
- **失敗したCIでPRをマージしない** - まず問題を修正

## よくある落とし穴

### 落とし穴0: mainブランチで直接作業する

**問題**: featureブランチを使わずに`main`ブランチに直接コミットする。

**解決策**:
- 作業開始前に必ず`git branch`で現在のブランチを確認
- `main`に直接コミットしない（ブランチ保護で防止されるはず）
- featureブランチを作成: `git checkout -b feature/api-<名前>`
- 誤って`main`にいる場合は、すぐに切り替えて適切なブランチを作成

### 落とし穴1: 理解せずに実装

**問題**: 仕様や既存コードを確認せずにすぐコーディングを開始。

**解決策**: コードを書く前に必ずステップ0（タスク理解）を完了してください。

### 落とし穴2: APIとUIの実装を混在

**問題**: 同じブランチ/PRでバックエンドとフロントエンド両方を実装。

**解決策**: API優先（`main`にマージ）、次にUIを別ブランチ/PRで。

### 落とし穴3: データベーススキーマ確認のスキップ

**問題**: テーブル/カラムが既に存在するか確認せずにマイグレーション作成。

**解決策**: 必ず`alembic history`を実行し、既存スキーマを先に確認してください。

### 落とし穴4: 要件の仮定

**問題**: バリデーションルール、エラーハンドリング、ビジネスロジックについて仮定する。

**解決策**: 明確化のための質問をしてください。ARCHITECTURE.md仕様を参照してください。

### 落とし穴5: テストカバレッジ不足

**問題**: 最小限のテストのみ書いて75%カバレッジ要件を満たせない。

**解決策**: 全てのコードパスのテストを書いてください。95%カバレッジを目指してください。

### 落とし穴6: 既存パターンの無視

**問題**: 既存コードと異なる方法で機能を実装（命名、構造、エラーハンドリング）。

**解決策**: Grep/Globで類似機能を検索してください。確立されたパターンに従ってください。

### 落とし穴7: ローカルCIチェックのスキップ

**問題**: リンター、フォーマッター、型チェッカー、テストをローカルで実行せずにプッシュ。

**解決策**: プッシュ前に全てのチェックをローカルで実行してください。pre-commitフックを使用してください。

## まとめ

**実装ワークフローを一文で**:
> タスクと現状を理解し（ステップ0）、アプローチを分析し（ステップ1）、API優先で実装し（ステップ2）、UIを別途実装し（ステップ3）、統合を確認する（ステップ4）。

**主要原則**:
1. **推測しない** - 不明な点は必ず質問
2. **APIとUIは分離** - 別ブランチ、別PR
3. **ARCHITECTURE.mdが情報源** - 仕様に従う
4. **テストは必須** - 最低75%、95%を目指す
5. **コード品質を重視** - リンティング、フォーマッティング、型チェックが必要

**重要**: 不確実な場合に質問して要件を明確化する方が、間違った機能を実装するよりも良いです。タスクを理解するために時間をかけることは、長期的には時間を節約します。

---

**最終更新日**: 2025-12-30
