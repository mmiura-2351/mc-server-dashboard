# コーディング規約

## 目的

このドキュメントは、Minecraft Server Dashboardプロジェクトのコーディング規約、命名規則、コードスタイルガイドラインを定義します。これらの規約により、コードの一貫性、保守性、プロジェクトの中核的価値観への準拠が保証されます。

## 中核原則

すべてのコードはプロジェクト哲学に沿う必要があります：

1. **テスタビリティファースト**: 明確な依存関係を持つテスト可能なコードを書く
2. **コードの一貫性**: 自動化ツールによる厳格な強制
3. **型安全性**: 静的型付けを活用（Python型ヒント、TypeScript）
4. **可読性**: コードは書かれるよりも読まれる

---

## Python（バックエンド）

### コードスタイル

**フォーマッター**: [Black](https://black.readthedocs.io/)（行長: 100）
**リンター**: [Ruff](https://docs.astral.sh/ruff/)
**インポートソート**: [isort](https://pycqa.github.io/isort/)（Black互換プロファイル）

**設定** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py313']

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.isort]
profile = "black"
line_length = 100
```

**自動強制**: pre-commitフックとCIチェック

### 命名規則

| 種類 | 規約 | 例 |
|------|------|-----|
| **変数** | `snake_case` | `server_id`, `backup_count` |
| **関数** | `snake_case` | `create_server()`, `get_user_by_id()` |
| **クラス** | `PascalCase` | `ServerManager`, `BackupScheduler` |
| **定数** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PORT` |
| **プライベートメンバー** | `_先頭アンダースコア` | `_internal_method()`, `_cache` |
| **型変数** | `PascalCase`（`T`接頭辞） | `TModel`, `TResponse` |
| **ファイル** | `snake_case.py` | `server_manager.py`, `backup_service.py` |
| **パッケージ** | `lowercase`（アンダースコアなし） | `services/`, `models/` |

### 型ヒント

**必須**: すべての関数シグネチャとパブリックAPIには型ヒントが必要です。

```python
# 良い例
async def create_server(
    config: ServerConfig,
    user_id: int,
    strategy: ServerLaunchStrategy,
) -> Server:
    ...

# 悪い例（型ヒントなし）
async def create_server(config, user_id, strategy):
    ...
```

**複雑な型**: 明確性のため`typing`モジュールを使用。

```python
from typing import Optional, Dict, List, Any
from collections.abc import Sequence

def process_players(
    players: Sequence[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Player]:
    ...
```

**型チェック**: `mypy`をstrictモードで使用。

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### インポートの整理

**順序**（`isort`で強制）:
1. 標準ライブラリのインポート
2. サードパーティのインポート
3. ローカルアプリケーションのインポート

```python
# 標準ライブラリ
import asyncio
from pathlib import Path
from typing import Optional

# サードパーティ
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# ローカル
from app.core.config import settings
from app.models.server import Server
from app.services.server_manager import ServerManager
```

**グループ化**: グループ間は空行で分離。

**絶対インポート**: 相対インポートより絶対インポートを優先。

```python
# 良い例
from app.services.server_manager import ServerManager

# 避ける
from ..services.server_manager import ServerManager
```

### ドキュメント文字列

**スタイル**: Google形式のdocstring
**必須**: すべてのパブリックモジュール、クラス、関数

```python
async def create_backup(
    server_id: str,
    snapshot_type: SnapshotType,
    created_by: int,
) -> Snapshot:
    """Minecraftサーバーのバックアップスナップショットを作成する。

    Args:
        server_id: サーバーの一意識別子。
        snapshot_type: スナップショットタイプ（manual, scheduled, auto_save）。
        created_by: バックアップを開始したユーザーID。

    Returns:
        メタデータを含む作成されたスナップショットオブジェクト。

    Raises:
        ServerNotFoundError: サーバーが存在しない場合。
        InsufficientStorageError: ストレージクォータを超過した場合。
    """
    ...
```

**モジュールdocstring**:

```python
"""サーバー起動戦略の実装。

このモジュールは、異なるサーバー起動方法（Host、DinD、DooD）向けの
ServerLaunchStrategyインターフェースの具体的実装を提供します。
"""
```

### コード構成

**ファイル構造**:
```
backend/
├── api/              # APIエンドポイント（FastAPIルート）
├── services/         # ビジネスロジック
├── models/           # SQLAlchemyモデル
├── schemas/          # Pydanticスキーマ（リクエスト/レスポンス）
├── core/             # コアユーティリティ（config、security、db）
└── tests/            # テストファイル（構造をミラー）
```

**1ファイル1クラス**（密接に関連する場合を除く）。

**関数の長さ**: 最大50行（ガイドライン、厳格ではない）。

**クラスメソッドの順序**:
1. `__init__`
2. パブリックメソッド
3. プライベートメソッド
4. プロパティ
5. マジックメソッド（`__init__`以外）

### エラーハンドリング

**カスタム例外**: ベース例外クラスから継承。

```python
# core/exceptions.py
class ApplicationError(Exception):
    """すべてのアプリケーションエラーのベース例外。"""

class ServerNotFoundError(ApplicationError):
    """サーバーが見つからない場合に発生。"""
```

**裸の`except`を避ける**: 常に例外タイプを指定。

```python
# 良い例
try:
    result = await perform_operation()
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Operation failed: {e}")
    raise

# 悪い例
try:
    result = await perform_operation()
except:  # 広すぎる
    pass
```

---

## TypeScript/React（フロントエンド）

### コードスタイル

**フォーマッター**: [Prettier](https://prettier.io/)
**リンター**: [ESLint](https://eslint.org/)（TypeScriptとReactプラグイン付き）

**設定** (`.prettierrc.json`):
```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

**ESLint** (`.eslintrc.json`):
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

### 命名規則

| 種類 | 規約 | 例 |
|------|------|-----|
| **変数** | `camelCase` | `serverId`, `backupCount` |
| **関数** | `camelCase` | `createServer()`, `getUserById()` |
| **コンポーネント** | `PascalCase` | `ServerCard`, `BackupScheduler` |
| **インターフェース** | `PascalCase`（`I`接頭辞なし） | `Server`, `BackupConfig` |
| **型** | `PascalCase` | `ServerStatus`, `UserRole` |
| **列挙型** | `PascalCase` | `ServerType`, `SnapshotType` |
| **定数** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `API_BASE_URL` |
| **ファイル（コンポーネント）** | `PascalCase.tsx` | `ServerCard.tsx`, `BackupList.tsx` |
| **ファイル（ユーティリティ）** | `kebab-case.ts` | `api-client.ts`, `token-manager.ts` |
| **CSSモジュール** | `PascalCase.module.css` | `ServerCard.module.css` |

### 型定義

**明示的な戻り値の型**: すべての関数に必須。

```typescript
// 良い例
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// 悪い例（暗黙的な戻り値の型）
function calculateTotal(items: Item[]) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

**InterfaceとType**:
- `interface`：オブジェクト形状に使用（拡張可能）
- `type`：ユニオン、交差、プリミティブに使用

```typescript
// Interface（オブジェクトに推奨）
interface Server {
  id: string;
  name: string;
  status: ServerStatus;
}

// Type（ユニオン/交差に使用）
type ServerStatus = 'running' | 'stopped' | 'starting';
type UpdateableServer = Partial<Server> & { id: string };
```

**`any`を避ける**: `unknown`または特定の型を使用。

```typescript
// 良い例
function parseResponse(data: unknown): Server {
  if (isServer(data)) {
    return data;
  }
  throw new Error('Invalid server data');
}

// 悪い例
function parseResponse(data: any): Server {
  return data;  // 型安全性なし
}
```

### インポートの整理

**順序**:
1. React/Next.jsのインポート
2. サードパーティライブラリ
3. 内部モジュール（`@/`経由の絶対パス）
4. 相対インポート
5. CSSモジュール（最後）

```typescript
// React/Next.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// サードパーティ
import { Result } from 'neverthrow';

// 内部（絶対パス）
import { useAuth } from '@/contexts/auth';
import { ServerService } from '@/services/server';
import type { Server } from '@/types/server';

// 相対
import { ServerCard } from './ServerCard';

// CSS
import styles from './ServerList.module.css';
```

### Reactコンポーネントガイドライン

**関数コンポーネント**: 関数宣言を使用（アロー関数ではない）。

```typescript
// 良い例
export function ServerCard({ server }: ServerCardProps) {
  return <div>{server.name}</div>;
}

// 避ける
export const ServerCard = ({ server }: ServerCardProps) => {
  return <div>{server.name}</div>;
};
```

**Propsインターフェース**: 明示的に定義し、`Props`で接尾辞を付ける。

```typescript
interface ServerCardProps {
  server: Server;
  onDelete?: (id: string) => void;
  className?: string;
}

export function ServerCard({ server, onDelete, className }: ServerCardProps) {
  // ...
}
```

**Propsの分割代入**: 関数シグネチャで行う（上記のとおり）。

**フックの順序**:
1. Contextフック（`useAuth`, `useLanguage`）
2. Stateフック（`useState`）
3. Effectフック（`useEffect`）
4. カスタムフック
5. イベントハンドラー
6. レンダーロジック

**ファイル構造**（コンポーネントファイル）:
```typescript
// インポート
import { useState } from 'react';
import styles from './Component.module.css';

// 型
interface ComponentProps {
  // ...
}

// コンポーネント
export function Component({ prop }: ComponentProps) {
  // Contextフック
  const { user } = useAuth();

  // Stateフック
  const [data, setData] = useState<Data | null>(null);

  // Effect
  useEffect(() => {
    // ...
  }, []);

  // イベントハンドラー
  const handleClick = () => {
    // ...
  };

  // レンダー
  return <div>...</div>;
}
```

### CSSモジュール

**ファイル名**: `ComponentName.module.css`

**クラス名**: CSSでは`camelCase`、TypeScriptではオブジェクトプロパティとしてアクセス。

```css
/* ServerCard.module.css */
.container {
  padding: 1rem;
}

.titlePrimary {
  font-size: 1.5rem;
}
```

```typescript
import styles from './ServerCard.module.css';

export function ServerCard() {
  return (
    <div className={styles.container}>
      <h2 className={styles.titlePrimary}>Server Name</h2>
    </div>
  );
}
```

**グローバルスタイルを避ける**: コンポーネントスコープのスタイルにはCSSモジュールを使用。

### コメントとドキュメント

**JSDoc**: 複雑な関数とユーティリティに使用。

```typescript
/**
 * APIからサーバー詳細を取得する。
 *
 * @param id - サーバーの一意識別子
 * @returns Serverオブジェクトまたはエラーに解決されるPromise
 * @throws {ApiError} サーバーが見つからないかネットワークエラーの場合
 */
async function fetchServer(id: string): Promise<Result<Server, ApiError>> {
  // ...
}
```

**インラインコメント**: 「何を」ではなく「なぜ」を説明。

```typescript
// 良い例（理由を説明）
// 過度なAPI呼び出しを避けるため検索をデバウンス
const debouncedSearch = debounce(handleSearch, 300);

// 悪い例（当たり前のことを述べている）
// loadingをtrueに設定
setLoading(true);
```

---

## SQLとデータベース

### スキーマ命名

**テーブル**: `snake_case`、複数形

```sql
CREATE TABLE servers (...);
CREATE TABLE backup_schedules (...);
```

**カラム**: `snake_case`

```sql
CREATE TABLE servers (
  id UUID PRIMARY KEY,
  server_name VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE
);
```

**外部キー**: `<table>_<column>`または説明的な名前

```sql
server_id UUID REFERENCES servers(id),
owner_id INTEGER REFERENCES users(id)
```

**インデックス**: `idx_<table>_<columns>`

```sql
CREATE INDEX idx_servers_owner_id ON servers(owner_id);
CREATE INDEX idx_backups_server_created ON backups(server_id, created_at);
```

### マイグレーション（Alembic）

**ファイル名**: Alembicによる自動生成
**メッセージ形式**: 説明的、命令法

```bash
# 良い例
alembic revision -m "add server subdomain column"
alembic revision -m "create backup schedules table"

# 悪い例
alembic revision -m "changes"
alembic revision -m "update"
```

**マイグレーション構造**:
- 1マイグレーションにつき1つの論理的変更
- `upgrade()`と`downgrade()`の両方を含める
- ロールバック機能をテスト

---

## テスト

### ファイル命名と配置

**バックエンド**:
```
backend/
├── app/
│   └── services/
│       └── server_manager.py
└── tests/
    └── services/
        └── test_server_manager.py  # 構造をミラー、"test_"接頭辞
```

**フロントエンド**:
```
frontend/
├── components/
│   └── ServerCard.tsx
└── __tests__/
    └── components/
        └── ServerCard.test.tsx  # 構造をミラー、".test.tsx"接尾辞
```

### テスト命名

**テスト関数**: 説明的、`test_`で開始（Python）または`it`（TypeScript）。

```python
# Python（pytest）
def test_create_server_with_valid_config():
    ...

def test_create_server_raises_error_when_user_not_approved():
    ...
```

```typescript
// TypeScript（Vitest）
describe('ServerCard', () => {
  it('renders server name correctly', () => {
    // ...
  });

  it('calls onDelete when delete button is clicked', () => {
    // ...
  });
});
```

### テスト構造

**AAAパターン**: Arrange（準備）、Act（実行）、Assert（検証）

```python
def test_backup_scheduler_creates_snapshot():
    # Arrange（準備）
    server = create_test_server()
    scheduler = BackupScheduler()

    # Act（実行）
    snapshot = await scheduler.create_backup(server.id)

    # Assert（検証）
    assert snapshot is not None
    assert snapshot.server_id == server.id
    assert snapshot.snapshot_type == SnapshotType.SCHEDULED
```

---

## Gitコミットメッセージ

詳細は[WORKFLOW.md](./WORKFLOW.md)を参照。

**クイックリファレンス**:
- 形式: `type(scope): description`
- タイプ: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- 命令法: "add feature"（"added feature"ではない）
- 件名行は最大72文字

---

## エディタ設定

**EditorConfig** (`.editorconfig`):
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{ts,tsx,js,jsx,json,css}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

---

## 強制

### Pre-commitフック

**バックエンド** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
```

**フロントエンド**: `package.json`で設定:
```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier --write .",
    "type-check": "tsc --noEmit"
  },
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

### CIチェック

マージ前に必要なチェック（[WORKFLOW.md](./WORKFLOW.md)参照）:
- ✅ リンター（Ruff、ESLint）
- ✅ 型チェック（mypy、TypeScript）
- ✅ ユニットテスト
- ✅ コードフォーマット（Black、Prettier）
- ✅ ビルド成功

---

## 追加リソース

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

**最終更新日**: 2025-12-26
