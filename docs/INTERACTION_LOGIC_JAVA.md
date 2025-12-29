# 数据集管理系统 - Spring Boot版完整交互逻辑说明

## 目录
1. [技术栈说明](#技术栈说明)
2. [系统架构](#系统架构)
3. [数据流程](#数据流程)
4. [数据库到后端交互](#数据库到后端交互)
5. [后端到前端交互](#后端到前端交互)
6. [完整业务流程](#完整业务流程)
7. [文档说明](#文档说明)

---

## 技术栈说明

### 后端技术栈（Java）

| 技术组件 | 版本 | 作用说明 |
|---------|------|---------|
| **Java** | 17+ | 后端开发语言，长期支持版本 |
| **Spring Boot** | 3.x | 应用框架，整合MVC、安全、数据访问、消息、定时等能力 |
| **Spring MVC** |  | Web层，提供REST API与拦截器体系 |
| **Spring Security** | 6.x | 认证授权，支持JWT/Token，方法级鉴权 |
| **Spring Data JPA** |  | ORM层，简化PostgreSQL数据访问，支持分页与审计 |
| **Spring AMQP / RabbitMQ** |  | 消息队列，分发解析、指标计算、报告生成等异步任务 |
| **Spring Batch** |  | 批处理框架，可用于大批量数据导入与转换 |
| **springdoc-openapi** | 2.x | 自动生成OpenAPI 3.0文档与Swagger UI |
| **PostgreSQL Driver** |  | JDBC驱动，与数据库通信 |
| **Redis (lettuce)** | 6+ | 缓存与分布式锁，可选任务进度存储 |
| **Apache POI** | 5.x | Excel/Word/PPT读写与报告生成 |
| **Jackson / OpenCSV** |  | CSV/JSON解析工具链 |
| **java-can / j1939 等 CAN 库** |  | 解析BLF/ASC等车辆CAN日志，结合DBC信号解码 |
| **JFreeChart / XChart** |  | 服务器侧图表生成（如需要导出PNG/SVG） |

### 前端技术栈

| 技术组件 | 版本 | 作用说明 |
|---------|------|---------|
| **Vue.js** | 3 | 构建SPA界面 |
| **Vue Router** | 4 | 路由管理 |
| **Vuex** | 4 | 全局状态管理（数据集、文件、指标、报告） |
| **Element Plus** |  | UI组件库（表格/表单/对话框） |
| **ECharts** |  | 数据可视化图表 |
| **Axios** |  | HTTP客户端，封装认证与错误处理 |

### 中间件与工具

| 组件 | 作用说明 |
|-----|---------|
| **RabbitMQ** | 任务队列与消息分发 |
| **Nginx** | 反向代理与静态资源分发，HTTPS终结 |
| **Docker / Docker Compose** | 部署编排，隔离服务依赖 |
| **Flyway / Liquibase** | 数据库变更管理，保证DDL一致性 |
| **Lombok / MapStruct** | 代码简化与DTO映射 |

---

## 系统架构

### 整体架构图

```mermaid
graph TB
    subgraph "前端层 - Vue 3"
        A[用户浏览器] --> B[Vue Router<br/>路由管理]
        B --> C[Vue Components<br/>视图组件]
        C --> D[Vuex Store<br/>状态管理]
        D --> E[Axios API<br/>HTTP客户端]
        C --> F[Element Plus<br/>UI组件]
        C --> G[ECharts<br/>数据可视化]
    end

    subgraph "API网关层"
        E --> H[Spring MVC<br/>RESTful API]
        H --> I[Spring Security<br/>JWT/Token]
        H --> J[CORS过滤器]
        H --> K[OpenAPI/Swagger]
    end

    subgraph "业务服务层 - Spring Boot"
        H --> L[Datasets Service<br/>数据集管理]
        H --> M[Files Service<br/>文件处理]
        H --> N[Metrics Service<br/>指标计算]
        H --> O[Reports Service<br/>报告生成]

        L --> P[Spring Data JPA<br/>ORM]
        M --> P
        N --> P
        O --> P

        M --> Q[批处理/异步任务]
        N --> Q
        O --> Q
    end

    subgraph "消息队列层"
        Q --> R[RabbitMQ<br/>任务队列]
        R --> S[Worker - 解析]
        R --> T[Worker - 指标]
        R --> U[Worker - 报告]
    end

    subgraph "数据层"
        P --> V[(PostgreSQL<br/>主数据库)]
        R --> W[(Redis<br/>缓存/锁)]
        S --> X[文件存储<br/>Media Files]
        U --> X

        V --> V1[元数据表]
        V --> V2[数据内容表]
        V --> V3[指标值表]
    end

    style A fill:#e1f5ff
    style V fill:#ffe1e1
    style W fill:#fff4e1
    style X fill:#e1ffe1
```

### 架构层次说明

**1. 前端层 (Vue 3)**
- 路由与导航：Vue Router管理6个主要页面
- 状态管理：Vuex集中管理数据集、文件、指标、报告
- UI与可视化：Element Plus + ECharts
- API通信：Axios统一封装Token、超时与错误

**2. API网关层**
- RESTful API：Spring MVC控制器 + 全局异常处理
- 认证授权：Spring Security + JWT，方法级鉴权
- 跨域：CORS过滤器支持前后端分离
- API文档：springdoc-openapi生成OpenAPI/Swagger UI

**3. 业务服务层**
- Datasets服务：CRUD、统计、质量评估
- Files服务：上传、格式验证、解析调度
- Metrics服务：定义、计算、聚合
- Reports服务：模板、文档生成、图表渲染
- 异步/批处理：Spring AMQP + Worker，或Spring Batch处理大批量导入

**4. 数据层**
- PostgreSQL：存储核心业务表与动态数据表
- Redis：缓存热点数据、分布式锁、可选进度存储
- 文件存储：原始文件、导出报告、图表截图

---

## 数据流程

### 完整数据处理流程

```mermaid
graph LR
    A[用户上传文件] --> B{文件类型检测}

    B -->|Excel/CSV| C[Apache POI/CSV解析]
    B -->|BLF/ASC| D[java-can读取]
    B -->|DBC| E[DBC信号解码]

    C --> F[数据类型推断]
    D --> G[CAN消息解码]
    E --> G

    F --> I[数据清洗/校验]
    G --> I

    I --> J[动态创建表结构]
    J --> K[批量写入PostgreSQL]

    K --> L[元数据记录]
    L --> M[触发指标计算]

    M --> N[统计指标]
    M --> O[质量指标]
    M --> P[性能指标]

    N --> Q[结果存储]
    O --> Q
    P --> Q

    Q --> R[数据质量评估]
    R --> S[生成可视化图表]

    S --> T[Word报告]
    S --> U[PPT报告]
    S --> V[Excel报表]

    T --> W[用户下载]
    U --> W
    V --> W

    style A fill:#e1f5ff
    style K fill:#ffe1e1
    style Q fill:#fff4e1
    style W fill:#e1ffe1
```

### 文件解析详细流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as Spring API
    participant MQ as RabbitMQ
    participant C as Worker
    participant DB as PostgreSQL
    participant R as Redis

    U->>F: 选择并上传文件
    F->>A: POST /api/files (multipart/form-data)

    A->>A: 校验文件类型与大小
    A->>DB: 保存文件记录(status=uploaded)
    A->>MQ: 发送解析任务
    A->>F: 返回fileId
    F->>U: 显示上传成功

    MQ->>C: Worker接收任务
    C->>C: 读取文件内容

    alt CAN文件 (BLF/ASC)
        C->>C: 使用java-can读取
        C->>C: 使用DBC解码信号
        C->>C: 时间戳对齐
    else Excel文件
        C->>C: 使用Apache POI读取
        C->>C: 数据类型推断
    end

    C->>DB: 更新状态(parsing)
    C->>DB: 创建动态数据表
    C->>DB: 批量插入数据
    C->>DB: 创建ParsedData记录
    C->>DB: 更新状态(parsed)

    F->>A: 轮询文件状态
    A->>DB: 查询文件记录
    DB->>A: 返回状态
    A->>F: 返回解析结果
    F->>U: 显示解析完成
```

---

## 数据库到后端交互

### ORM映射机制（Spring Data JPA）

```mermaid
graph LR
    A[实体对象] -->|JPA映射| B[SQL语句]
    B -->|JDBC驱动| C[(PostgreSQL)]
    C -->|结果集| D[ResultSet]
    D -->|JPA转换| A

    style A fill:#e1f5ff
    style C fill:#ffe1e1
```

### 数据库操作流程

#### 1. 查询流程

```mermaid
sequenceDiagram
    participant V as REST Controller
    participant R as Repository
    participant P as Persistence Context
    participant D as PostgreSQL

    V->>R: datasetRepository.findByStatus("COMPLETED")
    R->>P: 生成JPQL/SQL
    P->>D: 执行查询
    D->>P: 返回结果集
    P->>R: 转换为实体/投影
    R->>V: 返回Page<List<Dataset>>
```

**要点：**
1. 方法名派生查询或`@Query`自定义查询
2. JPA转换结果为实体/DTO
3. 支持`Pageable`分页、`Specification`动态条件

#### 2. 创建流程

```mermaid
sequenceDiagram
    participant V as REST Controller
    participant R as Repository
    participant D as PostgreSQL

    V->>R: save(new Dataset(...))
    R->>R: 验证与转换
    R->>D: INSERT INTO datasets ...
    D->>R: 返回ID
    R->>V: 返回实体(含ID)
```

**要点：** 事务由`@Transactional`管理，失败自动回滚。

#### 3. 更新流程

```mermaid
sequenceDiagram
    participant V as REST Controller
    participant P as Persistence Context
    participant D as PostgreSQL

    V->>P: dataset.setStatus(COMPLETED)
    P->>D: 自动生成UPDATE语句
    D->>P: 返回影响行数
    P->>V: 返回结果
```

**要点：**
- 脏检查：持久化上下文检测变更字段，按需更新
- 事件：可通过`ApplicationEvent`或`Domain Event`触发后置处理

### 复杂查询优化

```mermaid
graph TB
    A[查询数据集] --> B{是否关联?}
    B -->|是| C[fetch join / entity graph]
    B -->|是| D[批量抓取 batch-size]
    B -->|否| E[普通查询]
    C --> F[减少N+1]
    D --> F
    E --> F
```

**优化策略：**
- `@EntityGraph`或`JOIN FETCH`避免N+1
- `@BatchSize`或`hibernate.default_batch_fetch_size`批量抓取
- `Pageable`分页与`Slice`流式查询
- 只选必要字段：DTO投影或`@Query`选择列

### 连接池与事务

```mermaid
graph LR
    A[HTTP请求] --> B{HikariCP连接池}
    B -->|获取连接| C[执行SQL]
    C --> D[归还连接]
    D --> B
```

**配置要点：**
- `maximumPoolSize`、`connectionTimeout`、`idleTimeout`合理设置
- `spring.jpa.open-in-view=false`避免视图层懒加载问题
- 事务边界由Service层`@Transactional`控制

---

## 后端到前端交互

### RESTful API设计规范

```mermaid
graph LR
    A[HTTP方法] --> B[GET 查询]
    A --> C[POST 创建]
    A --> D[PATCH 部分更新]
    A --> E[PUT 完整更新]
    A --> F[DELETE 删除]

    B --> G["api/datasets/<br/> 列表"]
    B --> H["api/datasets/{id}/<br/> 详情"]
    C --> I["api/datasets/<br/> 创建"]
    D --> J["api/datasets/{id}/<br/> 更新"]
    F --> K["api/datasets/{id}/<br/> 删除"]
```

**端点命名：**
- 集合：`/api/datasets/`
- 单体：`/api/datasets/{id}/`
- 自定义动作：`/api/datasets/{id}/quality/`
- 嵌套：`/api/datasets/{id}/files/`

### HTTP请求-响应流程

```mermaid
sequenceDiagram
    participant B as 浏览器
    participant V as Vue前端
    participant A as Axios
    participant N as Nginx
    participant S as Spring Boot
    participant DB as PostgreSQL

    B->>V: 用户操作
    V->>A: 调用API方法
    A->>A: 添加JWT到Authorization
    A->>N: GET /api/datasets/

    N->>S: 反向代理
    S->>S: CORS过滤 + 认证 + 路由匹配
    S->>S: 控制器 -> Service -> Repository
    S->>DB: ORM查询
    DB->>S: 返回数据
    S->>S: DTO/JSON序列化

    S->>N: 200 OK + JSON
    N->>A: 返回数据
    A->>V: Promise resolve
    V->>V: Vuex commit
    V->>B: 更新DOM
```

### 序列化与反序列化

```mermaid
graph TB
    subgraph "后端→前端"
        A[实体/DTO] --> B[Jackson序列化]
        B --> C[JSON字符串]
        C --> D[HTTP响应]
    end
    subgraph "前端→后端"
        E[HTTP请求Body] --> F[JSON字符串]
        F --> G[Jackson反序列化]
        G --> H[DTO/命令对象]
        H --> I[校验 @Valid]
        I -->|通过| J[业务处理]
        I -->|失败| K[错误响应]
    end

    style D fill:#e1f5ff
    style J fill:#e1ffe1
    style K fill:#ffe1e1
```

### 前端状态管理流程

```mermaid
graph TD
    A[Vue组件] -->|dispatch| B[Vuex Action]
    B -->|Axios调用| C[Spring API]
    C -->|JSON| B
    B -->|commit| D[Vuex Mutation]
    D --> E[Vuex State]
    E -->|响应式| A
    F[其他组件] -.->|computed| E
```

### Axios拦截器

```mermaid
graph LR
    A[发起请求] --> B[请求拦截]
    B --> C{有Token?}
    C -->|是| D[加Authorization头]
    C -->|否| E[跳转登录]
    D --> F[发送HTTP]

    F --> G[响应拦截]
    G --> H{状态码}
    H -->|2xx| I[返回数据]
    H -->|401| J[清Token并跳登录]
    H -->|403| K[提示权限不足]
    H -->|404| L[提示资源不存在]
    H -->|5xx| M[提示系统错误]
```

---

## 完整业务流程

### 业务流程1：文件上传与解析

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as Spring API
    participant MQ as RabbitMQ
    participant C as Worker
    participant DB as PostgreSQL

    U->>F: 选择并上传文件
    F->>A: POST /api/files

    A->>DB: 创建File记录(status=uploaded)
    A->>MQ: 发布解析任务(messageId)
    A->>F: 返回fileId

    MQ->>C: Worker消费任务
    C->>DB: 状态改为parsing
    C->>C: 解析文件(POI/java-can/CSV)
    C->>DB: 创建动态表并批量写入
    C->>DB: 状态改为parsed

    F->>A: 轮询/长轮询状态
    A->>DB: 读取状态与摘要
    A->>F: 返回解析结果
```

### 业务流程2：指标计算与报告生成

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as Spring API
    participant MQ as RabbitMQ
    participant C as Worker
    participant DB as PostgreSQL

    U->>F: 选数据集并点击"计算指标"
    F->>A: POST /api/metrics/calculate

    A->>MQ: 发布计算任务(taskId)
    MQ->>C: Worker拉取任务
    C->>DB: 读取指标定义与解析数据
    C->>C: 统计/质量/性能计算
    C->>DB: 写入指标值

    U->>F: 点击"生成报告"
    F->>A: POST /api/reports
    A->>DB: 创建Report记录
    A->>MQ: 发布报告任务(reportId)
    MQ->>C: Worker生成Word/PPT/Excel
    C->>DB: 更新Report状态与文件路径

    U->>F: 下载报告
    F->>A: GET /api/reports/{id}/download
    A->>DB: 查询路径并返回文件流
    F->>U: 下载完成
```

### 关键技术交互

1. **异步任务**：RabbitMQ + Spring AMQP；可用`RetryTemplate`或死信队列做重试
2. **数据质量**：缺失率、异常值检测（IQR/Z-score）、业务一致性校验，结果入库并可视化
3. **文件类型策略**：
   - BLF/ASC：java-can读取，DBC解码信号
   - XLSX：Apache POI；CSV：OpenCSV/Jackson
   - MDF（可选）：使用`mdfreader`的Java替代方案或JNI扩展
4. **性能优化**：批量写入`JdbcTemplate`/Batch，复制表`CREATE TABLE ... AS`，合理索引与分区
5. **安全**：JWT无状态认证，方法级`@PreAuthorize`，审计日志记录关键操作

---

## 文档说明

本文档以Spring Boot + PostgreSQL + Vue技术栈描述系统的技术栈、架构设计、数据流程与交互逻辑。

### 相关文档
- 技术文档：TECHNICAL_DOCUMENTATION.md（需同步更新为Java版）
- 项目总结：../PROJECT_SUMMARY.md
- README：../README.md

---

*最后更新时间: 2025年12月29日*
