# macOS Security: Gatekeeper & Quarantine

本文件記錄 macOS 安全機制研究結果，說明為何此 skill 的 binary 分發不會被 Gatekeeper 阻擋。

## 概述

### com.apple.quarantine 屬性

macOS 使用 `com.apple.quarantine` 擴展屬性標記「來自可疑來源」的檔案，主要是從網路下載的檔案。當使用者首次執行帶有此屬性的應用程式時，Gatekeeper 會檢查其簽名和公證狀態。

### Gatekeeper 檢查機制

```
┌─────────────────────────────────────────────────────────────┐
│  使用者執行應用程式                                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  檢查 com.apple.quarantine 屬性                              │
├─────────────────────────────────────────────────────────────┤
│  有 quarantine        │  無 quarantine                      │
│       │               │       │                             │
│       ▼               │       ▼                             │
│  Gatekeeper 檢查      │  直接執行（跳過檢查）                  │
│  - 簽名驗證           │                                      │
│  - 公證確認           │                                      │
│  - 惡意軟體掃描       │                                      │
└─────────────────────────────────────────────────────────────┘
```

## 下載方式與 Quarantine

### 會添加 quarantine 的方式

| 應用程式 | LSFileQuarantineEnabled | 說明 |
|----------|-------------------------|------|
| Safari | ✅ Yes | 瀏覽器下載 |
| Chrome | ✅ Yes | 瀏覽器下載 |
| Mail.app | ✅ Yes | 郵件附件 |
| Messages | ✅ Yes | 訊息附件 |

### 不會添加 quarantine 的方式

| 工具 | 說明 |
|------|------|
| curl | 命令列下載工具 |
| wget | 命令列下載工具 |
| git | 版本控制（包含 git clone） |
| scp/sftp | 遠端檔案傳輸 |
| npm | Node.js 套件管理 |
| pip | Python 套件管理 |
| brew | Homebrew 套件管理 |

### 技術原理

quarantine 機制是 **opt-in**：應用程式必須在 Info.plist 中設定 `LSFileQuarantineEnabled = YES` 才會為下載的檔案添加 quarantine 屬性。

命令列工具（如 curl、wget、git）不是 macOS 應用程式 bundle，沒有這個設定，因此不會添加 quarantine。

> "Most Unix-y tools don't quarantine their downloads, including curl and scp"
> — Apple Developer Forums

## 解壓縮方式與 Quarantine 繼承

當解壓縮帶有 quarantine 的壓縮檔時，解壓出的檔案是否繼承 quarantine 取決於解壓工具：

| 解壓方式 | 繼承 quarantine | 說明 |
|----------|-----------------|------|
| Archive Utility (雙擊 Finder) | ✅ 繼承 | macOS 內建，會傳遞屬性 |
| `unzip` 命令 | ❌ 不繼承 | Unix 工具，不處理 xattr |
| `tar` 命令 | ❌ 不繼承 | Unix 工具，不處理 xattr |
| 第三方軟體 | ⚠️ 視實作而定 | 如 Keka、The Unarchiver |

> "Files unarchived by Unix-based command-line unarchiving tools such as unzip and tar won't inherit the quarantine extended attribute."
> — Palo Alto Unit42

## 完整情境分析

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        下載 + 解壓縮情境                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  情境 1: Safari 下載 → Archive Utility 解壓                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Safari   │ →  │ .zip     │ →  │ 雙擊解壓  │ →  │ 檔案     │          │
│  │ 下載     │    │ 有 quar. │    │          │    │ 有 quar. │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│  結果: ⚠️ Gatekeeper 會檢查                                             │
│                                                                         │
│  情境 2: Safari 下載 → unzip 命令解壓                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Safari   │ →  │ .zip     │ →  │ unzip    │ →  │ 檔案     │          │
│  │ 下載     │    │ 有 quar. │    │ 命令     │    │ 無 quar. │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│  結果: ✅ Gatekeeper 不會檢查（即使原 zip 有 quarantine）                 │
│                                                                         │
│  情境 3: curl 下載 → 任何方式解壓                                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ curl     │ →  │ .zip     │ →  │ 任何方式  │ →  │ 檔案     │          │
│  │ 下載     │    │ 無 quar. │    │          │    │ 無 quar. │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│  結果: ✅ Gatekeeper 不會檢查                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 此 Skill 的安裝流程

```
┌────────────────────────────────────────────────────────────┐
│  youtube-audio-transcribe skill 安裝流程                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  git clone (或 Claude Code plugin 安裝)                   │
│       │                                                    │
│       ▼  ← 無 quarantine（git 不會添加）                   │
│                                                            │
│  執行 _download_ffmpeg.sh                                  │
│       │                                                    │
│       ▼                                                    │
│  curl 下載 ffmpeg.zip  ← 無 quarantine（curl 不會添加）     │
│       │                                                    │
│       ▼                                                    │
│  unzip 解壓縮          ← 不繼承（即使有也不會繼承）          │
│       │                                                    │
│       ▼                                                    │
│  bin/ffmpeg            ← 無 quarantine ✅                  │
│                                                            │
│  同理：                                                    │
│  - jq: curl 下載 → 無 quarantine ✅                        │
│  - whisper-cli: 本地編譯 → 無 quarantine ✅                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Binary 安全性總結

| Binary | 來源 | 下載方式 | Quarantine | Gatekeeper |
|--------|------|----------|------------|------------|
| ffmpeg | martin-riedl.de | curl + unzip | ❌ 無 | ✅ 不阻擋 |
| jq | GitHub Releases | curl | ❌ 無 | ✅ 不阻擋 |
| whisper-cli | 本地編譯 | N/A | ❌ 無 | ✅ 不阻擋 |

## 額外資訊：Code Signing

雖然 quarantine 繞過讓 Gatekeeper 不會檢查，但 ffmpeg 仍然是已簽名的：

```bash
$ codesign -dv bin/ffmpeg
# TeamID: KU3N25GGLU (Martin Riedl)
```

這提供了額外的信任保證，即使不經過 Gatekeeper 檢查。

## 管理 Quarantine 屬性

### 檢查屬性

```bash
xattr -l /path/to/file
```

### 移除屬性

```bash
xattr -d com.apple.quarantine /path/to/file
# 或遞迴移除
xattr -dr com.apple.quarantine /path/to/app
```

## 參考來源

- [Apple Developer Forums - Avoiding notarisation & Gatekeeper](https://developer.apple.com/forums/thread/666452)
- [Apple Community - Apps downloaded via curl bypass Gatekeeper](https://discussions.apple.com/thread/256200611)
- [Palo Alto Unit42 - Gatekeeper Bypass](https://unit42.paloaltonetworks.com/gatekeeper-bypass-macos/)
- [The Eclectic Light Company - Explainer: Quarantine](https://eclecticlight.co/2021/12/11/explainer-quarantine/)
- [Red Canary - Gatekeeping in macOS](https://redcanary.com/blog/threat-detection/gatekeeper/)
- [Der Flounder - Clearing quarantine attribute](https://derflounder.wordpress.com/2012/11/20/clearing-the-quarantine-extended-attribute-from-downloaded-applications/)

---

*最後更新：2026-02-15*
