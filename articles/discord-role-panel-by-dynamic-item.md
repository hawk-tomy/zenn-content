---
title: "Discord.pyのダイナミックアイテムでロールパネルを作る"
emoji: "✨"
type: "tech"
topics:
  - "python"
  - "discord"
  - "discordpy"
  - "discordbot"
published: true
---
discord.pyにv2.4で追加された[discord.ui.DynamicItem](https://discordpy.readthedocs.io/ja/stable/interactions/api.html#dynamicitem)は便利ですよ、ということをボタン一つの簡易的なロールパネルを作ることで紹介します。
[公式の使用例](https://github.com/Rapptz/discord.py/blob/master/examples/views/dynamic_counter.py)

## 概要
discord.pyにおいてcustom_idで処理を分岐しようと考えた場合、BOTが起動してから送信したviewに含まれるcustom_id(ランダムか自分で設定したか)か、BOTの起動時に登録された永続化してあるViewに含まれるcustom_idかを利用するしかありませんでした。
つまり、custom_idに情報を保存しようとした場合には、永続化したい場合を利用して、過去に送信したcustom_idを全て永続化したものとして登録する必要がありました。
DynamicItemは、これを処理したいcustom_idを正規表現で表すことで便利に使えるようにしました。
具体的には、ボタンなどを継承して処理を記述するのではなく、DynamicItemを正規表現を設定して継承し処理を記述するようにすることで、一つの正規表現とcustom_idで扱える情報であればまとめて扱うことができるようになっています。

## 実装
ここにある実装は[github](https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py)にもあります。

### ダイナミックなボタン

https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py#L18-L21

ダイナミックなボタンは、DynamicItemを継承しつつ同時に`template="..."`というように正規表現を与える必要があります。
また、`__init__`で`super().__init__`を呼び出す時には、ボタンのようなダイナミックにしたいアイテムを与える必要があります。
この場合であれば、custom_idをダイナミックアイテムの識別のためのプレフィックスにロールIDを16進数に直した文字列を付けたものとしたいので、templateをそれにマッチするように設定し、`__init__`ではそうなるようにButtonのcustom_idを作っています。
使いやすく渡されるのはマッチオブジェクトのため、templateには`(?P<id>[0-9a-f]+)`のようにIDの部分をグループにしています。
 
https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py#L23-L25

クラスメソッドとして`from_custom_id`を実装する必要があります。
このクラスメソッドは、ボタンなどが押されたときに、そのcustom_idがtemplateにfullmatchを実行しマッチオブジェクトが帰ってきたときに、その`Interaction`、押されたアイテム自体、そのマッチオブジェクトの三つが渡され、処理した後に自身を返す必要があります。
この場合であれば、`__init__`はラベルとロールidを要求しているので、itemのラベルとマッチオブジェクトからidの部分を抜き取って使っています。

https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py#L27

https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py#L44-L53

ダイナミックなボタンが押されたりしたときには、そのcallbackまたは、`__init__`で与えたアイテムのcallbackが呼ばれます。

### ダイナミックなボタンを使う
このダイナミックなボタンを使うには、まず、botにadd_dynamic_itemsを使って登録する必要があります。

https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py#L68-L76

登録されていれば、次のように普通のアイテムのように扱うことができます。

https://github.com/hawk-tomy/zenn-content/blob/main/sample/discord-role-panel-by-dynamic-item/bot.py#L56-L65

### 動作
この例の実装は、次のように使えます。
まずは、コマンドを実行してロールパネルを設定します。
例えば、次のようなコマンドは、
![](/images/role-panel-command.png)
次のように表示され、
![](/images/role-panel-command-result.png)
実際に使うと、このようになります。
![](/images/role-panel-use-button.png)


## 終わりに
割と雑めではありますが、DynamicItemを使うと便利だよと言うのが伝わっていると嬉しいです。
なお、この記事のコードのライセンスは0BSDとします。
