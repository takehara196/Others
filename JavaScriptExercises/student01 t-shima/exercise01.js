export function q01(){
    // console.log('1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47, 48, 50');
    let arr = [];
    for (let i = 1; i <= 50; i++){
        let ans = i % 7;
        if (ans != 0) {
            console.log(i);
        }
    }
}

export function q02(){
    // console.log([7, 14, 21, 28, 35, 42, 49]);
    let arr = [];
    for (let i = 1; i < 50; i++){
        let ans = i % 7;
        if (ans == 0) {
            arr.push(i);
        }
    }
    console.log(arr);
}
export function q02a(){
    // console.log([7, 14, 21, 28, 35, 42, 49]);
    let arr = [];   // 配列初期化
    let i = 1;  // 初期値１
    let ans = 0;    // 初期値0
    while (i < 10000) {
        //ループ ()内が成立する内はループを実行する 49でもOK  true は常に正なので常にループ(無限ループ) 
        // i < 10000 無限じゃなくて10000で終わらせる保険的な書き方 ans<50 or true
        ans = i * 7;    // ans 1*7=7, 2*7=14, 3*7=21 ...    8*7=56
        if (ans >= 50) {  //50以上だったら
            break;          // break ループを止めてループを抜ける 56の時抜ける
        }
        arr.push(ans);  //配列を追加 7,14,21,28,...,49
        /*  7に7を足していく方法もあり
        i += 7; //i = i + 7; i -= 7; i *= 7; etc...
        */
        i += 1; // iに1を足してiに格納  2,3,4...,7,8
    }
    console.log(arr);
}

export function q05() {
    // Math.sin サインの計算
    // PI → π
    // x° = x * π / 180 ラジアン
    let ans = 0;
    for (let i = 1; i <= 90; i++) {
        ans = Math.sin(i * (Math.PI / 180));
        console.log(ans);
    }
}

export function q06() {
    //ボタン押す前提でよい？
    let inp = document.getElementById('input1').value;
    document.getElementById('q06_box').innerText = inp;
}

export function q08(){
    // let inp2 = parseInt(document.getElementById('input1').value);
    // let ans2 = inp2.toString(2);
    // console.log(ans2);
    let arr = [];
    let inp = parseInt(document.getElementById('input1').value);
    if (inp !== 0) {
        while (inp > 0) {
            let sur = inp % 2;
            inp = Math.floor(inp / 2);
            arr.unshift(sur);
        }
    }
    let sen = "";
    for (let i = 0; i < arr.length; i++){
        sen = sen + arr[i];
    }
    console.log(sen);
}