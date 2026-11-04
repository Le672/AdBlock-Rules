# Loon AdBlock Rules

适用于 iOS Loon 的广告与跟踪规则聚合。订阅文件仅输出 Loon 可用的域名、关键词和 IP 规则，全部动作在 Loon 订阅处指定为 `REJECT`。

## 导入 Loon

将以下远程规则添加到配置，或在远程规则页面添加同一订阅 URL 并选择 `REJECT`：

```ini
https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock.list, policy=REJECT, tag=Le672 广告拦截, enabled=true
```

[规则直链](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock.list)

## 自动更新

GitHub Actions 每 12 小时运行一次（UTC 00:17、12:17；新加坡时间 08:17、20:17），也可在 **Actions → Update Loon ad rules → Run workflow** 手动运行。主要源不可用或构建结果异常时，工作流会失败并保留上一次生成的规则；历史索引中的可选源若暂时不可用会跳过，并在规则文件头部注明。

## 已接入的来源

- [Blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)：Advertising_Domain 域名表
- [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts)：Loon `rejectAd.list`
- [217heidai/adblockfilters](https://github.com/217heidai/adblockfilters)：项目专用 Loon 规则 14
- [anti-AD](https://anti-ad.net/)：Surge 格式规则
- [Lynricsy/HyperADRules](https://github.com/Lynricsy/HyperADRules)：Surge 广告规则集
- [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever)：仅去广告规则
- [nthack/Shadowrocket-ADBlock-Rules-Easy](https://github.com/nthack/Shadowrocket-ADBlock-Rules-Easy)：只抽取动作明确为 REJECT 的规则
- [REIJI007/Adblock-Rule-Collection](https://github.com/REIJI007/Adblock-Rule-Collection)：仅抽取可严格转为域名规则的条目
- B 站 [《AdGuard 规则整理》](https://www.bilibili.com/opus/694495747932946457) 所列网络规则源：EasyList、EasyList China、EasyPrivacy、乘风、Adbyby、CJX Annoyance、ADgk

## 转换范围

格式转换采取保守方式：接受 Loon/Surge 文本中的 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR`、`IP-CIDR6`；从 Adblock 语法只提取无额外修饰符的 `||domain^` 网络规则；从 hosts 只提取标准黑洞地址域名。白名单、网页元素隐藏、脚本/响应体改写、视频规则和含歧义的修饰符不会转换。Shadowrocket 混合规则只取明确的 `REJECT` 项，避免把代理或直连规则误变成拦截。

因此本订阅拦截网络请求，不会隐藏页面中已经加载的元素，也不能保证去除所有 App 内广告。覆盖范围扩大可能造成误拦截或影响 App 登录、推送和内容加载；出现问题时可停用本订阅或添加更优先的放行规则。

## 归属与许可

所有上游规则的归属及其原有许可由各维护者保留。聚合文件头部记录每个成功接入的来源和本轮转换条数；REIJI007 项目列有 GPL-3.0 与 CC BY-NC-SA 4.0 许可，请使用者查看其项目说明及规则内容上的许可条件。此仓库不声称拥有上游规则，也不移除来源标记。
