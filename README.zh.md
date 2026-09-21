# Tsumugy-Narrative

**Languages:** [English](README.md) · [日本語](README.ja.md) · **中文（这里）** · [한국어](README.ko.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [Русский](README.ru.md)

## 这是什么

https://github.com/user-attachments/assets/82d17d1e-6d3e-4422-b317-80a751a913e5

仓库中的同一文件：[demo-claude.mp4](docs/assets/demo-claude.mp4)

> 一个把文字变成高质量故事的简单技能。它产出一篇故事：故事正文、一段简短讲解，以及一个出处标记。

我是一名医学生。我需要一种在短时间内掌握难懂概念的方法。我曾试着画图来记忆。我请 AI 替我画图。但 AI 画不出精确的图。于是我有了一个新想法：把像画面一样的场景变成故事。效果非常好，它真的帮我掌握了复杂的概念。我把故事分享给朋友，他们说公共卫生统计学一下子变简单了。一句简单的指令每次输出都不一样，所以你总得告诉它"讲得再有趣一点"或者"这个比喻我没懂"。这个技能自带自检脚本，它会检查每一篇故事。所以每一篇故事，每一次，都保持高质量。

输入示例：

```
Good morning, everyone. Today we close the pharmacology lecture series. The midterm exam is next week. As before, I will answer your questions as we go. Many of you asked for a drug that fixes daytime sleepiness. I want one too. First-generation antihistamines cross the blood-brain barrier, so they bring sleepiness, dry mouth, and difficulty urinating. Second-generation drugs mostly stay out of the brain, so they calm allergy symptoms without the sleepiness...
（摘录。90 分钟讲座录音。）
```

<details>
<summary>输出示例：</summary>

```
## 故事

### 鼻腔里的小小烟花

平静的春日午后，《春日花粉雪》🌸(花粉)悄无声息地飘进鼻腔深处。

鼻腔里，《鼻腔烟花》🎆(喷嚏)啪地一声绽开，干脆的声响穿过隐隐作痛的脑袋，高高回荡。

《流水的水龙头鼻子》🚰(流涕)像眼泪一样一滴一滴往下淌，冰凉的触感一直渗到干裂的嘴唇。

看不见的《嗡嗡作响的线电话》📞(副交感神经)在甜甜的花香背后低低 humming。

接着，《堵路的砖块》🧱(白三烯)在鼻腔的路上越堆越高，《堵塞的灯笼》🏮(鼻塞)泛起深红的光。

不要责怪鼻子。只有知道幕后班底的人，才能熬过漫长的春天。

## 讲解

看不见的《嗡嗡作响的线电话》📞(副交感神经)在甜甜的花香背后低低地响着。

> 出处：药理讲座 30:12

voice: DA (fragile-confession style)

## 故事

### 油腻的老路与子弹列车

在摆满药摊的集市上，《油腻的老路》🛢️(第一代抗组胺药)散发着油味，绵绵向前。

老路轻轻松松穿过《大脑关卡》🚧(血脑屏障)，连正午惨白的日光都被它搅浑了。

旅人一屁股陷进《瞌睡坐垫》🛋️(嗜睡)，远远听着冰冷的风声，直直坠入深眠。

嘴里只剩下一个《干瘪的水壶》🥤(口干)，苦味在舌面上漫开，化作缓慢的不安。

《生锈的水龙头》🔩(排尿困难)一点也拧不动，责骂声挤满了整条街。

别贪便宜的困意，选清醒安稳的白天吧。《子弹列车票》🎫(第二代抗组胺药)才是真正的答案。

## 讲解

一个关于新老两代抗组胺药的热闹故事。老路象征第一代，车票象征第二代，坐垫象征嗜睡。

> 出处：药理讲座 48:52

voice: MA (crowded-street style)
```

</details>

## 快速上手（1 分钟）

两条路任选一条，两条都只要一分钟左右。

### Claude 应用（不用终端）

1. 下载发布包：[narrative-formatter.skill](dist/narrative-formatter.skill)。
2. 打开 Claude 应用。打开汉堡菜单。去 Customize。按 Add。
3. 把文件拖进去。打开代码执行。
4. 在聊天里提问，给出材料和模式。

https://github.com/user-attachments/assets/e70f9b9c-9f10-4012-85fe-a42d782cffb6

仓库中的同一文件：[install-claude.mp4](docs/assets/install-claude.mp4)

如果上传失败，重新下载发布包。如果看不到 Skills 一项，打开代码执行。

### Coding agent（终端）

所有 coding agent 的首选都是 Npx。Npx 随 Node.js 一起安装。先装好它：https://nodejs.org/

```bash
npx skills add Karimuto/tsumugy-narrative
npx skills list
```

## 用法

写故事只需要调用一次技能。在 Claude 应用或 ClaudeCode、Codex、Pi、OpenCode 这样的 Coding agent 里输入：

```
/narrative-formatter <input file>. mode: <mode (optional)>.
```

比如，写在输入文件旁边：

```
/narrative-formatter "pharmacology2Lect3.pdf" (or drug and drop some files). mode: serial.
```

三种模式（默认 `fable`）：

- **episodic**：忠实于原文，每章一个独立成篇的故事。
- **serial**：同一个主人公、同一个世界，一集接一集连载。记忆靠 ledger 延续。
- **fable**（默认）：印象优先，允许一定程度的不准确，力求让人难忘。

## 工作原理

六步。每一步都很简单，高中生也能看懂。

1. 读难懂的文字，找出关键概念和它们之间的联系。
2. 搭一个小场景，用会行动、会有感受的人物。
3. 把每个难词包进比喻里，用括号标出来。
4. 给每个人、每样东西配一个 emoji。同一个东西每次出现都用同一个 emoji。
5. 起草故事：标题、故事正文、简短讲解、出处标记。
6. 跑自检脚本。它会给出 PASS、CONDITIONAL PASS 或 FAIL。把点名的问题改掉。只交付 PASS 或 CONDITIONAL PASS 的作品。

连载的 Thread 带一本 Ledger。Ledger 存着世界和人物。每一集新故事都先读 Ledger。

## Contributing

读 [CONTRIBUTING.md](CONTRIBUTING.md)（权威版本；[日本語](CONTRIBUTING.ja.md) · [中文](CONTRIBUTING.zh.md)）。Issue 和 pull request 欢迎用日语或英语。

## 许可证

![MIT](https://img.shields.io/badge/license-MIT-green) ![version](https://img.shields.io/badge/version-0.1.0-blue)

MIT（[LICENSE](LICENSE)）。
