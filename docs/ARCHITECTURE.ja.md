# アーキテクチャ設計

## 目的

このドキュメントは、Minecraft Server Dashboardのシステム全体のアーキテクチャ、技術スタック、コンポーネント構造、設計判断を記述します。

## システム概要

Minecraft Server Dashboardは、以下を目的としたWebベースの管理アプリケーションです：
- 複数のMinecraftサーバーの管理（起動/停止/コマンド実行）
- 複数のサーバー起動戦略のサポート（ホストプロセス、Docker-in-Docker、Docker-out-of-Docker）
- ロールバック機能付きバージョン管理の提供
- ロールベースのアクセス制御と承認ワークフローによる複数ユーザーサポート
- 設定可能な保持ポリシーによる自動バックアップの処理
- RCON同期を伴うプレイヤーグループ（OP/ホワイトリスト）の管理
- 高速なサーバー作成のためのMinecraftバージョン情報のキャッシュ
- サブドメインベースのネットワーキングによるMinecraftトラフィックのルーティング（将来機能）

### 想定規模
- **同時接続ユーザー数**: 10-100ユーザー（中規模）
- **管理サーバー数**: インスタンスあたり複数のMinecraftサーバー
- **デプロイ環境**: Docker/Kubernetesおよびローカルマシン

### プラットフォームサポート

**オペレーティングシステム**:
- **Linux**: 完全サポート（主要プラットフォーム）
- **Windows**: 部分的サポート
  - ✅ **Docker-out-of-Docker (DooD)**: サポート（Docker Desktop for Windowsの名前付きパイプ経由）
  - ✅ **ホストプロセス**: サポート（Windowsに特化したパス処理付き）
  - ⚠️ **Docker-in-Docker (DinD)**: 優先度低（WSL2バックエンド必須、特権モードの制限あり）

**Windows実装の注意点**:
- **パス処理**: クロスプラットフォームのパス区切り文字（`/` vs `\`）
- **Dockerソケット**: Unixソケット（`/var/run/docker.sock`） vs 名前付きパイプ（`//./pipe/docker_engine`）
- **プロセス管理**: systemdデーモンではなくWindowsサービス

**優先度**: DooDとホストプロセス戦略がWindows対応を先に受ける。DinDは後回し。

### クライアントサポート

**Web UIレスポンシブデザイン**:
- **デスクトップ**: 全機能（主要ターゲット）
- **タブレット**: 中程度のサポート（基本操作）
- **モバイル**: 優先度低（閲覧専用機能推奨）

**設計哲学**: デスクトップファーストアプローチ
- 複雑な操作（ファイル編集、高度な設定）はデスクトップ向けに最適化
- シンプルな操作（サーバー起動/停止、ステータス監視）は全デバイスでアクセス可能

## アーキテクチャスタイル

**完全分離された3層アーキテクチャ**

