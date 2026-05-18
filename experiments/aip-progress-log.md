# Aip Progress Log

> Source: Notion (exported 2026-05-18)

> 每次重要節點後更新這頁，新對話時告訴 Claude「去我的 Notion 看 AIP 進度頁面」即可。

---

## 基本資訊

- 項目名稱：Autonomous Intent-integrity Protocol (AIP)

- 目標：AI Agent 鏈上授權安全協議，推甄研究所用

- 技術棧：ERC-7579 Hook + EIP-1153 TSTORE + GoPlus 黑名單

- 指導教授：掛通訊作者

- GitHub：https://github.com/USDHGwang/aip-protocol

- 論文目標：期刊版本（10 成），清明（4/4）前完成

- 投稿狀態：已投稿 IEEE Transactions on Dependable and Secure Computing（TDSC），Submission ID: dc725cd4-d5d0-412e-a226-4f996940fed6，投稿日期：2026-03-29

---

## 當前狀態（2026-03-29）

- 44 項測試全過（含動態 δ）

- 教授已開始動筆，目前約兩頁，目標 4/4 清明完成

- 預計投 IEEE 期刊

- 三份合約已部署 Monad Testnet

- 與 Box（Monad DevRel）技術辯論進行中，澄清 AIP 核心防禦邊界

- ✅ 2026-03-29：論文正式投稿 IEEE TDSC（CCF-A 期刊）

下一步

- [ ] 等待 IEEE TDSC peer review（預計 3–6 個月）

- [ ] GitHub repo 補充投稿狀態（Under review at IEEE TDSC）

- [ ] Twitter thread 發布（有投稿紀錄撐腰）

- [ ] Monad hackathon 準備

- [ ] Grant 申請調查

---

## 進度紀錄

### 2026年5月16日（0G APAC Hackathon Track 1 — AIP SafeHarness 提交完成）

Hackathon：0G APAC Hackathon 2026, Track 1 Agentic Infrastructure

項目：AIP SafeHarness — AIP Protocol 的工程實作層（off-chain Python harness + on-chain enforcement on 0G Aristotle Mainnet）

提交日期：2026-05-16

提交內容：

- GitHub：https://github.com/USDHGwang/aip-safeharness

- Demo Video：https://youtu.be/18fUBinzE7M

- AgentExecutor (Mainnet, Chain ID 16661)：0x5715001b3add9724DF93D57E145c2a4330422D0F

- AIPSensoryLayer v2：0xe2073A9bFe630d87C2256357a09AfA918feD41C9

- 兩個合約皆於 chainscan.0g.ai 上 source verified

- Demo AIP tx 0x5c5d50ca... 一筆 atomic tx 內 emit 三個 events (IntentOpened → ExecutionTriggered → IntentClosed)

- 三個 0G Storage snapshots（awaiting_human / submitting_onchain / completed）皆可從 indexer-storage-turbo.0g.ai 獨立取回

- 報名賽道：Grand Prizes + Excellence Awards + Community Awards

Stack delivered：

- Dual-agent loop（Generator + Evaluator）+ HITL checkpoint（state uploaded before review）

- 0G Storage snapshots with verify-after-upload polling

- AIP on-chain enforcement using EIP-1153 transient storage（preCheck → action → postCheck atomic）

關鍵工程教訓（記錄供未來參考）：

1. Multi-source verification 不可省略。Terminal 顯示 success + state.json status 不能單獨當作 milestone 完成判斷，必須交叉驗證 chainscan + indexer GET + filesystem 三方

1. CC / agentic coding 工具的 report 對 filesystem 真實狀態不可信。三次 hallucinate 完成（5/8 storage partial、5/10 wallet bug undetected、5/13 README 未實際寫入）。每個 milestone 都需要 PowerShell 親手驗證

1. 硬編碼 secret 災難級風險。multi_agent_loop.py line 432 hardcoded AIza Gemini key、push 後幾分鐘內被 Google 偵測、強制刪 repo + 重洗 git history + 換 key。push 前必須 grep 所有 secret pattern

