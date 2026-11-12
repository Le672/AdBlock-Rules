# Multi-platform AdBlock Rules

适用于 iOS Loon 的广告与跟踪规则聚合。订阅文件仅输出 Loon 可用的域名、关键词和 IP 规则，全部动作在 Loon 订阅处指定为 `REJECT`。

## 导入 Loon

将以下远程规则添加到配置，或在远程规则页面添加同一订阅 URL 并选择 `REJECT`：

```ini
https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock.list, policy=REJECT, tag=Le672 广告拦截, enabled=true
```

核心版（建议先导入，体积较小）：[AdBlock.list](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock.list)

扩展版（合并全部可用来源，规则更多、文件较大；与核心版二选一，避免重复）：[AdBlock-Extended.list](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock-Extended.list)

## 多平台订阅

每个平台提供核心版与扩展版，二选一即可。所有输出与 Loon 订阅一起每 12 小时更新。各客户端也需启用订阅自动更新；GitHub 定时任务可能延迟。

| 软件 / 平台 | 核心版 | 扩展版 | 导入方式 |
| --- | --- | --- | --- |
| AdGuard / AdGuard Home / uBlock Origin | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.adguard.txt) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.adguard.txt) | 自定义过滤器；域名后缀拦截，不包含网页元素隐藏 |
| Surge / Shadowrocket | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.surge.list) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.surge.list) | 远程规则集，选择 REJECT |
| Clash / Mihomo | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.clash.yaml) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.clash.yaml) | rule-provider，behavior: classical |
| Quantumult X | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.quantumultx.list) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.quantumultx.list) | filter_remote，文件自带 REJECT |
| sing-box | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.sing-box.json) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.sing-box.json) | remote rule_set，format: source |
| hosts / AdAway | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.hosts.txt) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.hosts.txt) | hosts 黑名单；仅匹配列出的主机名 |
| 域名列表 / Pi-hole | [核心版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.domains.txt) | [扩展版](https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock-extended.domains.txt) | 按域名列表导入；仅匹配列出的主机名 |

AdGuard：在“过滤器 / 自定义过滤器”中添加上述链接。AdGuard Home：在“过滤器 → DNS 黑名单”中添加链接。uBlock Origin：在“设置 → 过滤器列表 → 导入”粘贴链接。此处是域名网络拦截订阅，可与软件内置的网页元素过滤规则一起使用。AdGuard 版本只输出 `DOMAIN-SUFFIX`，不扩大精确域名规则的匹配范围，不转换关键词和 IP 规则。

Clash / Mihomo 配置示例（合并进现有配置，将 RULE-SET 放在最终兜底规则之前）：

```yaml
rule-providers:
  le672-adblock:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.clash.yaml
    path: ./ruleset/le672-adblock.yaml
    interval: 43200
rules:
  - RULE-SET,le672-adblock,REJECT
```

Quantumult X 的 `[filter_remote]` 示例：

```ini
https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.quantumultx.list, tag=Le672 广告拦截, force-policy=reject, update-interval=43200, enabled=true
```

sing-box 的 `route.rule_set` 条目：

```json
{
  "type": "remote",
  "tag": "le672-adblock",
  "format": "source",
  "url": "https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/rules/adblock.sing-box.json",
  "update_interval": "12h"
}
```

在 `route.rules` 中添加 `{"rule_set":["le672-adblock"],"action":"reject"}`（适用于支持 action 路由语法的 sing-box 版本）。源文件使用多个独立规则对象实现域名、关键词和 IP 的 OR 匹配。规则集本身不包含代理节点或完整客户端配置。

hosts 和纯域名格式保留域名项，但不支持任意子域名、关键词和网段匹配，因此覆盖范围小于代理软件规则。扩展版体积较大，移动设备建议先用核心版。

格式依据：[AdGuard 官方语法](https://adguard-dns.io/kb/general/dns-filtering-syntax/)、[Mihomo rule-provider](https://wiki.metacubex.one/en/config/rule-providers/)、[Quantumult X 示例](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)、[sing-box source format](https://sing-box.sagernet.org/configuration/rule-set/source-format/)。

## 自动更新

GitHub Actions 每 12 小时运行一次（UTC 00:17、12:17；新加坡时间 08:17、20:17），也可在 **Actions → Update Loon ad rules → Run workflow** 手动运行；主分支内容更新时也会自动重建。两份订阅使用同一批成功获取的来源分别生成。主要源不可用或构建结果异常时，工作流会失败并保留上一次生成的规则；历史索引中的可选源若暂时不可用会跳过，并在规则文件头部注明。

## 已接入的来源

- [Blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)：Advertising_Domain 域名表
- [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts)：Loon `rejectAd.list`
- [217heidai/adblockfilters](https://github.com/217heidai/adblockfilters)：项目专用 Loon 规则 14
- [anti-AD](https://anti-ad.net/)：Surge 格式规则
- [Lynricsy/HyperADRules](https://github.com/Lynricsy/HyperADRules)：Surge 广告规则集
- [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever)：仅去广告规则
- [nthack/Shadowrocket-ADBlock-Rules-Easy](https://github.com/nthack/Shadowrocket-ADBlock-Rules-Easy)：只抽取动作明确为 REJECT 的规则
- [REIJI007/Adblock-Rule-Collection](https://github.com/REIJI007/Adblock-Rule-Collection)：使用其 Lite 订阅，仅抽取可严格转为域名规则的条目
- B 站 [《AdGuard 规则整理》](https://www.bilibili.com/opus/694495747932946457) 所列网络规则源：EasyList、EasyList China、EasyPrivacy、乘风、Adbyby、CJX Annoyance、ADgk

## 转换范围

格式转换采取保守方式：接受 Loon/Surge 文本中的 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR`、`IP-CIDR6`；从 Adblock 语法只提取无额外修饰符的 `||domain^` 网络规则；从 hosts 只提取标准黑洞地址域名。白名单、网页元素隐藏、脚本/响应体改写、视频规则和含歧义的修饰符不会转换。Shadowrocket 混合规则只取明确的 `REJECT` 项，避免把代理或直连规则误变成拦截。

因此本订阅拦截网络请求，不会隐藏页面中已经加载的元素，也不能保证去除所有 App 内广告。覆盖范围扩大可能造成误拦截或影响 App 登录、推送和内容加载；出现问题时可停用本订阅或添加更优先的放行规则。

## 归属与许可

所有上游规则的归属及其原有许可由各维护者保留。聚合文件头部记录每个成功接入的来源和本轮转换条数；REIJI007 项目列有 GPL-3.0 与 CC BY-NC-SA 4.0 许可，请使用者查看其项目说明及规则内容上的许可条件。此仓库不声称拥有上游规则，也不移除来源标记。
