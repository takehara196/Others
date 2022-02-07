# JavaScript 勉強会

注意：練習問題の内容とは連動していません。

## Lesson 01 HTMLとJavaScript

### JavaScriptは何に使えるの？

1. webサイトの動的な処理
1. ソフトウェアやSaaS等の処理のカスタマイズ
1. 汎用的な実行環境で

一般的には，1.のwebサイトの処理で使用するものを思い浮かべる人が多いと思う。
例えば，検索サイトで，数文字入力すると，自動的にマッチする候補が表示されるものは，典型的なJavaScriptを用いた処理である。

ちなみに，公開されたwebサイトである必要はなく，ローカルPC上のhtmlファイルを，ブラウザで開いたものでも，JavaScriptを実行できる（制約がある場合もある）。
例えば，パスワード用のランダムな文字列を生成する，のような単純な処理なら，簡単に実現できる。

これに対して，2.の例としては，以下のようなものがある。

- cybozu社の「kintone」のカスタマイズ
  - 入力内容を保存前にチェックしたり，所定のルールで整形して保存する
  - 保存したら，Slackに通知を投げる
  - 他のアプリからデータを取ってきたり，他のアプリにデータを入れたり，等々
- Googleスプレッドシートでの，GASによる処理
  - GAS (Google Apps Script) は，JavaScriptがベース（というか，ほぼJavaScript)
  - Excelの「マクロ」のように，数式では実現できない複雑な処理が可能
  - さらにはGoogleドライブ等のGoogleサービスへのアクセスも可能
- ソフトの例を挙げると，OpenOffice/LibreOfficeでは，JavaScriptでのマクロ作成が可能（他にも，PythonやOpenOffice Basic等も使える）

さらには，Node.jsのような，3.もある。特定の環境やサービス内に限定せず，汎用的な処理を目的とした，JavaScriptの実行環境である。

### どこにJavaScriptを書くの？

1. HTML内
1. 別のファイル

本体のHTMLファイルの例：

```html
<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="utf-8">
        <title>Lesson 01 HTMLとJavaScript</title>

        <!-- ↓ 1.の場合 -->
        <script>
            'use strict';
            var a = 0;
            for(var i = 0; i < 10; i++){
                a += i;
            }
            alert(a);
        </script>

        <!-- ↓ 2.の場合 -->
        <script src="lesson01-1.js"></script>
    </head>
    <body>
        ページの内容
    </body>
</html>
```

上記で参照している別ファイル（lesson01-1.js）の例

```js
function addTo(n){
    var a = 0;
    for(var i = 0; i < n; i++){
        a += i;
    }
    return a;
}
```

なお，`<script>`タグは，`<body>`内に書いても良い。

### コードはいつ，どこから実行されるの？

1. ページ読み込み（完了）時：関数外の部分
2. クリック等のイベントの発生時
2-1. HTML側で指定（最近は推奨されない）
2-2. JS内で指定（addEventListenerを使う）
2-3. ライブラリ，フレームワーク等の所定の方法で設定（kintoneもコレ）
3. コールバックとして設定した場合，コールバック条件の成立時

#### 1. ページ読み込み（完了）時：関数外の部分

関数は呼び出されて実行される。
逆に言えば，関数外の部分は，すぐに実行される。
この「すぐ」とは，ページが読み込まれて，`<script>`が処理される時点である。
場合によっては，ページ描画が完了していない段階で実行されてしまう。
そのため，`<script>`を`<body>`の最後におく場合もある。

```js
function XXX(){
    /* あれこれ処理 */
}
```

#### 2. クリック等のイベントの発生時

##### 2-1. HTML側で指定（最近は推奨されない）

```html
<button type="button" onclick="buttonClick()">押すなよ</button>
```

```js
function buttonClick(){
    alert("押すなよって言ったじゃん");
}
```

##### 2-2. JS内で指定（addEventListenerを使う）

```js
window.addEventListener('load', init); // ページ読み込み時の処理を登録

function init(){
    /* 初期化等の処理を実施 */
    var button2 = document.getElementById('button2');
    button2.addEventListener('click', buttonClick);
}

```

```html
<button id="button2" type="button">押してね</button>
```

#### 2-3. ライブラリ，フレームワーク等の所定の方法で設定（kintoneもコレ）

kintoneの場合，kintone側で管理されているJavaScriptにより，自分が設置したjsファイル内で，所定の書き方で指定すると，コードが呼び出される。

```js
kintone.events.on('app.record.index.show', indexShown);
// レコード一覧画面が表示された際の処理を設定

function indexShown(event){
    /* 処理を記述 */
}

```

`kintone.events.on(実行タイミング, 呼び出す関数);`のように書く。
実行タイミングの部分を配列にして，複数を指定することもできる。

```js
// レコード追加または編集で，保存を押し，kintoneに保存される前のタイミングで実行
kintone.events.on([
    'app.record.create.submit'
    ,'app.record.edit.submit'
], checkBeforeSave);

function checkBeforeSave(event){
    /* 保存前の入力チェックなどの処理 */
}
```

##### 3. コールバックとして設定した場合，コールバック条件の成立時

コールバックは，組み込みオブジェクト等で，次のような所定の条件成立時に処理を実施するもの。

- 一定時間が経過した
- AJAXの通信が完了した

※そもそも，上記2.のイベントリスナーやkitnoneでの関数呼び出しもコールバックの一種である

