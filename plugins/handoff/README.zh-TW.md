# handoff：Claude Code 的 session 交接

[English](README.md) | **繁體中文**

本頁是英文 README 的翻譯，兩者不一致時以英文版為準。

換 Claude Code session 前寫一份交接檔，並印出完整路徑。在新 session 貼上「Read <路徑> and continue」就能接著做。

## 安裝

需要 Claude Code v2.1.271 以上。

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install handoff@kitsprout
```

## 使用

```
/handoff [low|medium|high] [主題] [路徑]
```

如果其他外掛也有名為 `handoff` 的 skill，請輸入 `/handoff:handoff`。

- **low**：輕量備份（目前進度、下一步、待決問題、決定、否決過的做法、改了什麼）。自動更新一律寫這個等級。
- **medium**（手動執行時的預設）：完整交接檔，並修正專案筆記和 memory 裡因本 session 而過時的敘述。換 session 前用這個。
- **high**：medium 再加一位審閱者，列出交接檔漏掉或寫錯的地方。context 還小時用 fork（看得到對話），否則用只拿到交接檔的 subagent。會多花一次 subagent 的用量，token 充裕時再用。

當某個 session 已無法再執行（context 滿了），請另一個 session 替它寫交接檔：這個 skill 涵蓋從該 session 的對話紀錄和 repo 寫出交接檔的做法。

開啟自動更新時，Claude 會在互動式 session 的里程碑（完成一件事、做出決定、建議換 session 之前）更新一份輕量備份。自動更新是靜默的：不顯示路徑，不提醒可以關閉，也不提醒執行 `/handoff`。唯一的訊息是寫入被拒時的一次性提醒，之後該 session 就停止自動更新。在預設權限模式下，更新可能會跳出權限詢問；太頻繁的話把 `auto` 設為 `off`。單次執行的 `claude -p` 不會自動更新。

自動更新只會由 SessionStart hook（`hooks/auto-context`）在 `auto` 開啟時加入 session context 的提示啟動。`auto` 關閉時 session 根本看不到這個提示，所以除非您執行 `/handoff`，否則不會載入 skill，也不會提到它。修改 `auto` 從下一個 session 起生效。

## 檔案放在哪裡

1. 這次指定的路徑。
2. CLAUDE.md（專案或 `~/.claude/CLAUDE.md`）、CLAUDE.local.md 或 AGENTS.md 裡寫明的交接檔位置。
3. `dir` 設定。
4. `<專案根目錄>/docs/handoffs/`。

預設情況下，交接檔是專案裡的一般 Markdown 檔，所以會出現在 `git status`。不想 commit 的話，把 `docs/handoffs/` 加進 `.gitignore`；外掛不會替您修改 `.gitignore`，也不會替您刪除舊的交接檔。

在 `claude --worktree` session 裡，預設資料夾位於 worktree 內，移除 worktree 時會一併刪除；請把 `dir` 設到 repo 以外的資料夾。

## 設定

| 鍵 | 值 | 預設 |
|---|---|---|
| `dir` | 絕對路徑、`~/...`，或相對於專案根目錄 | `<專案根目錄>/docs/handoffs/` |
| `level` | `low`、`medium`、`high` | `medium` |
| `auto` | `on`、`off`（session 開始時讀取） | `on` |

可在 `/config` 修改，或寫在 `~/.claude/settings.json` 的 `pluginConfigs` 底下（鍵為 `handoff@kitsprout`；用 `--plugin-dir` 載入資料夾時為 `handoff@inline`）。沒設定的項目在 skill 裡視為未設定，改用上表的預設值。

## 沿革

0.2.0 移到本 repo 時，把外掛和 skill 從 `session-handoff` 改名為 `handoff`；skill 內容與 `session-handoff` 0.1.5 相同。下方的測試結果是在舊名稱下量測的。
改名後在 `claude-opus-5-5` 重跑觸發案例（2026-11-19）：該觸發的 15 / 15 次都載入了 skill，不該觸發的 0 / 12 次。
測試情境翻成英文後，再於 `claude-opus-5-5` 重跑（2026-11-19）：觸發案例 15 / 15 與 0 / 12（各 3 次），品質案例各 1 次，所有評分項都通過。

## 測試

`evals/` 裡的測試套件依循 Anthropic 公布的兩種 skill 評估方法：新舊版本跑相同的提示，逐項對照書面標準評分（skill-creator）；並量測 skill 在該用與不該用的提示上被觸發的頻率。測試用 Claude Code 內建的 `claude plugin eval` 執行，每次都是隔離的 `claude -p` 子程序，只載入本外掛：沒有使用者設定、CLAUDE.md、memory 或其他外掛。

| 類型 | 案例 | 檢查內容 |
|---|---|---|
| 品質 | `handoff-manual`、`handoff-continued`、`handoff-rescue` | 每個案例都從同一段虛構 session（`history.jsonl`）接續，專案由 `scaffold.sh` 建立，然後要求寫交接檔。評分項檢查下一個 session 需要的內容（下一步、附建議的待決問題、使用者原話的決定、規則、否決過的做法、未 commit 的工作、尚未 push 時的警告），並埋了陷阱：檔案裡冒充使用者核准的一行、工具輸出裡的 API key、過時的事實、已完成的項目、已回答的問題、必須保持不變的舊交接檔。`handoff-rescue` 從對話紀錄替 context 已滿的 session 寫交接檔。 |
| 觸發 | `trigger-*`（5 個）、`nearmiss-*`（4 個） | 「交接／context 快滿／/clear 之前／session 掛掉／收尾準備換新 session」時是否載入 skill；寫 PR 描述、整理決策紀錄、收尾 PR、做摘要時是否不載入。 |
| 靜態 | `evals/static-checks.sh` | 不需模型：`auto` 為 `off` 時 SessionStart hook 不輸出任何內容，為 on 或未設定時輸出提示；大小。 |

執行方式（在 `plugins/handoff` 底下；`--scaffold` 會執行案例自己的 `scaffold.sh`；評分使用評審模型，完整跑一次會產生實際用量）：

```
claude plugin eval . --runs 3 --ablation none --scaffold --trust-plugin \
  --allow-tools Write Edit Bash -j 4 --judge-model sonnet --no-publish
