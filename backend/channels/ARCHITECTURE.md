# Channels 模块

## 当前实现

- FeishuAdapter.verify(event) 恒真返回。
- WeComAdapter.verify(event) 恒真返回。
- 两个 handle(event) 均原样返回输入。
- 当前 API 没有调用这些适配器。

这些方法是占位接口，不构成飞书或企业微信接入，也不能作为验签通过证据。

## 目标边界

渠道适配器负责官方协议的签名、时间窗、防重放和统一消息转换，再交给 API 与 Agent。
渠道层不得直接访问业务数据库；校验失败默认拒绝。
