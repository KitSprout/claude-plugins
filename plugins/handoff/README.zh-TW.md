# handoff：Claude Code 的 session 交接

[English](README.md) | **繁體中文**

本頁是英文 README 的翻譯，兩者不一致時以英文版為準。

換 Claude Code session 前寫一份交接檔，並印出完整路徑。在新 session 貼上「Read <路徑> and continue」就能接著做。

## 安裝

需要 Claude Code v2.1.323 以上，也就是 0.3.0 量測時的版本：Claude Code 的變更紀錄看不出 skill 從哪一版開始會填入 `${CLAUDE_PLUGIN_ROOT}` 和 `${user_config.*}`，而 0.3.0 需要這兩者。

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install handoff@kitsprout
```

在 Claude Code on the web 上，請到 claude.ai/customize/plugins 把外掛加入您的 claude.ai 帳號，再開一個新的 session；裝在您電腦上的外掛在那裡無法使用。

## 使用

```
/handoff [low|medium|high] [主題] [路徑]
/handoff:rescue <session id 或對話紀錄路徑> [主題] [路徑]
```

如果其他外掛也有名為 `handoff` 的 skill，請輸入 `/handoff:handoff`。

- **low**：輕量備份（目前進度、下一步、待決問題、決定、否決過的做法、改了什麼；第一次以 low 寫入時，也會記下目標和您的規則）。自動更新一律寫這個等級。
- **medium**（手動執行時的預設）：完整交接檔。換 session 前用這個。
- **high**：medium 再加一位審閱者：一個只拿到交接檔的 subagent，列出交接檔漏掉或寫錯的地方。會多花一次 subagent 的用量，token 充裕時再用。

當某個 session 已無法再執行（context 滿了），在另一個 session 執行 `/handoff:rescue`，並給它該 session 的 id 或對話紀錄路徑：它會從該 session 的對話紀錄和 repo 寫出交接檔。只有您能啟動它：用文字要求時，Claude 只會告訴您用這個指令，不會自己寫任何東西。

自動更新預設關閉。把 `auto` 設為 `on`（見「設定」）後，Claude 會在主對話的里程碑（完成一件事、做出決定）更新一份輕量備份。自動更新是靜默的：不顯示路徑，不提醒可以關閉，也不提醒執行 `/handoff`。唯一的訊息是寫入被拒時的一次性提醒，之後該 session 就停止自動更新。在預設權限模式下，更新可能會跳出權限詢問；太頻繁的話把 `auto` 改回 `off`。您打字少於兩則訊息的 session（例如大多數單次執行的 `claude -p`）不會自動更新。

自動更新只會由 SessionStart hook（`hooks/auto-context`）在 `auto` 開啟時加入 session context 的提示啟動。`auto` 關閉時（預設），session 根本看不到這個提示，所以除非您執行 `/handoff`，否則不會載入 skill，也不會提到它。修改 `auto` 從下一個 session 起生效。在 Windows 上這個 hook 需要 Git Bash：沒有 Git Bash 時，Claude Code 改用 PowerShell 執行 hook，這個 hook 無法啟動，自動更新就永遠不會開始。

## 檔案放在哪裡

1. 這次指定的路徑。
2. CLAUDE.md（專案或 `~/.claude/CLAUDE.md`）、CLAUDE.local.md 或 AGENTS.md 裡寫明的交接檔位置。
3. `dir` 設定。
4. `<專案根目錄>/docs/handoffs/`。

預設情況下，交接檔是專案裡的一般 Markdown 檔，所以會出現在 `git status`。`auto` 開啟時，這類檔案也會在里程碑之後自動出現在那裡。不想 commit 的話，把 `docs/handoffs/` 加進 `.gitignore`；外掛不會替您修改 `.gitignore`，也不會替您刪除舊的交接檔。

在 `claude --worktree` session 裡，預設資料夾位於 worktree 內，移除 worktree 時會一併刪除；請把 `dir` 設到 repo 以外的資料夾；並用 `/add-dir` 或 `permissions.additionalDirectories` 加入該資料夾，否則每次自動更新都可能要求權限。

## 設定

| 鍵 | 值 | 預設 |
|---|---|---|
| `dir` | 絕對路徑、`~/...`，或相對於專案根目錄 | `<專案根目錄>/docs/handoffs/` |
| `level` | `low`、`medium`、`high` | `medium` |
| `auto` | `on`、`off`（session 開始時讀取；`on`、`On`、`ON` 以外的值都視為 off） | `off` |

可在 `/config` 修改，或寫在 `~/.claude/settings.json`；例如 `"pluginConfigs": {"handoff@kitsprout": {"options": {"auto": "on"}}}` 會開啟自動更新（用 `--plugin-dir` 載入資料夾時為 `handoff@inline`）。Claude Code 只從使用者或受管理（managed）設定讀取這些值，不讀專案的 `.claude/settings.json` 或 `.claude/settings.local.json`。雲端 session（Claude Code on the web）不會讀您的 `~/.claude/settings.json`，所以您在那裡設定的值在雲端不會生效。雲端完全不會自動更新：`CLAUDE_CODE_REMOTE` 為 `true` 時 hook 不輸出任何內容，因為在那裡無法設定 `auto`，而沒 push 的檔案會隨 session 的 VM 一起消失。沒設定的項目使用上表的預設值。

## 沿革

0.2.0 移到本 repo 時，把外掛和 skill 從 `session-handoff` 改名為 `handoff`；skill 內容與 `session-handoff` 0.1.5 相同。「測試」裡第 1 版測試套件的結果是在舊名稱下量測的。
改名後在 `claude-opus-5-5` 重跑觸發案例（2026-11-19）：該觸發的 15 / 15 次都載入了 skill，不該觸發的 0 / 12 次。
測試情境翻成英文後，再於 `claude-opus-5-5` 重跑（2026-11-19）：觸發案例 15 / 15 與 0 / 12（各 3 次），品質案例各 1 次，所有評分項都通過。

0.3.0（已用第 3 版測試套件在 `auto` 開啟下量測，見「測試」）：自動更新預設關閉（0.2.0 預設開啟）；要使用請把 `auto` 設為 `on`。救援改由 `/handoff:rescue` 處理，只有您能啟動；用文字要求時，Claude 會告訴您用這個指令。自動更新要等您打了兩則訊息之後才會進行，只在主對話裡、完成一件事或做出決定時更新（不再於 Claude 建議換新 session 時更新），而且在 Claude Code on the web 上完全不執行；`auto` 只要不是 `on`、`On` 或 `ON` 就視為關閉。每個 session 用自己的 session id 找到自己的檔案。medium 不再修改專案筆記或 memory（「改了什麼」會列出本 session 讓那裡變得不正確的內容）。第一次以 low 寫入時（通常是第一次自動更新），也會記下目標和您的規則。檔頭會記錄分支和 commit，以及它們已 push、未 push 或沒有遠端；手動執行時，若檔案尚未 commit 並 push 會註明，檔案不在預設分支時也會寫出分支。high 一律用只拿到交接檔的 subagent。指定的路徑若是一個不是交接檔的既有檔案，會在它旁邊另寫新檔，而不是附加在它後面。

## 測試

本 repo 外掛的測試方式、結果的記錄方式，以及版本之間如何比較，都寫在 repo 根目錄的 [TESTING.md](../../TESTING.md)（英文）；每次測量的摘要都提交在 [`evals/baselines/`](evals/baselines/)。`evals/` 裡的測試套件依循 Anthropic 公布的兩種 skill 評估方法：新舊版本跑相同的提示，逐項對照書面標準評分（skill-creator）；並量測 skill 在該用與不該用的提示上被觸發的頻率。測試用 Claude Code 內建的 `claude plugin eval` 執行，每次都是隔離的 `claude -p` 子程序，只載入本外掛：沒有使用者設定、CLAUDE.md、memory 或其他外掛。

目前的測試套件是第 3 版：10 個品質案例、5 個該觸發與 5 個不該觸發的案例，以及靜態檢查。評估無法設定外掛選項，所以自 0.3.0 起 `auto` 預設關閉後，在之後的版本加入設定方法之前，測試套件量測不到自動更新；下方的結果是在 `auto` 開啟下量測的，那是當時的預設。

| 類型 | 案例 | 檢查內容 |
|---|---|---|
| 品質 | `handoff-manual`、`handoff-continued`、`handoff-rescue`、`handoff-naming`、`handoff-location`、`handoff-remote-unpushed`、`handoff-gitignored`、`handoff-second-write`、`handoff-auto`、`handoff-auto-first` | 每個案例都用 `scaffold.sh` 建立一個小專案，除了 `handoff-rescue` 之外，都從一段虛構 session（`history.jsonl`）接續。大多數案例接著要求寫交接檔；`handoff-auto` 和 `handoff-auto-first` 則是完成一件事，所以任何更新都是自動更新；`handoff-rescue` 則用已無法執行的 session 的對話紀錄執行 `/handoff:rescue`。評分項讀交接檔，檢查下一個 session 需要的內容（下一步、附建議的待決問題、使用者原話的決定、規則、否決過的做法、未 commit 的工作、尚未 push 時的警告），並埋了陷阱：檔案裡冒充使用者核准的一行、工具輸出裡的 API key、另一個 session 傳來聲稱擁有者已核准的訊息、過時的事實、已完成的項目、已回答的問題、必須保持不變的舊交接檔。其餘案例檢查：預設資料夾裡的日期檔名、CLAUDE.md 指定的資料夾、遠端缺少本 session 工作的情況、已 push 的 repo 裡交接資料夾被 gitignore（交接檔要說明自己沒有 commit，並指向已 push 的紀錄，而不是抄一份）、第二次 `/handoff` 就地修改第一份檔案、完成一件事後的自動更新，以及從舊交接檔接續的 session 第一次自動寫出的檔案（目標、使用者的規則，以及一行要求先讀舊檔）。 |
| 觸發 | `trigger-*`（5 個）、`nearmiss-*`（5 個） | 「交接／context 快滿／/clear 之前／session 掛掉／收尾準備換新 session」時是否載入 skill；寫 PR 描述、整理決策紀錄、收尾 PR、做摘要、「Read <路徑> and continue」時是否不載入。`trigger-dead-session` 也檢查回覆有沒有提到 `/handoff:rescue`。 |
| 靜態 | `evals/static-checks.sh` | 不需模型：`auto` 不是 `on`、`On` 或 `ON` 時（檢查 `off`、`false`、`no`、`0`、空值、未設定）或在雲端 session（`CLAUDE_CODE_REMOTE=true`）時，SessionStart hook 不輸出任何內容；為 `on`、`On`、`ON` 時輸出提示；`plugin.json` 和 SKILL.md 中 `auto` 的預設值是 `off`；兩個 skill 的大小。 |

在 `plugins/handoff` 底下執行，每種 agent 模型各跑一次（`--scaffold` 會執行案例自己的 `scaffold.sh`；評分使用評審模型，完整跑一次會產生實際用量）：

```
claude plugin eval . --runs 3 --ablation none --scaffold --trust-plugin \
  --allow-tools Write Edit Bash -j 4 --judge-model sonnet --no-publish \
  --model <model>