```
┌─────────────────────────────────────────────────────────────┐
│                      クライアント                              │
│              (Webブラウザ、モバイルデバイス)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌──────────────────┐
│  フロントエンド  │            │  Minecraft       │
│  SSR (Next.js)  │            │  クライアント     │
└────────┬────────┘            └────────┬─────────┘
         │                               │
         │ REST API + ポーリング          │
         │                               │
         ▼                               │
┌─────────────────────────────────────────┐
│        バックエンドAPIサーバー            │
│        (FastAPI + Python)               │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  ネットワーク層（将来実装）        │  │
│  │  - サブドメインルーティング        │  │
│  │  - Minecraftプロトコルプロキシ     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Minecraftサーバーマネージャー     │◄─┘
│  │  (Strategy Pattern)              │
│  │  - ホストプロセス起動             │
│  │  - Docker-in-Docker起動          │
│  │  - Docker-out-of-Docker起動      │
│  │  - RCON通信                      │
│  │  - ログ監視                       │
│  └──────────────────────────────────┘  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        データ層                          │
│  ┌──────────────────────────────────┐  │
│  │         PostgreSQL               │  │
│  │  (メインDB、バージョン履歴、       │  │
│  │   ユーザーデータ、バックアップ    │  │
│  │   スケジュール)                   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 技術スタック

### バックエンドAPI

**フレームワーク**: Python 3.13+ + FastAPI 0.115+

**選定理由**:
- **非同期ファースト**: 高パフォーマンスI/OのためのネイティブAsyncioサポート
- **実証済みソリューション**: 既存実装は本番環境対応済み
- **高速開発**: 自動APIドキュメント生成を伴うPythonのシンプルさ
- **型安全性**: Pydanticモデルがデータ検証を強制
- **プロセス管理**: 優れたサブプロセスとデーモンプロセスサポート

**主要ライブラリ**:
- `fastapi`: 非同期Webフレームワーク
- `uvicorn`: ASGIサーバー
- `sqlalchemy`: 非同期サポート付きデータベースORM
- `alembic`: データベースマイグレーションツール
- `pydantic`: データ検証と設定管理
- `python-jose`: JWTトークン処理
- `passlib[bcrypt]`: パスワードハッシュ化
- `modern-rcon`: RCONプロトコルクライアント
- `docker`: コンテナ管理用Docker APIクライアント
- `psutil`: プロセス監視とシステム情報
- `aiofiles`: 非同期ファイル操作

### フロントエンド

**フレームワーク**: Next.js 15+ (App Router) + React 19+ + TypeScript

**選定理由**:
- **SSR + CSRハイブリッド**: クライアントサイドインタラクティビティを伴うサーバーサイドレンダリング
- **型安全性**: 保守性のためのTypeScript
- **開発者体験**: 優れたツールとエコシステム
- **本番環境対応**: 組み込みの最適化

**主要ライブラリ**:
- `react`: UIライブラリ
- `typescript`: 型安全性
- `neverthrow`: エラーハンドリング用Result型
- カスタムContext API（状態管理: auth、connection、language）
- CSSモジュール: コンポーネントスコープのスタイリング
- `DOMPurify`: XSS防止

**状態管理**:
- React Context API（軽量、Redux/Zustand不要）
- 3つのcontext: Auth、Connection Monitoring、Language（i18n）

### データベース

**メインデータベース**: PostgreSQL 16+

**選定理由**:
- **リレーショナルデータ**: ユーザー、サーバー、権限、バージョン履歴
- **ACID準拠**: 重要なデータに対して信頼性が高い
- **スケーラビリティ**: 中規模（10-100ユーザー）に容易に対応
- **豊富な機能**: JSONカラム、全文検索、高度なインデックス作成
- **本番グレード**: マルチユーザー環境でSQLiteより優れている

**スキーマハイライト**:
- 承認ワークフロー付きユーザー管理（`is_approved`フラグ）
- セキュアな認証のためのリフレッシュトークンストレージ
- ファイルとワールドバックアップのバージョン履歴（統一スナップショットシステム）
- 保持ポリシー付きバックアップスケジュール
- RCON同期を伴うグループ管理（OP/ホワイトリスト）
- Minecraftバージョンキャッシュ（Vanilla、Paper、Forge）
- Java互換性マトリックス（起動戦略に基づく条件付き）

**マイグレーションツール**: Alembic
- バージョン管理されたスキーマ変更
- モデルからの自動マイグレーション生成
- ロールバックサポート

### Minecraftサーバーコンテナ

**Dockerイメージ**: `itzg/minecraft-server`

**選定理由**:
- **複数タイプのサポート**: Vanilla、Paper、Forge、Fabric、Spigot、Bukkitなど
- **バージョンの柔軟性**: 環境変数で任意のMinecraftバージョンを指定可能
- **よくメンテナンスされている**: アクティブなコミュニティサポートと定期的な更新
- **機能豊富**: 環境変数による広範な設定オプション

**使用例**:
```bash
docker run -e TYPE=PAPER -e VERSION=1.20.4 itzg/minecraft-server
```

**サポートされているサーバータイプ**（`TYPE`環境変数経由）:
- `VANILLA`: 公式Mojangサーバー
- `PAPER`: Paper（高性能フォーク）
- `FORGE`: Forge（MODサポート）
- `FABRIC`: Fabric（軽量MODサポート）
- `SPIGOT`: Spigot
- `PURPUR`: Purpur
- その他: Mohist、Magmaなど

### リアルタイム通信

**アプローチ**: ポーリングベース（WebSocketではない）

**選定理由**:
- よりシンプルなデプロイ（WebSocketアップグレード処理が不要）
- 現在のユースケースに十分（ステータス更新、ログストリーミング）
- 既存実装は遷移中の2秒ポーリングで良好に機能している

**将来の検討**: 必要に応じて後でWebSocketを追加可能

---

## コンポーネントアーキテクチャ

### バックエンドコンポーネント

```
backend/
├── api/                    # REST APIエンドポイント
│   ├── auth/              # 認証・認可
│   ├── users/             # ユーザー管理（承認ワークフロー）
│   ├── servers/           # MinecraftサーバーCRUD
│   ├── logs/              # ログ取得
│   ├── backups/           # バックアップ管理
│   ├── groups/            # OP/ホワイトリストグループ
│   ├── versions/          # Minecraftバージョンキャッシュ
│   └── snapshots/         # バージョン履歴（ファイル + ワールド）
├── services/              # ビジネスロジック層
│   ├── server_manager/    # サーバーライフサイクル管理
│   ├── launch_strategy/   # サーバー起動のStrategy pattern
│   │   ├── host_process.py      # 直接ホストプロセス起動
│   │   ├── docker_in_docker.py  # DinD起動
│   │   └── docker_out_docker.py # DooD起動
│   ├── backup_scheduler/  # スケジュールされたバックアップサービス
│   ├── version_cache/     # Minecraftバージョン管理
│   ├── snapshot_service/  # 統一バージョニングシステム
│   └── group_sync/        # RCONグループ同期
├── models/                # データベースモデル
│   ├── user.py           # User、RefreshToken
│   ├── server.py         # Server、ServerConfig
│   ├── snapshot.py       # 統一バージョン履歴
│   ├── backup.py         # Backup、BackupSchedule
│   ├── group.py          # Group、ServerGroup
│   └── version.py        # MinecraftVersion
├── core/                  # コアユーティリティ
│   ├── config.py         # 環境設定
│   ├── database.py       # DB接続管理
│   ├── security.py       # パス検証、サニタイゼーション
│   └── exceptions.py     # カスタム例外
└── middleware/            # （最小限 - パフォーマンス監視なし）
    └── cors.py           # CORS処理
```

### フロントエンドコンポーネント

```
frontend/
├── app/                   # Next.js App Router
│   ├── (auth)/           # 認証ページ（ログイン、登録）
│   ├── dashboard/        # メインダッシュボード
│   ├── servers/          # サーバー管理ページ
│   │   ├── [id]/        # 個別サーバー詳細
│   │   └── new/         # 新規サーバー作成
│   ├── groups/           # グループ管理
│   ├── users/            # ユーザー管理（管理者）
│   └── settings/         # 設定
├── components/           # 再利用可能なコンポーネント
│   ├── ui/              # 基本UIコンポーネント
│   ├── server/          # サーバー関連コンポーネント
│   ├── groups/          # グループ管理UI
│   └── snapshots/       # バージョン履歴UI
├── contexts/             # React Context実装
│   ├── auth.tsx         # 認証 + 承認ステータス
│   ├── connection.tsx   # API接続監視（最小限）
│   └── language.tsx     # i18n（英語 + 日本語）
├── services/             # API通信
│   ├── api.ts           # Result型を伴うベースfetchラッパー
│   ├── server.ts        # サーバーAPI呼び出し
│   ├── auth.ts          # 認証API呼び出し
│   ├── groups.ts        # グループ管理API
│   └── snapshots.ts     # バージョン履歴API
├── utils/                # ユーティリティ
│   ├── token-manager.ts # JWTトークンライフサイクル
│   ├── input-sanitizer.ts # XSS/インジェクション防止
│   └── secure-storage.ts  # 安全なlocalStorageラッパー
└── i18n/                 # 国際化
    └── messages/         # 英語 + 日本語翻訳
        ├── en.json
        └── ja.json
