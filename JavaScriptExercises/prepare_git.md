## Gitの用意について（主にWindowsの場合）

ひとまずメモ程度ですが...

- 公式サイトからインストーラを入手して実行
- やたらと設定の選択を求められるが，以下のもの以外はデフォルでOK
  - 改行コードをどうするか？
    →どっちも「そのまま(as-is)」である選択肢を選ぶ

- ユーザ登録
  - Git Bashを開き，以下を設定

  ```sh
  git config --global user.name "XXX"
  git config --global user.email "xxx@example.com"
  ```

- 当Exercisesのリポジトリを登録
  - Git Bashで格納先のフォルダに行く
  - ブラウザでGitHubリポジトリのCode（緑のボタン）をクリックし，URLをコピー
  - Git Bashで以下を実行

  ```sh
  git clone URL
  ```

- VSCodeで上記フォルダを開き，解答を用意
  - 自分用のフォルダを用意（README.mdを参照）

- 解答を書いたら，commit（VSCodeで，またはコマンドラインで）

- GitHubへpush
  - あらかじめ以下を行っておく必要がある
    - GitHubアカウントを登録しておく
    - リポジトリ管理者にcollaboratorとして招待してもらう
  - VSCodeの場合，初回実行時に認証の連携許可の操作が求められる
  - コマンドラインの場合，GitHubのセキュリティ強化でパスワード認証ができなくなっている
    - ssh鍵を用意し，GitHubに登録の上，httpsではなく，sshでリポジトリのgit cloneを行うの方がスムーズかもしれません