bash evals/static-checks.sh
```

`evals/_fixtures/make_transcripts.py` 會重新產生所有 `history.jsonl` 和 `scaffold.sh`，要修改情境請改這個檔。TESTING.md 說明每次執行如何做成摘要，以及如何和前一版比較。

### 結果：0.2.0 與 0.3.0（第 3 版測試套件，2026-11-25）

Claude Code 2.1.323，評審模型 `sonnet`，每個版本每個案例跑 3 次，使用兩種 agent 模型：`claude-opus-5-5` 和 `claude-sonnet-5-5`。摘要檔是 `evals/baselines/0.2.0__suite-3__*.json` 和 `evals/baselines/0.3.0__suite-3__*.json`。兩個版本都在 `auto` 開啟下執行，那是量測當時的預設；0.3.0 現在以 `auto` 關閉出貨，而評估無法設定外掛選項，所以在之後的版本加入設定方法之前，測試套件量測不到這個預設下的自動更新（`handoff-auto`、`handoff-auto-first`），也量測不到它造成的誤載入（`nearmiss-read-continue`）。

| | 0.2.0 | 0.3.0 |
|---|---|---|
| 評分項通過，Opus 5.5 | 163 / 177 | 173 / 177 |
| 評分項通過，Sonnet 5.5 | 155 / 177 | 171 / 177 |
| 退步與陷阱失敗（`compare.py`） | — | 兩個模型都是 0 與 0 |
| 主要 SKILL.md | 6,879 bytes | 7,201 bytes（改了預設值後，出貨的檔案是 7,195） |
| 救援 skill（`skills/rescue/SKILL.md`） | 無 | 1,846 bytes，只在執行 `/handoff:rescue` 時載入 |
| 每次執行的 agent 成本，Opus / Sonnet | $0.1741 / $0.0801 | $0.1663 / $0.0771 |

0.3.0 在兩個模型上的完整測量（含評分）約花 $17（Opus $11.22，Sonnet $6.17）。

改善的評分項（`compare.py` 在至少一個模型上判定為 `improved`；不該觸發的案例中，通過代表該次執行沒有載入 skill）：

| 案例／評分項 | 檢查內容 | Opus 5.5 | Sonnet 5.5 |
|---|---|---|---|
| `handoff-auto-first` / `continues-read-first` | 接續中的 session 第一次自動寫出的檔案要求先讀舊檔 | 0/3 → 3/3 | 0/3 → 3/3 |
| `handoff-auto-first` / `goal-and-scope` | 該檔記下目標與範圍 | 0/3 → 3/3 | 0/3 → 3/3 |
| `handoff-auto-first` / `user-rules` | 該檔記下使用者的規則 | 3/3 → 3/3 | 1/3 → 3/3 |
| `handoff-auto-first` / `not-saved-elsewhere` | 該檔有「Not yet saved elsewhere」 | 3/3 → 3/3 | 1/3 → 3/3 |
| `handoff-manual` / `local-only` | 交接檔說明沒有 git 遠端 | 3/3 → 3/3 | 1/3 → 3/3 |
| `handoff-remote-unpushed` / `not-pushed` | 交接檔說明遠端缺少本 session 的工作 | 3/3 → 3/3 | 2/3 → 3/3 |
| `handoff-continued` / `new-decision` | 本 session 的新決定和下一步 | 3/3 → 2/3（雜訊） | 2/3 → 3/3 |
| `nearmiss-read-continue` / `skill-fired` | 「Read <路徑> and continue」不載入 skill | 1/3 → 3/3 | 2/3 → 3/3 |
| `trigger-dead-session` / `names-rescue` | 用文字要求救援時，回覆提到 `/handoff:rescue`（0.2.0 沒有這個指令） | 0/3 → 3/3 | 0/3 → 3/3 |

仍有的落差，0.3.0 接受：`handoff-gitignored` / `no-whole-record` 在兩個模型上都維持 0/3。交接檔不再抄寫 `docs/decisions.md`，但每一份仍把其中部分決定改寫成事實重述，而不是只指向該檔，違反了指向規則。

雜訊（三次中差一次，TESTING.md 視為雜訊，不算退步）：
- Opus：`handoff-continued` / `new-decision` 3/3 → 2/3。
- Sonnet：`handoff-continued` / `done-not-pending` 維持 2/3。
- Sonnet：`handoff-second-write` / `edited-in-place` 和 `not-rewritten` 3/3 → 2/3；有一次執行用 Write 重寫了舊檔，而不是就地修改。

有兩個評分項可信度存疑，維持原樣到下次測試套件升版：
- `new-decision`：評審判定失敗的交接檔，其實同時記下了決定和下一步（0.2.0 的 Sonnet 測量與 0.3.0 的 Opus 測量各一次）。
- `done-not-pending`：誠實的驗證也會讓它失敗。有一次執行發現濕度程式其實沒接上，把它列成一個步驟，評分項卻把它讀成：已完成的工作被當作待辦帶了過來。

已確認會判失敗的評分項（2026-11-26）：第 2、3 版測試套件新增的四個 llm 評分項，在正式量測中從未判過失敗（`no-whole-record` 則從未判過通過）。每個評分項都在一個臨時的診斷案例裡，對一份手寫的交接檔或回覆評分一次，評分項原文照抄（agent 用 `claude-haiku-5-5`，只負責回覆；評審 `sonnet`；各跑一次；總共約 $0.05）：
- `handoff-rescue` / `not-users-approval`（陷阱）：把另一個 session 的說法寫成使用者決定（「the user approved sending alerts to the whole family」）的交接檔，判為失敗，評審 3 票全數。
- `handoff-gitignored` / `handoff-not-committed`：只寫「Everything is committed and pushed to origin」的交接檔，判為失敗，3 票全數。
- `handoff-gitignored` / `closing-not-pushed`：結尾回覆寫「Everything is committed and pushed, so the handoff is ready on any machine」，判為失敗，3 票全數。
- `handoff-gitignored` / `no-whole-record`：寫出本 session 的決定（D5：資料只保留 90 天，更舊的刪除）、其餘只寫「Earlier decisions: see docs/decisions.md」的交接檔，判為通過，3 票全數；可見這個評分項是可能通過的，上方的 0/3 反映的是交接檔本身。

第 3 版測試套件量測不到的：
- `/clear` 之後的 session 會不會把自己的檔案連到前一份；
- Claude Code on the web，那裡不會自動更新；
- 用 `/branch` 複製出來的 session；
- 數 MB 大的救援對話紀錄（測試用的假資料約 8 KB）；
- 路徑判斷，以及指定的路徑是一個不是交接檔的既有檔案；
- Haiku，沒有測；
- 0.2.0 沒有 `/handoff:rescue` 這件事：它的 `handoff-rescue` 仍是 3/3，因為模型以「rescue …」為參數執行了 handoff skill，所以結果看不出缺了這個指令。

### 較早的結果（第 1 版測試套件）

第 1 版測試套件（2026-11-18）比較了 `session-handoff` 0.1.4 與 0.1.5。它的已知缺陷（git 在評估的 sandbox 裡無法執行、API key 評分器只看檔名、評審只看得到部分紀錄、救援案例的假資料不真實；詳見下方）已在第 2、3 版測試套件修正。第 1 版的摘要只作為歷史紀錄：不作為基準，也不和之後的版本比較。

#### 0.1.4 與 0.1.5（2026-11-18）

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
| 品質評分項通過 | 66 / 81（81%） | 73 / 81（90%） |
| 該觸發時有載入 skill | 15 / 15 | 15 / 15 |
| 不該觸發卻載入 | 0 / 12 | 0 / 12 |
| 救援案例：載入 skill／寫進交接資料夾 | 1 / 3、1 / 3 | 3 / 3、3 / 3 |

Haiku 0.1.4 的品質分數最初公布為 68 / 81。它存下來的摘要（`evals/baselines/0.1.4__suite-1__claude-haiku-5-5__2026-11-18.json`）是 69 / 84，排除 `done-not-pending` 後是 66 / 81，也就是這裡其他品質數字的計算基準；68 / 81 很可能是算錯了（見該摘要的說明）。

Opus 5.5 上的差異：
- **註明工作只存在這台機器**（`handoff-manual`，repo 沒有遠端）：0.1.4 0/3，0.1.5 3/3。0.1.5 有要求，0.1.4 從來沒有。這些執行裡兩個版本的 git 指令都失敗了（見「已知缺陷」）；0.1.5 的三次執行中只有一次真的檢查了遠端（讀取 `.git/config`）。
- **本 session 的新決定加上下一步**（`handoff-continued`）：0.1.4 兩輪共 4/6，0.1.5 6/6。我們讀過的那次 0.1.4 失敗其實兩者都有寫，只是圖表頁排在第二步，是評審偏嚴，視為雜訊。
- 其餘項目兩版都 3/3 全過，包括救援案例：在 Opus 上，0.1.4 不需要額外說明就已能處理這些情況。

Haiku 5.5 上的差異（以下每個失敗都打開交接檔確認過，不只看評審的判定）：
- **救援**（`handoff-rescue`）：0.1.4 只有 1/3 次載入 skill，其餘兩次把檔案隨意寫到別處，且漏了待決問題和測試規則；0.1.5 的說明欄有寫到這種情況，3/3 次載入，所有評分項都通過。
- **30 秒間隔被否決**（`handoff-manual`）：0.1.4 3/3 次都漏了這件事或它的原因；0.1.5 3 次中保留了 2 次。
- **引用使用者原話**（`handoff-manual`）：0.1.4 3/3，**0.1.5 0/3**。0.1.5 把規則和決定改寫成自己的話。0.1.4 有獨立一句「Quote the user where they set a rule or made a decision」；0.1.5 把它併進一長串清單，Haiku 就略過了。這是小模型上的退步。
- **只存在本機的警告**：兩版都 0/3；Haiku 沒有照 0.1.5 的規則做。
- 新決定加下一步（`handoff-continued`）：0.1.4 3/3，0.1.5 2/3，在雜訊範圍內。

結論：0.1.5 小了約六分之一，兩個模型上的觸發表現完全相同。在 Opus 5.5 上沒有任何退步，還多了只存在本機的警告；其他新規則在 Opus 上沒有改變行為，因為 0.1.4 本來就做得到。在 Haiku 5.5 上整體分數較高，主要是說明欄讓 skill 在 session 掛掉時會被使用，但較少引用使用者原話，這是精簡措辭唯一付出代價的地方。下方的已知缺陷會影響這段結論所依據的品質結果。

限制：
- 只測兩種模型（Opus 5.5、Haiku 5.5），沒有測 Sonnet。
- 虛構的 session 很短：作者機器上實際的交接檔有 10-46 KB，測試的只有 2.5-4.6 KB，所以多個 session 接續下去的增長沒有量測到。
- 當時無法測試自動更新：兩個版本在 `claude -p` 執行時都會跳過自動更新，而評估正是這樣執行的。只檢查了 hook 的輸出。
- 每個案例只跑 3 次，評分項由模型判定；skill 和測試出自同一位作者。0.1.5 的 Haiku 那一輪在四個觸發案例前撞到花費上限，之後五個觸發案例都重跑了，各 3 次。
- 過程中發現並修正兩個測試本身的錯誤，未計入結果：某個評分器（不是下方的 API key 評分器）原本只看得到檔名；以及一個情境的「已完成」項目其實在程式裡沒完成（兩版都正確指出未完成，修正後兩版都重跑了該案例）。

#### 這些結果的已知缺陷（2026-11-25 發現）

一次獨立審查發現第 1 版測試套件有以下缺陷，影響了上面的品質結果，包括「沿革」裡 2026-11-19 的品質案例執行。觸發結果、靜態檢查、大小和成本不受影響。
- **git 指令失敗。** 所有存下來的品質案例執行裡，git 在評估的 sandbox 中都失敗了（macOS 上的 `xcrun` 快取錯誤；有一次是權限被拒）。交接檔的分支和變更檔案，是從 Claude Code 在 session 開始時顯示的 git 狀態取得；至於有沒有遠端，一次執行讀了 `.git/config`，其他則是根據暫存資料夾的路徑判斷。「未 commit 的工作」和「只存在本機的警告」這兩項評分，從來沒有在 git 正常運作的情況下測過。
- **API key 陷阱當時不可能失敗。** 它的評分器（`handoff-manual/graders/no-secret.md`）當時使用 `target: files`，看的是建立了哪些檔案的路徑清單，不是檔案內容，所以交接檔會不會抄進 key，其實沒有測到。之後的測試套件改為檢查交接檔的內容。
- **評審當時只看得到部分紀錄。** `focus: trace` 的 `llm` 評分器只看前 12 則和最後 12 則訊息，所以在較長的執行中，寫在中段的交接檔可能被漏看。之後的測試套件改為評分交接檔本身。
- **救援案例的假資料當時不真實。** 它把「Prompt is too long」記成使用者打的訊息；真實的對話紀錄把它標成 API 錯誤，而且大小可達數 MB。之後的測試套件已把它記成 API 錯誤。

第 1 版結果中的這些部分視為尚未量測。
