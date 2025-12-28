# ドキュメント索引

このディレクトリには、Minecraft Server Dashboardの全プロジェクトドキュメントが含まれています。

## 利用可能な言語

すべてのドキュメントは英語と日本語で利用可能です：
- 英語: `DOCUMENT_NAME.md`
- 日本語: `DOCUMENT_NAME.ja.md`

## ドキュメント一覧

### 1. プロジェクト哲学と原則

**目的**: プロジェクト全体の中核となる価値観、設計原則、意思決定フレームワークを定義します。

**ファイル**:
- 英語: [PHILOSOPHY.md](./PHILOSOPHY.md)
- 日本語: [PHILOSOPHY.ja.md](./PHILOSOPHY.ja.md)

**主なトピック**:
- なぜ再実装するのか
- 中核となる価値観（保守性、拡張性、パフォーマンス、信頼性）
- 設計原則（テスタビリティファースト、コードの一貫性）
- 品質基準と要件

---

### 2. アーキテクチャ設計

**目的**: システム全体のアーキテクチャ、技術スタック、コンポーネント構造を記述します。

**ファイル**:
- 英語: [ARCHITECTURE.md](./ARCHITECTURE.md)
- 日本語: [ARCHITECTURE.ja.md](./ARCHITECTURE.ja.md)

**主なトピック**:
- API/フロントエンド完全分離の3層アーキテクチャ
- 技術スタック（NestJS、Next.js、PostgreSQL、Redis）
- Minecraftサーバー管理（プロセス/Docker制御）
- サブドメインベースルーティングのためのネットワーク層設計（将来）
- コンポーネントアーキテクチャとデータフロー
- デプロイメントアーキテクチャ（Docker/Kubernetes）
- セキュリティとスケーラビリティの考慮事項

---

### 3. コーディング規約

**目的**: コーディング規約、命名規則、コードスタイルガイドラインを定義します。

**ファイル**:
- 英語: [CODING_STANDARDS.md](./CODING_STANDARDS.md)
- 日本語: [CODING_STANDARDS.ja.md](./CODING_STANDARDS.ja.md)

**主なトピック**:
- Pythonコードスタイル（Black、Ruff、型ヒント）
- TypeScript/React規約（Prettier、ESLint）
- 命名規則（変数、関数、クラス、ファイル）
- コメントとドキュメントのルール（docstring、JSDoc）
- インポートの順序と整理
- テスト規約
- データベースとSQL命名
- 自動強制（pre-commitフック、CI）

---

### 4. 開発ワークフロー

**目的**: 開発プロセス、Gitワークフロー、コラボレーションガイドラインを概説します。

**ファイル**:
- 英語: [WORKFLOW.md](./WORKFLOW.md)
- 日本語: [WORKFLOW.ja.md](./WORKFLOW.ja.md)

**主なトピック**:
- Gitブランチ戦略（Release Flow）
- コミットメッセージ規約（Conventional Commits）
- プルリクエストとレビュープロセス
- CI/CD要件と自動化
- リリースプロセスとGitHub Releases
- 依存関係管理（Dependabot）

---

## 推奨読書順序

新しいコントリビューターやチームメンバーには、以下の順序でドキュメントを読むことをお勧めします：

1. **[PHILOSOPHY.md](./PHILOSOPHY.md)** - プロジェクトの中核的な価値観と原則を理解する
2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - システム全体の構造と技術スタックを学ぶ
3. **[CODING_STANDARDS.md](./CODING_STANDARDS.md)** - コード規約に慣れる
4. **[WORKFLOW.md](./WORKFLOW.md)** - 開発プロセスを理解する

---

**最終更新日**: 2025-12-26