```js
// 例えばボタンを押すと以下を実行するようにしておく
// setTimeoutは組み込みオブジェクトで，
//   setTimeout(呼び出す関数, 実行までの時間[ミリ秒])
// のように使用する
function startTimeout(){
    var timer = setTimeout(cbTimeout, 3000);
}

// コールバックで呼び出される関数
function cbTimeout(){
    alert('3秒経過しました。');
}

```

### 書き方の注意点は？

#### 引用符

- シングル `'` でもダブル `"` でも良いが，揃えた方が良い。
  - バックスラッシュ ``` ` ``` を使うと，変数を展開できる

#### 比較演算子

- `==, !=` と `===, !==` のグループがある
  - 後者はデータ型も含めた厳密な一致となる
  - 前者の方が柔軟だがバグを生むので，後者を用いるのが良い

  ```js
  var a = 10;
  var b = '10';

  if(a == b){
      alert('aとbは等しい');
  }else{
      alert('aとbは等しくない');
  }

  if(a === b){
      alert('aとbは等しい');
  }else{
      alert('aとbは等しくない');
  }
  ```
  
#### 変数のスコープ

- 関数の外で宣言すると，グルーバル変数となる
  - 関数内を含め，どこからでもアクセスできる
  - しかし，バグの元になりやすいので，極力使わないようにする

- そもそも，`var`ではなく，`let`と`const`を使う方が良い
  - 本テキストでは，これ以降，`var`は使用しないこととする

#### ブラウザの開発者ツールとconsole.log

- いちいち`alert()`で出力すると，クリックして閉じるのは面倒である
- `console.log()`を使うと，ブラウザの開発者ツールの画面で出力を見られる

```js
function addTo100(){
    let sum = 0;
    let n = 100;
    for(let i = 1; i <= n; i++){
        sum += i;
        console.log(sum);
    }
    return sum;
}
```

#### コメントを書こう

- コメントはコード中で無視される部分
  - 行コメント：`//`以降の行末まで
  - ブロックコメント：`/*`で開始，`*/`で終了
- JSDoc形式
  - ブロックコメントを拡張した形式
  - `/**`で始まり，各行の初めは` * `とし，`*/`で閉じる
  - 引数や戻り値などの書式が決まっている

```js
/**
 * クリックした際のイベントリスナーを設定する
 * @param {String} id 
 * @param {Function} callback 
 * @returns なし
 */
function setClickListener(id, callback){
    const elem = document.getElementById(id);
    if(!elem){
        console.log(`${id}が存在しません`);
        return;
    }
    if(typeof callback !== 'function'){
        console.log(`指定されたコールバック関数が存在しません`);
        return;
    }
    // 問題ない場合のみ設定する
    elem.addEventListener('click', callback);
}
```

#### 何を使って開発するか？

- メモ帳でもできる
- とは言え，コーディング用のテキストエディタや，VSCodeのような開発環境が便利である

#### 情報源

ネットにはたくさんあるので，自分が見やすいものを参照すれば良い。
但し古いものは△。

- JavaScriptの文法
  - [[https://ja.javascript.info/]]
  - [[https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference]]
- Web API（ブラウザで使える機能）
  - [[https://developer.mozilla.org/ja/docs/Web/API]]

### 文法のピックアップ

#### 配列とオブジェクト

- 配列は，要素を順に入れたもの

```js
let a = []; // 空の配列を作成
let b = ['北海道', '青森', '秋田', '岩手']; // 要素を指定して配列を作成

b.push('山形'); // 要素を追加

// console.log()で出力できる
console.log(a);
console.log(b);

// 位置を指定して参照
console.log(b[0]); // 北海道
console.log(b[4]); // 山形
console.log(b[5]); // undefined

// 反復して処理
for(let item of b){
    console.log(item); 
}
/*
以下が出力される
北海道
青森
秋田
岩手
山形
*/

// 上記と同じ処理の伝統的な書き方
for(let i = 0; i < b.length; i++){
    console.log(b[i]);
}
```

- オブジェクトは，変数や関数をまとめたもの

```js
let c = {}: // 空のオブジェクトを作成
let d = {name => 'Pochi', age => 3, '名前' => 'ポチ'}; // 

console.log(c, d); // console.log()はカンマで区切って複数を放り込める

// 参照の仕方
console.log(d.name); // Pochi
console.log(d['name']); // Pochi
/*
console.log(d.名前); // 変数名で使えない文字は「.」で参照は不可
*/ 
console.log(d['名前']); // ポチ

// 後から追加しても良い
d.species = 'cat';
d['性別'] = 'オス';
// 関数も入れられる
d.speak = function(){
    console.log('コケコッコー');
}
// 階層的に使える
d.status = {};
d.status.length = '30cm';
d.status.weight = '3kg';

// 出力してみる
console.log(d);
// 関数を実行してみる
d.speak();
```

- 例は挙げなかったが，オブジェクトの要素に配列を入れることもできる

#### JSONって何？

- オブジェクトを他とやりとりするために「シリアライズ」（テキスト化）した形式
- JSON形式では，引用符は`"`のみが正当なので注意！

```js
// 文字列でオブジェクトを表現
let s = '{"name":"Tama", "age":"47", "品種":"三毛"}';
console.log(s);
// オブジェクトに変換
let obj = JSON.parse(s);
console.log(obj);
console.log(obj.age);
// 既存のオブジェクトをJSONの文字列にする
let jsn = JSON.stringify(d);
console.log(jsn); // 関数は無視される

```

### セキュリティ上の注意事項

- クロスサイトスクリプティングを盛り込まないように注意する
- kintoneで文字列等でレコードを検索する場合は，SQLインジェクション的なことをしなように注意する
