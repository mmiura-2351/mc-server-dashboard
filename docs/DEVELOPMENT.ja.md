# 開発環境セットアップ

**最終更新日**: 2025-12-28

## 目的

このドキュメントは、Minecraft Server Dashboardプロジェクトの開発環境セットアップ手順を説明します。

## 前提条件

開発環境をセットアップする前に、以下がインストールされていることを確認してください。

### 必須

- **Docker**: バージョン20.10以上（Docker Compose V2対応）
- **Git**: バージョン2.30以上
- **テキストエディタ/IDE**: VS Code、IntelliJ IDEA、または類似のもの

### オプション（Dockerを使わないローカル開発の場合）

- **Python**: 3.13以上
- **uv**: 最新バージョン（Pythonパッケージマネージャー）
- **Node.js**: 20.0以上
- **npm**: 10.0以上
- **PostgreSQL**: 16以上

## プロジェクト構造

```
mc-server-dashboard/
├── api/                          # バックエンド (Python + FastAPI)
│   ├── src/app/                  # アプリケーションコード
│   ├── tests/                    # テストコード
│   ├── alembic/                  # データベースマイグレーション
│   ├── pyproject.toml            # Python依存関係とツール設定
│   ├── alembic.ini               # Alembic設定
│   ├── Dockerfile                # バックエンドコンテナ定義
│   └── .dockerignore
│
├── ui/                           # フロントエンド (Next.js + React)
│   ├── src/app/                  # App Router構造
│   ├── public/                   # 静的ファイル
│   ├── package.json              # npm依存関係
│   ├── tsconfig.json             # TypeScript設定
│   ├── next.config.ts            # Next.js設定
│   ├── .eslintrc.json            # ESLint設定
│   ├── .prettierrc.json          # Prettier設定
│   ├── vitest.config.ts          # Vitest設定
│   ├── Dockerfile                # フロントエンドコンテナ定義
│   └── .dockerignore
│
├── docs/                         # ドキュメント
├── compose.yaml                  # Docker Compose V2設定
├── .env.example                  # 環境変数テンプレート
└── .gitignore
```

## クイックスタート（Docker Compose - 推奨）

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd mc-server-dashboard
```

### 2. 環境ファイルの作成

```bash
cp .env.example .env
```

`.env`を編集して必要に応じて値を更新します（開発環境では任意）。

### 3. 全サービスの起動

```bash
docker compose up -d
```

以下が起動します:
- **PostgreSQL** ポート5432
- **バックエンドAPI** ポート8000
- **フロントエンドUI** ポート3000

### 4. サービスの確認

```bash
docker compose ps
```

すべてのサービスが「Up」ステータスで表示されるはずです。

### 5. アプリケーションへのアクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs

### 6. ログの表示

```bash
# 全サービス
docker compose logs -f

# 特定のサービス
docker compose logs -f api
docker compose logs -f ui
```

### 7. サービスの停止

```bash
docker compose down
```

ボリュームも削除する場合（データベースデータも削除）:

```bash
docker compose down -v
```

---

## ローカル開発セットアップ（Dockerなし）

### バックエンド（Python + FastAPI）

#### 1. APIディレクトリへ移動

```bash
cd api
```

#### 2. uvのインストール（未インストールの場合）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. 仮想環境の作成と依存関係のインストール

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

uv pip install -e ".[dev]"
```

#### 4. 環境変数の設定

```bash
export DATABASE_URL="postgresql+asyncpg://mcadmin:mcpassword@localhost:5432/mc_dashboard"
export SECRET_KEY="your-secret-key-change-in-production"
```

#### 5. PostgreSQLの起動（Dockerを使わない場合）

PostgreSQL 16以上がローカルのポート5432で起動していることを確認してください。

#### 6. データベースマイグレーションの実行

```bash
alembic upgrade head
```

#### 7. 開発サーバーの起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 8. テストの実行

```bash
pytest
```

#### 9. リンターとフォーマッターの実行

```bash
ruff check .
ruff format .
```

#### 10. 型チェック

```bash
mypy app
```

---

### フロントエンド（Next.js + React）

#### 1. UIディレクトリへ移動

```bash
cd ui
```

#### 2. 依存関係のインストール

```bash
npm install
```

#### 3. 環境変数の設定

`.env.local`を作成:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4. 開発サーバーの起動

```bash
npm run dev
```

#### 5. テストの実行

```bash
npm run test
```

#### 6. リンターの実行

```bash
npm run lint
```

#### 7. フォーマッターの実行

```bash
npm run format
```

#### 8. 型チェック

```bash
npm run type-check
```

#### 9. 本番ビルド

```bash
npm run build
npm start
```

---

## データベース管理

### PostgreSQLへのアクセス

```bash
# Docker Composeを使う場合
docker compose exec postgres psql -U mcadmin -d mc_dashboard

# ローカルPostgreSQL
psql -U mcadmin -d mc_dashboard
```

### 新しいマイグレーションの作成

```bash
cd api
alembic revision --autogenerate -m "変更内容の説明"
```

### マイグレーションの適用

```bash
alembic upgrade head
```

### マイグレーションのロールバック

```bash
alembic downgrade -1
```

---

## よくある開発タスク

### Dockerイメージの再ビルド

```bash
docker compose build
docker compose up -d
```

### データベースのリセット

```bash
docker compose down -v
docker compose up -d
```

### Python依存関係の追加

```bash
cd api
uv pip install <package-name>
# pyproject.tomlを手動で更新
```

### npm依存関係の追加

```bash
cd ui
npm install <package-name>
```

---

## トラブルシューティング

### ポートが既に使用中

ポート3000、5432、8000が既に使用中の場合、`.env`で変更できます:

```bash
API_PORT=8001
UI_PORT=3001
POSTGRES_PORT=5433
```

### Dockerソケットのパーミッション拒否

ユーザーが`docker`グループに所属していることを確認:

```bash
sudo usermod -aG docker $USER
```

その後、ログアウトして再度ログインしてください。

### データベース接続拒否

PostgreSQLが起動しアクセス可能であることを確認:

```bash
docker compose ps postgres
docker compose logs postgres
```

### ホットリロードが動作しない

Dockerでファイル変更が検出されない場合:

```bash
# 再ビルドと再起動
docker compose down
docker compose build
docker compose up -d
```

---

## IDE設定の推奨事項

### VS Code

推奨拡張機能:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Docker (ms-azuretools.vscode-docker)

### PyCharm / IntelliJ IDEA

1. Pythonプラグインを有効化
2. Pythonインタープリタを`.venv/bin/python`に設定
3. フォーマットとリントにRuffを有効化
4. TypeScriptフォーマットにPrettierを有効化

---

## 次のステップ

開発環境のセットアップ後:

1. [PHILOSOPHY.md](PHILOSOPHY.md)を確認してプロジェクトの価値観を理解する
2. [ARCHITECTURE.md](ARCHITECTURE.md)を読んでシステム設計を学ぶ
3. [CODING_STANDARDS.md](CODING_STANDARDS.md)でコード規約を確認する
4. [WORKFLOW.md](WORKFLOW.md)でGitワークフローとブランチ戦略に従う
5. `docs/`の仕様に基づいて機能の実装を開始する

---

## 追加リソース

- [FastAPIドキュメント](https://fastapi.tiangolo.com/)
- [Next.jsドキュメント](https://nextjs.org/docs)
- [Docker Composeドキュメント](https://docs.docker.com/compose/)
- [uvドキュメント](https://docs.astral.sh/uv/)
- [Ruffドキュメント](https://docs.astral.sh/ruff/)