1. Storage subprocess silent failure：default try / except「continuing flow」會吞掉關鍵錯誤、需 hard-fail on critical snapshots、tracking per-snapshot success bool

與 AIP 論文線的關聯：

- AIP Protocol（IEEE TDSC 2026/03 投稿、4/03 desk reject、教授接手轉投）= 協議規範層（formal specification）

- AIP SafeHarness（本次 hackathon）= 工程實作層（reference implementation on 0G Mainnet）

- 兩者互補：論文證明設計，Hackathon 證明可運作

下一步：

- [ ] 5/17–5/22：hackathon 結果週（被動監測）

- [ ] 結果出來後：研究所推甄作品集文件（將 AIP SafeHarness 框架為研究專案、不是 hackathon retrospective）

- [ ] AIP 論文 resubmission（教授處理中）

- [ ] Month 2：Monad ecosystem 問題識別

- [ ] CCA-F：原訂 6 月、hackathon 後重新評估

---

### 2025年2月底 ～ 3月初（建立期）

- 從零學 Foundry，幾天內完成環境建置

- 完成 3 個合約：AIPHook、AIPRegistry、AIPBenchmark

- 20 個測試全過（fork mainnet 真實數據，含 4 個壓力測試）

- Gas 節省：TSTORE vs SSTORE 完整生命週期節省 51%（68.9% 開啟階段）

- 完成 12 頁簡報（AIP_簡報_2.pptx）

- 攻擊場景覆蓋：T-01 閃電貸、T-02 授權殘留、T-03 HookData 偽造、T-04 Multi-hop、T-05 跨 tx 污染

### 2026年3月5日

- 找到關鍵文獻：Alqithami (2026) arxiv:2601.04583，3000+ 篇 survey 未提及 EIP-1153 用於 Agent 授權，支撐 C2「首創」claim

- 簡報更新：移除未來展望頁，C2 加入文獻引用

- 20:00 教授報告完成

教授要求四樣東西：

1. 攻擊流程 Word 文件

1. PPT 加入程式碼

1. 偵測執行時間

1. 開發總結

投稿策略確定： 6 成版本投會議，10 成版本投期刊，推甄兩個都能用。

2026-03-13 更新：目標確定為期刊版本（10 成）。

新完成：壓力測試（4個，100筆攻擊）

總測試數量：16 → 20 個，全部通過。

新完成文件： AIP_技術報告.docx（5 個攻擊場景、19 個專有名詞、壓力測試數據、開發總結）

今天學會的東西：

- AIP 完整流程：Agent 發出意圖 → Registry + TWAP preCheck → hookData 存 TSTORE → 交易執行 → Hash 比對 + Zero-Allowance postCheck → Intent 關閉

- TSTORE 比 SSTORE 省 68.9% gas，授權物理上不可能殘留

- GoPlus 鏈下分析只要 2,100 gas（vs 鏈上 bytecode 分析 20,000+ gas）

還沒解決： 教授「換個場域」的學術貢獻質疑，AIP 的答案是「定義了一個新的問題」，但尚未與教授討論出結論。

---

## 待辦（報告後根據教授反饋決定）

- [x] 真實閃電貸攻擊者合約（FlashLoanAttacker，Aave 真實借貸）— 合約完成，測試待網路穩定後跑通

- [x] Fuzz Testing（forge fuzz）

- [x] Slippage Sentry（TSTORE 預存最小產出量）— 完成，SlippageSentryTest 3 項全過

- [x] GitHub repo 建立 → https://github.com/USDHGwang/aip-protocol

- [x] GoPlus 同步腳本

- [x] 形式化定義「Agent Intent Integrity」安全屬性

- [x] PPT 加入程式碼（教授要求）

- [x] 偵測執行時間量測（教授要求）

---

### 2026年3月31日

- AIP 論文已確認投稿完成（2026-03-29），進入 peer review 階段

- 開始新專案：AgentForge IDE — 多 Agent 協作可視化平台