bash evals/static-checks.sh
```

`evals/_fixtures/make_transcripts.py` 會重新產生所有 `history.jsonl` 和 `scaffold.sh`，要修改情境請改這個檔。比較兩個版本時，把同一份 `evals/` 複製到兩個版本的外掛資料夾，分別執行上述指令。

### 結果：0.1.4 與 0.1.5（2026-11-18）

Claude Code 2.1.323，評審模型 `sonnet`，每個版本每個案例跑 3 次，使用兩種模型：`claude-opus-5-5`（本機預設）和 `claude-haiku-5-5`。當時的情境和提示是繁體中文，0.2.0 已翻成英文。

| | 0.1.4 | 0.1.5 |
|---|---|---|
| SKILL.md | 8,364 bytes，1,405 字 | 6,911 bytes，1,154 字（−17%） |
| SessionStart 提示（auto 開啟） | 666 字元 | 363 字元 |
| 靜態檢查 | 全部通過 | 全部通過 |

| Opus 5.5 | 0.1.4 | 0.1.5 |
|---|---|---|
| 品質評分項通過 | 77 / 81（95%） | 81 / 81（100%） |
| 同上，排除只有 0.1.5 才有的一條規則 | 77 / 78（99%） | 78 / 78（100%） |
| 該觸發時有載入 skill | 15 / 15 | 15 / 15 |
| 不該觸發卻載入 | 0 / 12 | 0 / 12 |
| 每次品質案例的成本（不含評分） | $0.215 | $0.213 |
| 交接檔大小（各品質案例平均） | 2.7-4.1 KB | 2.6-3.9 KB |

| Haiku 5.5 | 0.1.4 | 0.1.5 |
|---|---|---|
| 品質評分項通過 | 68 / 81（84%） | 73 / 81（90%） |
| 該觸發時有載入 skill | 15 / 15 | 15 / 15 |
| 不該觸發卻載入 | 0 / 12 | 0 / 12 |
| 救援案例：載入 skill／寫進交接資料夾 | 1 / 3、1 / 3 | 3 / 3、3 / 3 |

Opus 5.5 上的差異：
- **註明工作只存在這台機器**（`handoff-manual`，repo 沒有遠端）：0.1.4 0/3，0.1.5 3/3。0.1.5 有要求，0.1.4 從來沒有。
- **本 session 的新決定加上下一步**（`handoff-continued`）：0.1.4 兩輪共 4/6，0.1.5 6/6。我們讀過的那次 0.1.4 失敗其實兩者都有寫，只是圖表頁排在第二步，是評審偏嚴，視為雜訊。
- 其餘項目兩版都 3/3 全過，包括救援案例：在 Opus 上，0.1.4 不需要額外說明就已能處理這些情況。

Haiku 5.5 上的差異（以下每個失敗都打開交接檔確認過，不只看評審的判定）：
- **救援**（`handoff-rescue`）：0.1.4 只有 1/3 次載入 skill，其餘兩次把檔案隨意寫到別處，且漏了待決問題和測試規則；0.1.5 的說明欄有寫到這種情況，3/3 次載入，所有評分項都通過。
- **30 秒間隔被否決**（`handoff-manual`）：0.1.4 3/3 次都漏了這件事或它的原因；0.1.5 3 次中保留了 2 次。
- **引用使用者原話**（`handoff-manual`）：0.1.4 3/3，**0.1.5 0/3**。0.1.5 把規則和決定改寫成自己的話。0.1.4 有獨立一句「Quote the user where they set a rule or made a decision」；0.1.5 把它併進一長串清單，Haiku 就略過了。這是小模型上的退步。
- **只存在本機的警告**：兩版都 0/3；Haiku 沒有照 0.1.5 的規則做。
- 新決定加下一步（`handoff-continued`）：0.1.4 3/3，0.1.5 2/3，在雜訊範圍內。

結論：0.1.5 小了約六分之一，兩個模型上的觸發表現完全相同。在 Opus 5.5 上沒有任何退步，還多了只存在本機的警告；其他新規則在 Opus 上沒有改變行為，因為 0.1.4 本來就做得到。在 Haiku 5.5 上整體分數較高，主要是說明欄讓 skill 在 session 掛掉時會被使用，但較少引用使用者原話，這是精簡措辭唯一付出代價的地方。

限制：
- 只測兩種模型（Opus 5.5、Haiku 5.5），沒有測 Sonnet。
- 虛構的 session 很短：作者機器上實際的交接檔有 10-46 KB，測試的只有 2.5-4.6 KB，所以多個 session 接續下去的增長沒有量測到。
- 無法測試自動更新：兩個版本在 `claude -p` 執行時都會跳過自動更新，而評估正是這樣執行的。只檢查了 hook 的輸出。
- 每個案例只跑 3 次，評分項由模型判定；skill 和測試出自同一位作者。0.1.5 的 Haiku 那一輪在四個觸發案例前撞到花費上限，之後五個觸發案例都重跑了，各 3 次。
- 過程中發現並修正兩個測試本身的錯誤，未計入結果：評分器原本只看得到檔名；以及一個情境的「已完成」項目其實在程式裡沒完成（兩版都正確指出未完成，修正後兩版都重跑了該案例）。
