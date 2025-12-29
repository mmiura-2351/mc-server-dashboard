# 開発環境セットアップ

**最終更新日**: 2025-12-30

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

## ⚠️ セキュリティに関する重要な注意事項

### Dockerソケットの露出について

開発環境の`compose.yaml`では、DockerベースのMinecraftサーバー起動戦略（Docker-in-Docker、Docker-out-of-Docker）をサポートするため、
Dockerソケット（`/var/run/docker.sock`）をAPIコンテナにマウントしています。

**これは以下のセキュリティリスクを伴います**：

- **ホストへのroot権限アクセス**: コンテナがホストのDockerデーモンにフルアクセス可能
- **コンテナエスケープのリスク**: 悪意のあるコードがコンテナから脱出してホストシステムを侵害可能
- **権限昇格の可能性**: コンテナ内のプロセスが実質的にホストのroot権限を取得可能

**開発環境での使用**：信頼できる開発者のローカル環境でのみ許容されます。

**本番環境では絶対に使用しないでください。**

### 本番環境での推奨セキュリティ対策

本番環境では、以下のいずれかの方法を使用してください：

#### 1. Docker Socket Proxy（推奨）

特定のDocker API操作のみを許可するプロキシを使用：

```yaml
# compose.prod.yaml
services:
  docker-socket-proxy:
    image: tecnativa/docker-socket-proxy:latest
    environment:
      CONTAINERS: 1  # コンテナ操作を許可
      IMAGES: 1      # イメージ操作を許可
      POST: 1        # POST リクエストを許可
      BUILD: 0       # ビルドは拒否
      EXEC: 0        # exec は拒否（重要）
      VOLUMES: 1     # ボリューム操作を許可
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - mc-dashboard-network

  api:
    environment:
      DOCKER_HOST: tcp://docker-socket-proxy:2375  # プロキシ経由で接続
    # volumes:
    #   - /var/run/docker.sock:/var/run/docker.sock  # 直接マウント削除
```

**メリット**：
- 最小権限の原則に従った細かい権限制御
- パフォーマンスへの影響がほぼゼロ
- アプリケーションコードの変更不要（環境変数`DOCKER_HOST`のみ）

#### 2. Rootless Docker

ホスト側でRootless Dockerを使用：

```bash
# ホスト側でRootless Dockerをセットアップ
dockerd-rootless-setuptool.sh install
systemctl --user enable docker
systemctl --user start docker
```

**メリット**：
- ホストへのroot権限不要
- コンテナエスケープのリスクを大幅に低減
- パフォーマンスへの影響は5%未満

#### 3. Docker Remote API with TLS

TLS認証付きのDocker Remote APIを使用：

```yaml
api:
  environment:
    DOCKER_HOST: tcp://docker-host:2376
    DOCKER_TLS_VERIFY: 1
    DOCKER_CERT_PATH: /certs
  volumes:
    - ./certs:/certs:ro
```

**メリット**：
- ネットワーク経由でのDocker制御（リモート実行可能）
- TLS証明書による認証・暗号化
- 物理的なソケット露出を回避

### 移行計画

現在のDocker-out-of-Docker（DooD）実装から本番環境用のセキュアな構成への移行は非常に簡単です：

1. **アプリケーションコード**：Pythonの`docker.from_env()`を使用（環境変数から自動設定）
2. **開発環境**：現在の`compose.yaml`を継続使用
3. **本番環境**：`compose.prod.yaml`を作成し、上記のいずれかの方法を実装

**コード変更は不要**で、設定ファイルの変更のみで移行できます。

### 参考情報

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Rootless Docker](https://docs.docker.com/engine/security/rootless/)
- [Docker Socket Proxy](https://github.com/Tecnativa/docker-socket-proxy)

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

## CI環境のセットアップ

### Pre-commitフック

Pre-commitフックは、コミット前にコード品質を確保します。リンター、フォーマッター、型チェッカーを自動的に実行します。

#### 自動セットアップ（推奨）

プロジェクトルートからセットアップスクリプトを実行:

```bash
./scripts/setup-hooks.sh
```

このスクリプトは以下を実行します:
1. バックエンドのpre-commitフック（Ruff、mypy）をインストールと設定
2. フロントエンドのhuskyフック（ESLint、Prettier）をインストールと設定
3. 全ファイルに対して初回チェックを実行

#### 手動セットアップ

**バックエンド（pre-commit）:**

```bash
# pre-commitをインストール
pip install pre-commit

# gitフックをインストール
pre-commit install

# 全ファイルに対して実行（オプション）
pre-commit run --all-files
```

**フロントエンド（husky + lint-staged）:**

```bash
cd ui

# 依存関係をインストール（huskyとlint-stagedを含む）
npm install

# huskyを初期化
npm run prepare
```

### チェック内容

**バックエンド（コミット時）:**
- Ruffリンター・フォーマッター（Pythonコードスタイル）
- mypy型チェッカー（静的型チェック）
- 一般的なファイルチェック（末尾の空白、YAML/JSON構文）

**フロントエンド（コミット時）:**
- ESLint（TypeScript/Reactリント）
- Prettier（コードフォーマット）
- ステージされたファイルのみをチェック

### GitHub Actions CI

全てのプッシュとプルリクエストで自動CIチェックがトリガーされます:

#### バックエンドCI（`backend-ci.yml`）
- Ruffによるリント
- mypyによる型チェック
- pytestによるユニットテスト
- カバレッジチェック（≥75%必須）

#### フロントエンドCI（`frontend-ci.yml`）
- ESLintによるリント
- Prettierによるフォーマットチェック
- TypeScriptによる型チェック
- Vitestによるユニットテスト
- カバレッジチェック（≥75%必須）
- Next.jsによるビルド検証

#### Docker CI（`docker-ci.yml`）
- Docker Composeビルド検証
- サービスヘルスチェック（API、UI、PostgreSQL）
- hadolintによるDockerfileリント

### CIチェックをローカルで実行

**バックエンド:**

```bash
cd api

# リント
ruff check .

# フォーマットチェック
ruff format --check .

# 型チェック
mypy src/

# カバレッジ付きテスト
pytest --cov --cov-report=term-missing
```

**フロントエンド:**

```bash
cd ui

# リント
npm run lint

# フォーマットチェック
npm run format:check

# 型チェック
npm run type-check

# カバレッジ付きテスト
npm run test:coverage

# ビルド
npm run build
```

**Docker:**

```bash
# 全サービスをビルド・検証
docker compose build
docker compose up -d

# ヘルスチェック
curl http://localhost:8000/health
curl http://localhost:3000

# ログ確認
docker compose logs

# クリーンアップ
docker compose down -v
```

### カバレッジ要件

- **目標**: 95%（ARCHITECTURE.mdからの理想的な目標）
- **CI最小値**: 75%（GitHub Actionsで強制）
- **現実**: 75-80%（CLAUDE.mdによる）

カバレッジが75%未満の場合、CIは失敗します。

### CIのトラブルシューティング

**Pre-commitフックが失敗する:**

```bash
# フックを最新バージョンに更新
pre-commit autoupdate

# キャッシュをクリアして再試行
pre-commit clean
pre-commit run --all-files
```

**Huskyが実行されない:**

```bash
cd ui
rm -rf .husky
npm run prepare
```

**CIが失敗するがローカルでは成功する:**

- 全ての変更をコミットしたことを確認
- `pyproject.toml`と`package.json`の依存関係が最新であることを確認
- `.github/workflows/*.yml`の構文を検証

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
