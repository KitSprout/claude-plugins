# KitSprout Claude Code plugins

[English](README.md) | **繁體中文**

KitSprout 的 Claude Code 外掛。本頁是英文 README 的翻譯，兩者不一致時以英文版為準。

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install <外掛名稱>@kitsprout
```

## 外掛

| 外掛 | 用途 | 類型 |
|---|---|---|
| [`handoff`](plugins/handoff) | 換 session 前寫一份交接檔，新 session 只要讀這個檔就能接著做（「Read <路徑> and continue」）。 | skill、hook |
| [`debate`](plugins/debate) | 對設計、計畫或決策發起 subagent 辯論或多人審閱，由裁判回原始資料查證。 | skill |

安裝或更新外掛前，請確認您信任它：外掛可以在您的電腦上執行 hook 和指令。

各外掛的說明文件都有英文版和繁體中文版（`README.zh-TW.md`），請見各自的資料夾。

## Repo 結構

```
.claude-plugin/marketplace.json   marketplace：列出每個外掛
plugins/<名稱>/                   小型外掛放在這裡，一個外掛一個資料夾
  .claude-plugin/plugin.json      名稱、版本、設定
  skills/ hooks/ commands/ agents/
  evals/                          `claude plugin eval` 的測試套件（有的話）
  README.md  LICENSE
.github/workflows/validate.yml    每個 pull request 都會跑的檢查
```

較大型的工具有自己的程式、測試和發版流程，放在獨立的 repo，外掛放在其中的子資料夾。本 marketplace 用來源位置列出它們，並固定在某個發布版本：

```json
{
  "name": "<工具名稱>",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/KitSprout/<工具名稱>.git",
    "path": "plugin",
    "ref": "v1.0.0",
    "sha": "<該版本的 commit>"
  }
}
```

這類工具發布新版後，要在這裡更新 `ref` 和 `sha`，使用者才會拿到新版。

## 慣例

- **名稱不可變更。** 外掛的 `name` 是安裝時用來對應的依據。只想改顯示名稱時，改 `displayName`；非改名不可時，在 `marketplace.json` 加上 `"renames": {"舊名": "新名"}`，讓已安裝的使用者自動轉移。
- **版本號。** 每次有使用者應該收到的變更，都要提高 `plugin.json` 的 `version`。
- **測試。** 有 `evals/` 資料夾的外掛，會在自己的 README 說明執行方式和最近一次的結果。
- **翻譯。** 每份 `README.md` 旁都有一份 `README.zh-TW.md` 翻譯；兩者不一致時以英文版為準。修改任一份時，請同步更新另一份。
- **每次 push 前：** 任何檔案都不能含個人資料、金鑰、密碼、私有主機名稱或機器識別資訊。CI 會跑通用的機密掃描，但它無從得知哪些內容對您而言屬於隱私。

## 檢查項目

`.github/workflows/validate.yml` 會在每個 pull request 檢查：JSON 檔案格式正確；每個本地項目都指向一個資料夾，且其 `plugin.json` 的名稱相同；`plugins/` 底下每個資料夾都有列在 marketplace；每份 README 都有 `README.zh-TW.md`；外部來源同時有 `ref` 和 `sha`；marketplace 和每個外掛都通過 `claude plugin validate`；不需模型的外掛檢查通過；沒有提交任何機密。

## 授權

MIT，見 [LICENSE](LICENSE)。每個外掛資料夾也附有一份。