```

---

## 主要機能と設計判断

### 1. Minecraftサーバー起動戦略（Strategy Pattern）

**重要な機能**: 複数の起動方法のサポート

```python
class ServerLaunchStrategy(ABC):
    @abstractmethod
    async def start(self, server_config: ServerConfig) -> Process:
        """Minecraftサーバーを起動"""
        pass

    @abstractmethod
    async def stop(self, server_id: str) -> None:
        """Minecraftサーバーを停止"""
        pass

    @abstractmethod
    async def get_status(self, server_id: str) -> ServerStatus:
        """サーバーステータスを取得"""
        pass

class HostProcessStrategy(ServerLaunchStrategy):
    """ホストプロセスとして起動（ダブルフォークデーモン）"""
    # PIDファイル追跡、API再起動を生き延びる

class DockerInDockerStrategy(ServerLaunchStrategy):
    """APIコンテナ内でDockerコンテナを起動"""
    # 特権モードが必要

class DockerOutOfDockerStrategy(ServerLaunchStrategy):
    """ソケットマウント経由でホスト上のDockerコンテナを起動"""
    # /var/run/docker.sockをマウント
```

**選択ロジック**:
- **システム全体の設定**: アプリケーション全体で1つの起動戦略を使用
- 環境変数で設定: `DEFAULT_LAUNCH_STRATEGY=host|dind|dood`
- 全サーバーが同じ戦略を使用（初期実装ではサーバーごとの選択なし）
- **戦略変更**: 将来機能（DBでフラグ変更のみ、次回サーバー起動時に適用）

**Java互換性**:
- Java互換性マトリックスはHostProcessStrategyにのみ適用
- Docker戦略（DinD/DooD）は `itzg/minecraft-server` イメージに含まれるJavaを使用

---

### 2. Java互換性マトリックス（HostProcessStrategyのみ）

**目的**: ホストプロセスとして起動するMinecraftサーバーのJavaバージョン自動選択

**Minecraftバージョン → Javaバージョン対応表**:
```
Minecraftバージョン    | 必要なJavaバージョン
----------------------|---------------------
~ 1.7.9               | Java 7
1.7.10 ~ 1.16.5       | Java 8
1.17 ~ 1.17.1         | Java 16
1.18 ~ 1.20.4         | Java 17
1.20.5 ~              | Java 21
```

**Java検出ロジック**（HostProcessStrategyのみ）:
1. まず `.env` 設定を確認:
   ```bash
   JAVA_8_PATH=/usr/lib/jvm/java-8-openjdk-amd64/bin/java
   JAVA_16_PATH=/usr/lib/jvm/java-16-openjdk-amd64/bin/java
   JAVA_17_PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin/java
   JAVA_21_PATH=/usr/lib/jvm/java-21-openjdk-amd64/bin/java
   ```
2. `.env` にない場合、標準パスを確認:
   ```bash
   /usr/lib/jvm/java-{7,8,16,17,21}-openjdk-amd64/bin/java
   ```
3. API起動時に全Javaバージョンの検出を実行
4. 検証用のJava検出APIエンドポイントを提供

**エラーハンドリング**:
- 必要なJavaバージョンが見つからない場合 → サーバー作成リクエスト時にエラー返却
- 異なるJavaバージョンへのフォールバックなし（互換性問題のため）

**注意**: Paper/Forge/FabricもVanillaと同じJava要件

---

### 3. 統一スナップショットシステム（バージョン管理）

**目的**: ファイルとワールドバックアップの共通バージョニング

**データモデル**:
```sql
Snapshot (
  id UUID PRIMARY KEY,
  resource_type ENUM('file', 'world', 'server_full'),
  resource_identifier VARCHAR,  -- ファイルパスまたはサーバーID
  version_number INTEGER,
  snapshot_type ENUM('manual', 'scheduled', 'auto_save', 'pre_update'),
  storage_path VARCHAR,  -- 実際のバックアップファイルの場所
  file_size BIGINT,
  metadata JSONB,  -- リソース固有のデータ
  created_by INTEGER FK(User),
  created_at TIMESTAMP
)
```

**機能**:
- 任意の以前のバージョンへのロールバック
- 設定可能な保持（リソースあたりの最大バージョン数）
- 古いスナップショットの自動クリーンアップ
- 更新前スナップショット（Minecraftバージョンアップグレード前）

---

### 4. サーバーステータスステートマシン

**目的**: 明確なサーバーライフサイクル状態と許可される操作を定義

**サーバー状態**:
```
- stopped     : サーバーは停止中
- starting    : サーバーは起動中（プロセス起動 → 準備完了）
- running     : サーバーは実行中（プレイヤー接続可能）
- stopping    : サーバーはシャットダウン中
- unknown     : サーバー状態が判定不可（一時的、再検出を行う）
```

**状態遷移**:
```
stopped  → starting   (start操作)
starting → running    (起動完了検出)
starting → stopped    (起動失敗 または force=True でのstop操作)
starting → unknown    (プロセス追跡不可)
running  → stopping   (stop操作)
running  → unknown    (プロセス追跡不可)
stopping → stopped    (シャットダウン完了検出)
stopping → unknown    (プロセス追跡不可)
unknown  → any state  (状態再検出)
```

**状態ごとの許可操作**:

| 状態      | start | stop | restart | RCON | 設定変更 | 削除 |
|-----------|-------|------|---------|------|----------|------|
| stopped   | ✅    | ❌   | ❌      | ❌   | ✅       | ✅   |
| starting  | ❌    | ✅*  | ❌      | ❌   | ❌       | ❌   |
| running   | ❌    | ✅   | ✅      | ✅   | ❌       | ❌   |
| stopping  | ❌    | ❌   | ❌      | ❌   | ❌       | ❌   |
| unknown   | ❌    | ❌   | ❌      | ❌   | ❌       | ❌   |

\* `starting` 状態でのstopは `force=True` パラメータが必要

**注意事項**:
- `unknown` は一時的な状態で、状態再検出により自動的に解決される
- `error` 状態なし（失敗は `stopped` 状態となり、エラーは別途ログに記録）
- 外部からのシャットダウン（Dockerコマンド、プロセスキル、ゲーム内 `/stop`）をサポート

---

### 5. 設定可能な制限付きバックアップスケジューラー

**3層制限システム**:

1. **アプリケーション最大値**: グローバル上限（例: 168時間間隔、最大30バックアップ）
2. **ユーザー最大値**: 管理者が設定するユーザーごとの上限（例: 72時間間隔、最大10バックアップ）
3. **サーバー設定値**: 実際の設定（ユーザー最大値 ≤ アプリ最大値 でなければならない）

**検証**:
```python
if server_config.backup_interval < user_limit.min_interval:
    raise ValidationError("ユーザー制限を超えています")
