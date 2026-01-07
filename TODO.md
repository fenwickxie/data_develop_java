DONE:
1. 仓库骨架：backend（Spring Boot 3）、frontend（已改为 Vue 2/CLI scaffold）、offline_tool（Python CLI）、infra（docker-compose 双 Postgres）。
2. 后端：Maven 项目、Application、HealthController，Raw/Metrics 双数据源配置、实体/仓库/服务/控制器；Flyway 脚本分别落在 raw/metrics；application.yml 已分 datasource。
3. 前端：Vue 2 + Vue Router 3 + Vuex 3 + Element UI 基础脚手架，健康检查与 dataset 列表示例接入。
4. 前端：导航增加 Metrics/Reports，指标与报表列表视图和 API 查询/创建已接通。
5. 离线工具：Typer CLI 骨架（download/compute/upload），requirements & config 示例。
6. 基础设施：docker-compose.yml 已含双 Postgres 环境变量（API 服务占位，MinIO 注释）。
7. 后端安全：OCI SDK 集成（预授权请求）、审计日志过滤器（记录敏感操作）、JWT 鉴权与 USER 角色强制。
8. 前端完整流程：Vuex 状态管理（用户/token/数据集/文件/指标/报表）、登出功能、文件上传带进度与签名 URL、文件下载直接触发、报表对象访问。
9. 离线工具增强：candecode BLF/ASC 完整解码与 parquet 输出、图表生成（matplotlib）、报表生成（Word/python-docx）。
10. 测试与配置：后端双数据源与安全集成测试、test profile、docker-compose 环境变量模板（.env.example）、local profile 支持。
11. 离线工具桌面 GUI：基于 PySide6 实现，5 个功能标签页（下载/计算/上传/图表/报表），集成所有 CLI 功能。

TODO（当前缺口）:
无主要功能缺口。可选增强：
- 前端 e2e 测试（Cypress/Playwright）与单元测试（Jest）。
- Liquibase 作为 Flyway 备选迁移方案（可选）。
- 性能优化：缓存、分页、索引、连接池调优。
- 可观测性：集成 Prometheus/Grafana、OpenTelemetry 追踪。