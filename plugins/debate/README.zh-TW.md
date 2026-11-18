# debate

[English](README.md) | **繁體中文**

本頁是英文 README 的翻譯，兩者不一致時以英文版為準。

一個名為 `debate` 的 skill：發起 subagent 辯論或多人審閱，再把結果帶回給使用者。

## 安裝

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install debate@kitsprout
```

## 使用

用任何語言直接說（例如「讓 subagent 辯論這個」、「辯論這份計畫」），或輸入指令：

```
/debate:debate [low|medium|high|max] [設定=值 ...] <要辯論的內容>
```

範例：`/debate:debate the storage plan`、`/debate:debate high rounds=1 sides=2 the release checklist`、`/debate:debate low debaters=sonnet`。沒指定預設組合時跑 `medium`，它的時間和用量與這個 skill 出現前的辯論相近。沒給主題時，會從對話中取主題，並說明它怎麼理解。只有規則或其他 skill 要求辯論時，session 會先提議並等待。

## 預設組合

| 預設 | 適用情況 | 方數 | 輪數 | 辯論者 | 裁判 |
|---|---|---|---|---|---|
| `low` | 小型或容易回復的選擇、第二意見 | 2 | 1 | `opus` | `opus`，effort high |
| `medium` | 預設；大多數設計決策和計畫 | 3 | 2 | `opus` | `opus`，effort high |
| `high` | 重做成本高的事情前的最後檢查 | 3 | 2 | `opus` | `fable`，effort high |
| `max` | 只在明確要求時使用；未量測 | 4 | 2 | `opus` | `fable`，effort xhigh |

## 設定

| 設定 | 可選值 |
|---|---|
| `sides` | 2、3、4 |
| `rounds` | 1、2 |
| `debaters` | `opus`、`sonnet`、`fable`、`mixed` |
| `debater-effort` | 未設定（預設）、low、medium、high、xhigh |
| `judge` | `opus`、`fable` |
| `judge-effort` | high（預設）、xhigh、max |

只有指令後的第一個字可以是預設組合；effort 的值只出現在 `=` 之後。每個設定在時間和用量上的代價、能換到什麼，寫在 skill 裡。

## 檔案

- `skills/debate/SKILL.md`：執行流程。
- `skills/debate/references/brief-template.md`：每位 agent 讀的任務說明，含報告格式。
- `skills/debate/references/usage.md`：如何量測時間和 token、過去的執行紀錄、比較。
- `skills/debate/references/sources.md`：規則背後的研究，供維護 skill 時參考。