if user_limit.max_backups > app_config.MAX_BACKUPS:
    raise ValidationError("アプリケーション制限を超えています")
```

**バックアップタイミング**:
- **間隔ベース**: Minecraftサーバー起動後、N時間ごとにバックアップ
- 例: サーバー10:00 AM起動、間隔=6h → 4:00 PM、10:00 PMにバックアップ
- Minecraftサーバー再起動時にタイマーリセット

**API再起動時の動作**:
- Minecraftサーバーが実行中のままAPIが再起動した場合:
  - API起動時刻からタイマーを再計算
  - 例: APIが3:00 PMに再起動（間隔=6h） → 次回バックアップは9:00 PM
- API停止中のバックアップは実行されない（次の間隔までスキップ）

**バックアップ失敗時の処理**:
- 失敗したバックアップはデータベースに記録（`Snapshot` テーブルに `status: failed`）
- 失敗理由をmetadataに保存
- リトライロジックなし（次のスケジュール間隔まで待機）

**データベース永続化スケジューラー**:
- 設定を `BackupSchedule` テーブルに保存
- 実行用のインメモリタイマー
- バックグラウンドタスクでバックアップをチェック・実行

---

### 6. グループ管理（OP/ホワイトリスト）

**目的**: 集中型プレイヤー権限管理

**機能**:
- プレイヤーリスト（JSON配列）を持つグループの作成
- グループタイプ: `op`, `whitelist`
- 複数サーバーにグループを適用
- RCON同期: 変更後に`whitelist reload`
- テンプレートグループ（サーバー間で再利用可能）

**データモデル**:
```sql
Group (
  id, name, type, players JSONB, owner_id, is_template
)

ServerGroup (
  id, server_id FK, group_id FK, priority, attached_at
)
```

---

### 7. Minecraftバージョンキャッシュ

**目的**: 繰り返しの外部API呼び出しを回避

**プロセス**:
1. スケジュールされたタスクがMojang/PaperMC APIからバージョンを取得
2. `MinecraftVersion`テーブルに保存
3. サーバー作成UIはキャッシュから読み込み（高速）
4. 更新ログが変更を追跡

**データモデル**:
```sql
MinecraftVersion (
  id, server_type ENUM('vanilla', 'paper', 'forge'),
  version VARCHAR, download_url, release_date,
  is_stable BOOLEAN, build_number INTEGER,
  created_at, updated_at
)
```

---

### 8. ユーザー承認ワークフロー

**フロー**:
1. ユーザー登録 → `is_approved = False`
2. 管理者が新規ユーザーをレビュー
3. 管理者が承認 → `is_approved = True`
4. ユーザーがフルアクセスを取得

**データベース**:
```sql
User (
  id, username, email, hashed_password,
  role ENUM('admin', 'operator', 'user'),
  is_active BOOLEAN, is_approved BOOLEAN
)
```

---

### 9. リフレッシュトークン無効化

**セキュリティ機能**:
- データベースにリフレッシュトークンを保存
- ユーザーごとに1つのアクティブトークン
- ログアウトまたは新規ログイン時にトークンを無効化
- 侵害後のトークン再利用を防止

**データモデル**:
```sql
RefreshToken (
  id, token VARCHAR UNIQUE, user_id FK,
  expires_at TIMESTAMP, created_at TIMESTAMP,
  is_revoked BOOLEAN DEFAULT FALSE
)
```

---

### 10. 権限ベースアクセス制御（PBAC）

**目的**: ロールベースのデフォルトとユーザー固有のオーバーライドによる細かい権限システム

**権限計算**: `(ロール権限 ∪ ユーザー付与) - ユーザー拒否`

**権限命名規則**: `category.action[.scope]`

**合計権限数**: 7カテゴリで38権限

**権限リスト**:

**1. servers（サーバー管理） - 8権限**
```
servers.create          - 新規サーバー作成
servers.view            - 自分のサーバー閲覧
servers.view_all        - 全サーバー閲覧（管理者）
servers.update          - サーバー設定変更
servers.delete          - サーバー削除
servers.start           - サーバー起動
servers.stop            - サーバー停止（force=Trueでの強制停止を含む）
servers.restart         - サーバー再起動
```

**2. rcon（RCON実行） - 1権限**
```
rcon.execute            - 他人のサーバーでRCONコマンド実行
                          （注意: 自分のサーバーでは常に実行可能）
