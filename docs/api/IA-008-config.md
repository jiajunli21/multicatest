# IA-008: 运营配置读取接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `GET` |
| 路径 | `/api/v1/morning-report/config/etf-list` |
| 处理方式 | 复用/新增 |
| 权限 | [default] 内部接口 |
| Mock | 是 [mock] |

## 请求参数

无请求参数。

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `etf_list` | array | ETF 样本配置列表 | [mock] |
| `etf_list[].code` | string | ETF 代码 | [mock] |
| `etf_list[].name` | string | ETF 名称 | [mock] |

### 权限兜底

[default] 内部接口，不对外暴露。

### 空数据规则

无配置时：
- `etf_list` 返回空数组 `[]`

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 配置加载失败 | 500 | `CONFIG_ERROR` | — |

## 示例请求

```bash
curl -X GET "https://api.example.com/api/v1/morning-report/config/etf-list"
```

## 示例响应

### 正常响应

```json
{
  "etf_list": [
    { "code": "510050", "name": "[mock] 上证50ETF" },
    { "code": "510300", "name": "[mock] 沪深300ETF" },
    { "code": "159915", "name": "[mock] 创业板ETF" },
    { "code": "588000", "name": "[mock] 科创50ETF" },
    { "code": "512880", "name": "[mock] 证券ETF" },
    { "code": "512100", "name": "[mock] 中证1000ETF" },
    { "code": "512690", "name": "[mock] 酒ETF" },
    { "code": "512010", "name": "[mock] 医药ETF" },
    { "code": "159949", "name": "[mock] 创业板50ETF" },
    { "code": "512170", "name": "[mock] 医疗ETF" }
  ],
  "_count": 10,
  "_note": "全部字段 [mock]；Phase 2 桥接运营配置"
}
```

### 空配置响应

```json
{
  "etf_list": []
}
```

## 兼容性说明

- 新增接口，复用了运营配置读取模式
- Phase 2 从运营平台读取真实配置，字段结构不变
- 为评分计算提供 ETF 样本范围
