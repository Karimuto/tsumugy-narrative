# Tsumugy-Narrative

**Languages:** **English (here)** · [日本語](README.ja.md) · [中文](README.zh.md) · [한국어](README.ko.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [Русский](README.ru.md)

## What is this

https://github.com/user-attachments/assets/82d17d1e-6d3e-4422-b317-80a751a913e5

Same video as a repo file: [demo-claude.mp4](docs/assets/demo-claude.mp4)

> A simple skill that turns text into high-quality stories. It makes a Story: a story body, a short explanation, and a Source marker.

I am a medical student. I needed a way to grasp hard concepts in a short time. I tried to draw pictures to remember them. I asked AI to draw the pictures for me. But AI could not draw exact pictures. So I had a new idea: I turn a scene that feels like a picture into a Story. It worked very well. It really helped me grasp complex concepts. I shared my stories with friends. They said statistics in public health felt very easy. A plain instruction gives a different output every time, so you always have to tell it, "Make it more fun," or "I don't get the metaphor." This skill ships a self-check script. It checks each Story. So each Story keeps high quality, each time.

Input example:

```
Good morning, everyone. Today we close the pharmacology lecture series. The midterm exam is next week. As before, I will answer your questions as we go. Many of you asked for a drug that fixes daytime sleepiness. I want one too. First-generation antihistamines cross the blood-brain barrier, so they bring sleepiness, dry mouth, and difficulty urinating. Second-generation drugs mostly stay out of the brain, so they calm allergy symptoms without the sleepiness...
(Excerpt. 90-minute lecture recording.)
```

<details>
<summary>Output example:</summary>

```
## Story

### The Small Fireworks in the Nose

On a calm spring afternoon, ⟨spring pollen snow⟩🌸(pollen) fell without sound deep into the nose.

Inside the nose, ⟨nose fireworks⟩🎆(sneeze) burst open with a bright crack, and the dry sound rang high through the aching head.

From the ⟨running faucet nose⟩🚰(runny nose), water dripped drop by drop like tears, and its cold touch reached the dry lips.

An unseen ⟨buzzing string telephone⟩📞(parasympathetic nerve) hummed behind the sweet flower smell.

Then ⟨traffic-jam bricks⟩🧱(leukotriene) piled high across the nose road, and the ⟨blocked lantern⟩🏮(stuffy nose) glowed deep red.

Do not blame the nose. Only those who know the backstage crew survive the long spring.

## Notes

A sad little tale of hay fever: sneezing, a runny nose, and a stuffy nose. Fireworks stand for sneezing, the faucet for a runny nose, bricks for leukotriene.

> Source: Pharmacology lecture 30:12

voice: DA (fragile-confession style)

## Story

### The Greasy Old Road and the Bullet Train

In a market lined with drug stalls, a ⟨greasy old road⟩🛢️(first-generation antihistamines) stretched long, smelling of oil.

The old road slipped through the ⟨brain checkpoint⟩🚧(blood-brain barrier) with ease, and clouded even the white noon light.

A traveler sank onto the ⟨sleep cushion⟩🛋️(drowsiness) and dropped deep, hearing the cold wind far away.

Only a ⟨dry canteen⟩🥤(dry mouth) stayed in the mouth, and a bitter taste spread slow unease across the tongue.

The ⟨rusty faucet⟩🔩(difficulty urinating) would not turn at all, and scolding voices filled the street.

Choose steady waking hours over cheap sleepiness. The ⟨bullet-train ticket⟩🎫(second-generation antihistamines) is the true answer.

## Notes

A lively tale of old and new antihistamines. The old road stands for the first generation, the ticket for the second, the cushion for sleepiness.

> Source: Pharmacology lecture 48:52

voice: MA (crowded-street style)
```

</details>

## Quick start (1 minute)

Pick your track. Both tracks take about one minute.

### Claude app (no terminal)

1. Download the pack: [narrative-formatter.skill](dist/narrative-formatter.skill).
2. Open the Claude app. Open the hamburger menu. Go to Customize. Press Add.
3. Drag and drop the file. Turn on code execution.
4. Ask in chat. Give the material and the mode.

https://github.com/user-attachments/assets/e70f9b9c-9f10-4012-85fe-a42d782cffb6

Same video as a repo file: [install-claude.mp4](docs/assets/install-claude.mp4)

If upload fails, download the pack again. If you see no Skills item, turn on code execution.

### Coding agent (terminal)

First choice for all coding agents: Npx. Npx comes with Node.js. Install it first: https://nodejs.org/

```bash
npx skills add Karimuto/tsumugy-narrative
npx skills list
```

## Usage

Making a story only requires one skill call. In Claude app or Coding agent like ClaudeCode, Codex, Pi, or OpenCode. Type:

```
/narrative-formatter <input file>. mode: <mode (optional)>.
```

Example, writing next to the input:

```
/narrative-formatter "pharmacology2Lect3.pdf" (or drug and drop some files). mode: serial.
```

Three modes (default `fable`):

- **episodic**: faithful to the text, one self-contained story per chapter. 
- **serial**: one protagonist and one world continued across episodes. Memory carries over in the ledger.
- **fable** (default): impression-first, tolerating some inaccuracy to stay memorable.

## How it works

Six steps. Each step is simple. A high school reader can follow them.

1. Read the hard text. Find the key ideas and how they connect.
2. Build a small scene. Use people who do things and feel things.
3. Wrap each hard word in a metaphor. Mark it with brackets.
4. Give each person and thing one emoji. Use the same emoji each time it shows up.
5. Draft the Story: title, story body, short explanation, Source marker.
6. Run the self-check script. It reads PASS, CONDITIONAL PASS, or FAIL. Fix what it names. Deliver only PASS or CONDITIONAL PASS work.

A serial Thread keeps a Ledger. The Ledger stores the world and the people. Each new episode reads the Ledger first.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) (canonical; [日本語](CONTRIBUTING.ja.md) · [中文](CONTRIBUTING.zh.md)). Issues and pull requests welcome in Japanese or English.

## License

![MIT](https://img.shields.io/badge/license-MIT-green) ![version](https://img.shields.io/badge/version-0.1.0-blue)

MIT ([LICENSE](LICENSE)).