```

**3. files（ファイル管理） - 5権限**
```
files.view              - ファイル閲覧
files.edit              - ファイル編集
files.upload            - ファイルアップロード
files.download          - ファイルダウンロード
files.delete            - ファイル削除
```

**4. backups（バックアップ管理） - 6権限**
```
backups.create          - 手動バックアップ作成
backups.view            - バックアップ一覧閲覧
backups.restore         - バックアップから復元
backups.delete          - バックアップ削除
backups.schedule        - 自動バックアップスケジュール設定
backups.download        - バックアップファイルダウンロード
```

**5. groups（グループ管理） - 6権限**
```
groups.create           - 新規グループ作成
groups.view             - グループ閲覧
groups.update           - グループ設定編集
groups.delete           - グループ削除
groups.attach           - サーバーにグループ適用
groups.detach           - サーバーからグループ解除
```

**6. users（ユーザー管理） - 8権限**
```
users.view              - ユーザー一覧閲覧
users.create            - 新規ユーザー作成
users.update            - ユーザー情報編集
users.delete            - ユーザー削除
users.approve           - 新規ユーザー登録の承認
users.change_role       - ロール変更
users.grant_permission  - 個別権限をユーザーに付与
users.deny_permission   - 個別権限をユーザーから拒否
```

**7. system（システム設定） - 4権限**
```
system.view_settings    - システム設定閲覧
system.update_settings  - システム設定変更
system.view_health      - ヘルスチェック情報閲覧
system.manage_limits    - 3層制限設定の管理
```

**データベーススキーマ**:
```sql
-- 権限定義
permissions (
  id, category, action, scope, description
)

-- ロールデフォルト権限
role_permissions (
  id, role ENUM('admin', 'operator', 'user'), permission_id FK
)

-- ユーザー固有の権限付与/拒否
user_permissions (
  id, user_id FK, permission_id FK,
  is_granted BOOLEAN  -- true: 付与, false: 拒否
)
```

**注意事項**:
- `is_dangerous` フラグは使用しない（設計から削除）
- 権限計算により、ユーザーが自分自身の権限を変更することを防止
- 監査ログはすべての権限変更に適用（別途実装）

---

### 11. セキュリティ実装

#### a) パストラバーサル防止
```python
def validate_path(user_path: str, base_dir: Path) -> Path:
    """多層検証"""
    resolved = (base_dir / user_path).resolve()
    if not resolved.is_relative_to(base_dir):
        raise SecurityError("パストラバーサルを検出")
    return resolved
```

#### b) アーカイブ展開セキュリティ
```python
def validate_archive(archive_path: Path) -> None:
    """zip爆弾と悪意のあるアーカイブを防止"""
    # サイズ制限、ファイル数制限、圧縮率チェック
    # シンボリックリンク、デバイスファイル、絶対パスを拒否
```

**設定可能な制限**（環境変数経由）:
```bash
ARCHIVE_MAX_SIZE_MB=500                    # アーカイブファイル最大サイズ
ARCHIVE_MAX_FILES=10000                    # アーカイブ内最大ファイル数
ARCHIVE_MAX_FILE_SIZE_MB=500               # 個別ファイル最大サイズ
ARCHIVE_MAX_COMPRESSION_RATIO=100          # 最大圧縮率（zip爆弾検出）
```

**拒否されるファイルタイプ**（セキュリティ考慮に基づき決定予定）:
- シンボリックリンク
- デバイスファイル
- 絶対パス（`/` プレフィックス）
- 親ディレクトリ参照（`../`）
- その他追加タイプ（TBD）

#### c) 入力サニタイゼーション（フロントエンド）
```typescript
class InputSanitizer {
  static sanitizeUsername(input: string): string { ... }
  static sanitizeFilePath(input: string): string { ... }
  static sanitizeHTML(input: string): string { ... }
}
```

**パスワードポリシー**: 緩め（email検証なし、個人データ保存なし）

---

### 12. 国際化（i18n）

**サポート言語**: 英語、日本語

**実装**:
- 遅延ロードされた翻訳を伴うカスタム`LanguageContext`
- 翻訳ファイル: `en.json`, `ja.json`
- localStorageに永続化
- エラーメッセージを翻訳

---

### 13. 接続監視（最小限）

**目的**: 基本的なAPIヘルスチェック

**実装**:
- 定期的チェック: `GET /api/v1/health`
- シンプルなステータス: 接続中 / 切断
- ビジュアルインジケーター（緑/赤）
- 複雑な再試行ロジックや劣化状態なし

---

### 14. WebベースのRCON実行

**目的**: Web UIからMinecraftサーバーコマンドを実行

**セキュリティモデル**:
- **バックエンド経由**: フロントエンドはRCON認証情報を受け取らない
- **権限**: 管理者ロールのみ（アプリケーションレベルの管理者）
- **実装**:
  ```
  フロントエンド（管理者UI） → POST /api/v1/servers/{id}/rcon
    → バックエンドがユーザーロールを検証
    → バックエンドがデータベースからRCON認証情報を取得
    → バックエンドがRCONクライアント経由でコマンドを実行
    → バックエンドがコマンド出力を返す
  ```

**コマンド検証**:
- コマンドインジェクション防止のための入力サニタイゼーション
- 許可コマンドのホワイトリスト（オプション、設定可能）
- RCON実行の監査ログ（オプション、将来機能）

---

### 15. サーバーログ取得（Strategy Pattern）

**目的**: 最小限のオーバーヘッドでWeb UIにMinecraftサーバーログを表示

**実装**: 戦略ベースのアプローチ（起動方法により異なる）

**インターフェース**:
```python
class LogRetrievalStrategy(ABC):
    @abstractmethod
    async def get_recent_logs(self, server_id: str, lines: int = 100) -> list[str]:
        """最後のN行のサーバーログを取得"""
        pass
