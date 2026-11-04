# Loon AdBlock Rules

适用于 iOS Loon 的广告与跟踪域名规则合集。规则聚合自长期维护的 Loon 原生规则列表，去重后保留 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR` 和 `IP-CIDR6` 类型，作为一条 `REJECT` 远程规则订阅。

## 导入 Loon

在 Loon 的配置中添加以下远程规则，或在远程规则页面添加同一 URL 并将策略设为 `REJECT`：

```ini
https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock.list, policy=REJECT, tag=Le672 广告拦截, enabled=true
```

规则直链：<https://raw.githubusercontent.com/Le672/Loon-AdBlock-Rules/main/AdBlock.list>

## 更新

GitHub Actions 每 12 小时运行一次（UTC 每日 00:17 和 12:17），也可在仓库的 **Actions → Update Loon ad rules → Run workflow** 手动触发。只有上游均成功且规则数量通过完整性检查后才会提交更新；失败时保留上次可用列表。

## 来源与范围

- [Blackmatrix7/ios_rule_script — Advertising_Domain (Loon-compatible domain list)](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/Advertising)
- [fmz200/wool_scripts — rejectAd](https://github.com/fmz200/wool_scripts/tree/main/Loon/rule)

构建脚本仅提取 Loon 可识别的域名和 IP 匹配规则，不包含网页元素隐藏、JavaScript 注入或其他客户端专属语法。因此它主要拦截网络请求，无法移除已随页面内容加载的广告素材。规则较全也可能导致个别 App 的登录、推送、统计或页面资源异常；可在 Loon 中停用本规则或为对应域名添加更高优先级的放行规则。

上游规则及其版权、许可证和归属仍归各自维护者所有；本仓库保留来源说明，不对上游条目作独立所有权声明。