```

**戦略**:

**A) ホストプロセス戦略**:
- ログファイルから読み取り: `servers/{server_id}/logs/latest.log`
- 最後の1000行をメモリにキャッシュ（ファイルmtimeの変更時に更新）
- フロントエンドは5秒ごとにポーリング
- リクエストあたり最後の100行を返す

**B) Docker戦略（DinD/DooD）**:
- Docker APIを使用: `container.logs(tail=100, stream=False)`
- ファイルI/O不要
- コンテナから直接ログを取得

**パフォーマンス最適化**:
- バックエンドがmtimeベースの無効化でログをキャッシュ
- ポーリング間隔: 5秒（設定可能）
- 制限: 最後の100行を表示、最大1000行をキャッシュ

---

### 16. 統一エラーレスポンス形式

**目的**: 全エンドポイントで一貫したAPIエラーハンドリング

**標準形式**:
```json
{
  "error": {
    "code": "SERVER_NOT_FOUND",
    "message": "Server with ID 'abc-123' not found",
    "details": {},
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**エラーコードカテゴリ**:
- `VALIDATION_ERROR`: 入力検証失敗
- `AUTHENTICATION_ERROR`: 認証失敗（無効な認証情報、期限切れトークン）
- `AUTHORIZATION_ERROR`: 権限拒否
- `NOT_FOUND`: リソースが見つからない
- `CONFLICT`: リソース競合（例: ユーザー名の重複）
- `INTERNAL_ERROR`: サーバー側エラー
- `EXTERNAL_SERVICE_ERROR`: MinecraftサーバーまたはDockerエラー

**HTTPステータスマッピング**:
- 400: `VALIDATION_ERROR`
- 401: `AUTHENTICATION_ERROR`
- 403: `AUTHORIZATION_ERROR`
- 404: `NOT_FOUND`
- 409: `CONFLICT`
- 500: `INTERNAL_ERROR`, `EXTERNAL_SERVICE_ERROR`

**`details` フィールド構造**:
- 機能ごとに標準化（実装時に定義）
- 例構造:
  ```json
  // VALIDATION_ERROR
  "details": {
    "field": "backup_interval",
    "constraint": "must be >= 1 hour",
    "provided": "30 minutes"
  }

  // AUTHORIZATION_ERROR
  "details": {
    "required_permission": "servers.delete",
    "user_role": "operator"
  }
  ```
- 実装フェーズでの決定（全エラーコードで事前定義しない）

**フロントエンドハンドリング**:
- TypeScriptインターフェースによる型安全なエラー解析
- 国際化されたエラーメッセージ（英語/日本語）
- ユーザーフレンドリーなエラー表示

---

### 17. グレースフルシャットダウン

**目的**: Minecraftサーバーを実行したままAPIを再起動

**グレースフルシャットダウン手順**:
```python
@app.on_event("shutdown")
async def shutdown_event():
    # 1. 進行中のバックアップを待つ（タイムアウト付き）
    await backup_service.wait_for_completion(timeout=300)

    # 2. データベース接続を閉じる
    await database.disconnect()

    # 3. リソースをクリーンアップ
    await cleanup_temp_files()
```

**重要な動作**:
- Minecraftサーバープロセスはバックグラウンドで実行し続ける
- プレイヤーには影響なし（接続維持）
- PIDファイル追跡により再起動後に再接続（HostProcessStrategy）
- Docker戦略は自動的に再接続（Dockerデーモンがコンテナを管理）

**バックアップ待機タイムアウト**:
- デフォルト: 300秒（5分）
- 環境変数で設定可能: `BACKUP_SHUTDOWN_TIMEOUT_SECONDS`
- タイムアウト時の動作: 進行中のバックアップは失敗としてマーク、次回間隔でリトライ

---

## データフロー例

### 1. サーバー作成フロー

```
ユーザー → フロントエンド（キャッシュからバージョン選択）
  → バックエンドAPI（POST /api/v1/servers）
    → ユーザー制限を検証（バックアップ設定など）
    → 起動戦略を選択（host/DinD/DooD）
    → Minecraft JARをダウンロード（キャッシュされたバージョンURLから）
    → サーバーディレクトリを初期化
    → 初期スナップショットを作成（起動前）
    → PostgreSQL（サーバー設定を保存）
    ← サーバーIDを返却
  ← サーバー詳細ページにリダイレクト
```

### 2. スケジュールされたバックアップフロー

```
バックグラウンドスケジューラー（N時間ごと）
  → BackupScheduleテーブルをチェック
    → バックアップ期限のサーバーを検索
      → 各サーバーごと:
        → スナップショットを作成（type: scheduled）
        → ワールドフォルダを圧縮 → tar.gz
        → バックアップディレクトリに保存
        → PostgreSQL（スナップショットメタデータを保存）
        → 古いスナップショットをクリーンアップ（max_backups制限を尊重）
```

### 3. グループ同期フロー

```
ユーザー → フロントエンド（グループプレイヤーを更新）
  → バックエンドAPI（PUT /api/v1/groups/:id）
    → PostgreSQL（group.players JSONBを更新）
    → 適用されたサーバーを検索（ServerGroupテーブル）
    → 各適用サーバーごと:
      → RCON接続
      → `whitelist add <player>`コマンドを送信
      → `whitelist reload`を送信
    ← 成功を返却
  ← UIを更新
```

---

## デプロイメントアーキテクチャ

### 開発環境

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: mcsd
      POSTGRES_USER: mcsd_user
      POSTGRES_PASSWORD: <secret>
    ports: ["5432:5432"]
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://mcsd_user:<secret>@postgres:5432/mcsd
      SECRET_KEY: <min-32-chars>
    ports: ["8000:8000"]
    depends_on: [postgres]
    volumes:
      - ./servers:/app/servers  # Minecraftサーバーデータ

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports: ["3000:3000"]
    depends_on: [backend]
```

### 本番環境（Docker）

- 開発環境と同じで、以下を追加:
  - シークレット管理（Dockerシークレットまたは環境変数）
  - サーバーデータ用の永続ボリューム
  - ヘルスチェック有効化
  - リソース制限設定

### systemdデプロイ（代替）

- バックエンド: `mc-server-dashboard-api.service`
- フロントエンド: `mc-dashboard-ui.service`
- コンテナなしの直接ホストデプロイ
- 単一マシンセットアップに適している

---

## ネットワーク層設計（将来 - フェーズ2）

### サブドメインベースのサーバールーティング

**目標**: `aaa.example.net:25565` → サーバーA、`bbb.example.net:25565` → サーバーB

**データモデル**（初日から実装）:
```sql
Server (
  ...
  subdomain VARCHAR UNIQUE,  -- "aaa", "bbb"など
  ...
)
```

**将来の実装**:
1. DNS: `*.example.net` → ダッシュボードIP
2. TCPプロキシがMinecraft接続を傍受
3. ハンドシェイクパケットを解析 → ホスト名を抽出
4. データベースでサブドメインを検索
5. 適切なサーバーにルーティング

**技術オプション**: カスタムTCPプロキシ、nginx stream、HAProxy、Velocity

---

## 設定管理

### 環境変数

**バックエンド（.env）**:
```bash
# セキュリティ
SECRET_KEY=<min-32-chars>
ALLOWED_ORIGINS=http://localhost:3000,https://mcsd.example.net  # カンマ区切り、ワイルドカード不可

# データベース
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 認証
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS設定
CORS_CREDENTIALS=true  # Cookieと認証ヘッダーを許可
CORS_METHODS=GET,POST,PUT,DELETE,PATCH
CORS_HEADERS=Content-Type,Authorization

# バックアップ制限（アプリケーションレベルの最大値）
MAX_BACKUP_RETENTION=30
MAX_BACKUP_INTERVAL_HOURS=168

# 起動戦略
DEFAULT_LAUNCH_STRATEGY=host  # host|dind|dood

# Javaパス（host戦略使用時 - 全バージョン）
JAVA_7_PATH=/usr/lib/jvm/java-7-openjdk-amd64/bin/java
JAVA_8_PATH=/usr/lib/jvm/java-8-openjdk-amd64/bin/java
JAVA_16_PATH=/usr/lib/jvm/java-16-openjdk-amd64/bin/java
JAVA_17_PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin/java
JAVA_21_PATH=/usr/lib/jvm/java-21-openjdk-amd64/bin/java

# ファイルストレージ
DATA_DIR=/data  # 全ファイルストレージのベースディレクトリ
MAX_UPLOAD_SIZE_MB=100  # Nginx/リバースプロキシ層で強制

# アーカイブセキュリティ（設定可能な制限）
ARCHIVE_MAX_SIZE_MB=500                    # アーカイブファイル最大サイズ
ARCHIVE_MAX_FILES=10000                    # アーカイブ内最大ファイル数
ARCHIVE_MAX_FILE_SIZE_MB=500               # 個別ファイル最大サイズ
ARCHIVE_MAX_COMPRESSION_RATIO=100          # 最大圧縮率（zip爆弾検出）

# グレースフルシャットダウン
BACKUP_SHUTDOWN_TIMEOUT_SECONDS=300        # バックアップ待機タイムアウト（秒）

# タイムゾーン
TZ=UTC  # バックエンドタイムゾーン（UTCに固定）

# APIレート制限（緩め、現実的な制限）
RATE_LIMIT_PER_MINUTE=60  # 一般APIコール
LOGIN_RATE_LIMIT_PER_MINUTE=10  # IPあたりのログイン試行
```

**フロントエンド（.env）**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_LOCALE=en  # デフォルト言語（enまたはja）
```

### ファイルストレージ構造

**ディレクトリレイアウト**:
```
/data/
├── servers/              # Minecraftサーバーファイル
│   ├── {server_id}/
│   │   ├── server.jar
│   │   ├── server.properties
│   │   ├── eula.txt
│   │   ├── world/
│   │   ├── plugins/     # Paper/Spigot
│   │   ├── mods/        # Forge/Fabric
│   │   └── logs/
│   │       └── latest.log
├── snapshots/            # バージョン履歴とバックアップ
│   ├── {snapshot_id}/
│   │   ├── metadata.json
│   │   └── data.tar.gz
└── temp/                 # 一時ファイル
    ├── uploads/         # 処理前のファイルアップロード
    └── extractions/     # アーカイブ展開
```

**パーミッション**:
- アプリケーションユーザー: `/data/`への読み書きアクセス
- Minecraftコンテナ: `/data/servers/{server_id}/`をボリュームとしてバインドマウント

**クリーンアップポリシー**:
- 24時間以上経過した一時ファイルは自動削除
- 失敗したアップロードは即座に削除

### CORSセキュリティ

**設定アプローチ**:
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    allowed_origins: list[str] = []  # ALLOWED_ORIGINS環境変数からロード

    @property
    def cors_config(self):
        return {
            "allow_origins": self.allowed_origins,  # ワイルドカード不可
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
```

**環境別設定**:
- **開発環境**: `ALLOWED_ORIGINS=http://localhost:3000`
- **本番環境**: `ALLOWED_ORIGINS=https://mcsd.example.net`
- **使用禁止**: `*`ワイルドカード（セキュリティリスク）

### タイムゾーン処理

**バックエンド**:
- **UTCに固定**: 全タイムスタンプをUTCで保存・処理
- データベース: `TIMESTAMP WITH TIME ZONE`カラムをUTCで使用
- Python: 全時間操作に`datetime.now(timezone.utc)`を使用

**フロントエンド**:
- **ユーザータイムゾーン変換**: 表示時にUTCをローカルタイムゾーンに変換
- ブラウザAPI: `Intl.DateTimeFormat`または`toLocaleString()`
- ユーザー設定: 設定でタイムゾーンセレクター（オプション）

**例**:
```typescript
// フロントエンド: UTCタイムスタンプをユーザーのローカル時刻で表示
const utcTimestamp = "2025-12-26T10:30:00Z";
const localTime = new Date(utcTimestamp).toLocaleString('ja-JP', {
  timeZone: 'Asia/Tokyo'
});
```

### APIレート制限

**実装**: ミドルウェアベース（例: FastAPI用`slowapi`）

**制限**（緩め、現実的な閾値）:
- **一般API**: IPあたり60リクエスト/分
- **ログインエンドポイント**: IPあたり10試行/分
- **ファイルアップロード**: ユーザーあたり5アップロード/分
- **RCON実行**: ユーザーあたり20コマンド/分

**制限超過時のレスポンス**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after": 30
    },
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**HTTPステータス**: `429 Too Many Requests`

### ファイルアップロード制限

**強制層**: Nginx/リバースプロキシ（アプリケーション層ではない）

**Nginx設定例**:
```nginx
server {
    location /api/v1/upload {
        client_max_body_size 100M;  # 最大アップロードサイズ

        # 特定のファイルタイプのみ許可（オプション）
        if ($request_filename ~* \.(exe|bat|cmd|sh|ps1)$) {
            return 403;
        }
    }
}
```

**許可拡張子**（アプリケーションレベル検証）:
- サーバーファイル: `.jar`, `.zip`, `.tar.gz`
- 設定ファイル: `.properties`, `.yml`, `.yaml`, `.json`, `.toml`
- ワールド: `.zip`, `.tar.gz`（ワールドフォルダアーカイブ）

**サイズ制限**:
- 個別ファイル: 100 MB（`MAX_UPLOAD_SIZE_MB`で設定可能）
- ワールドアーカイブ: 500 MB（ワールドバックアップ用のより大きな制限）

---

## ロギング戦略

### アプリケーションログ

**哲学**: Dockerベストプラクティスに従う（stdout/stderrロギング）

**実装**:
- **バックエンド**: stdout/stderrにログ出力（ファイルには出力しない）
- **フロントエンド**: サーバーサイドログはstdout、クライアントサイドログはブラウザコンソールへ
- **コンテナランタイム**: Dockerが自動的にログをキャプチャ
- **ログ集約**: 外部ツール（例: Dockerロギングドライバ、ELKスタック、Loki）

**ログレベル**:
- `DEBUG`: 開発デバッグ（本番環境では無効）
- `INFO`: 通常の操作（サーバー起動、スケジュールタスク）
- `WARNING`: 回復可能なエラー（Minecraftバージョン取得失敗、リトライロジック）
- `ERROR`: 深刻なエラー（データベース接続失敗、未処理例外）
- `CRITICAL`: システムレベル障害

**Pythonロギング設定**:
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # LOG_LEVEL環境変数で設定可能
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
```

**ログローテーション**: Dockerロギングドライバで処理
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**構造化ロギング**（オプション、将来の機能拡張）:
- JSON形式のログに`structlog`を使用
- ログ集約ツールによる解析が容易
- トレーシング用のリクエストIDを含める

### Minecraftサーバーログ

**保存**: サーバーごとのログファイル（ファイルストレージ構造を参照）
- パス: `/data/servers/{server_id}/logs/latest.log`
- ローテーション: Minecraftサーバー自身が処理

**取得**: 上記の「サーバーログ取得（Strategy Pattern）」セクションを参照

**保持**: サーバー削除時またはスナップショットクリーンアップ時にログを削除

---

## テスト戦略

### テストカバレッジ目標
- **現状**: 75-80%（既存実装）
- **目標**: 95%+
- **移行パス**: 時間をかけて段階的に改善

### テストタイプ
- **ユニットテスト**: サービス、ユーティリティ、モデル
- **統合テスト**: APIエンドポイント、データベース操作
- **E2Eテスト**: 重要なユーザーフロー（将来追加）

### ツール
- **バックエンド**: pytest、pytest-asyncio、coverage
- **フロントエンド**: Vitest、React Testing Library

---

## 将来の機能拡張

### フェーズ1（現在の実装スコープ）
- ✅ 複数のサーバー起動戦略（Host/DinD/DooD）
- ✅ Windows対応（DooDとホストプロセスを優先）
- ✅ 統一スナップショットシステム（ファイル + ワールド）
- ✅ グループ管理（RCON同期付きOP/ホワイトリスト）
- ✅ バージョンキャッシング（Vanilla/Paper/Forge）
- ✅ ユーザー承認ワークフロー
- ✅ 国際化（英語 + 日本語）
- ✅ 設定可能なバックアップ制限（3層: アプリ/ユーザー/サーバー）
- ✅ WebベースのRCON実行（管理者のみ）
- ✅ デスクトップファーストレスポンシブデザイン
- ✅ 統一エラーレスポンス形式
- ✅ APIレート制限
- ✅ ログ取得（戦略ベース）

### フェーズ2（ネットワーク層）
- ⏳ サブドメインベースルーティング（`aaa.example.net` → サーバーA）
- ⏳ Minecraftプロトコルプロキシ（TCPハンドシェイク解析）
- ⏳ DNS統合（ワイルドカード `*.example.net`）

### フェーズ3（可観測性 - オプション）
- ⏳ Prometheus + Grafana統合（外部ツール）
- ⏳ 分散トレーシング（マルチインスタンスデプロイが必要な場合）
- ⏳ 高度な監査ログ（RCONコマンド履歴、ユーザーアクション）

---

## 適用された設計原則

1. **Strategy Pattern**: プラガブルなサーバー起動方法とログ取得
2. **統一バージョニング**: ファイルとバックアップの共通スナップショットシステム
3. **セキュリティファースト**: パス検証、アーカイブ安全性、入力サニタイゼーション、レート制限
4. **ユーザー制限**: 3層設定（アプリ/ユーザー/サーバー）
5. **データベース永続化**: スケジュールは再起動を生き延びる
6. **シンプルさ**: 不要な複雑さを排除（WebSocketよりポーリング、ReduxよりContext API）
7. **プラットフォーム非依存**: クロスプラットフォームサポート（Linux主要、Windows部分的）
8. **デスクトップファーストUI**: デスクトップ向けに最適化、モバイルへのグレースフルデグラデーション
9. **一貫したエラーハンドリング**: 全エンドポイントで統一されたエラーレスポンス形式
10. **Dockerベストプラクティス**: stdout/stderrロギング、環境ベースの設定
11. **タイムゾーンの一貫性**: バックエンドはUTC、フロントエンドはユーザーローカル変換
12. **バックエンド経由のセキュリティ**: RCON認証情報はフロントエンドに公開しない

---

**最終更新日**: 2025-12-27
