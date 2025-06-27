# 开发范式与最佳实践总结

## 一、项目结构与文件组织

### 1. 推荐的项目结构
- **小型项目**：按类型组织（components、pages、utils）
- **大型项目**：按功能/模块组织（如 `/src/modules/user/components`）

```
src/
  ├── modules/         # 按功能模块划分
  │   ├── user/        # 用户模块
  │   │   ├── components/  # 模块内组件
  │   │   ├── services/    # 模块服务
  │   │   └── index.js     # 模块入口
  ├── components/      # 通用组件
  ├── utils/           # 工具函数
  ├── hooks/           # 自定义Hooks
  ├── App.js           # 应用入口
  └── index.js         # 根入口
```

### 2. 文件与命名规范
- 组件文件：PascalCase（如 `UserProfile.js`）
- 工具函数：camelCase（如 `formatDate.js`）
- 自定义Hooks：以`use`开头（如 `useUserData.js`）
- Redux项目推荐使用Ducks模式（actions、reducers整合在同一文件）

## 二、组件设计与开发

### 1. 组件开发原则
- **优先使用函数组件** + Hooks，避免类组件
- **单一职责原则**：一个组件只做一件事
- **避免冗余代码**：遵循DRY原则
- **拆分复杂组件**：将多功能组件拆分为更小的专注组件

### 2. 组件结构规范
```jsx
import React, { useState, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import './ComponentName.css';

const ComponentName = React.memo(({ prop1, prop2, onAction }) => {
  // 1. Hooks
  const [state, setState] = useState(initialState);
  
  // 2. 计算属性
  const computedValue = useMemo(() => {
    return expensiveCalculation(prop1, prop2);
  }, [prop1, prop2]);
  
  // 3. 事件处理
  const handleClick = useCallback(() => {
    onAction(computedValue);
  }, [onAction, computedValue]);
  
  // 4. 渲染
  return (
    <div className="component-name">
      {/* JSX内容 */}
    </div>
  );
});

// 5. PropTypes
ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
  onAction: PropTypes.func.isRequired
};

ComponentName.defaultProps = {
  prop2: 0
};

export default ComponentName;
```

## 三、状态管理与Hooks使用

### 1. 状态管理最佳实践
- **优先使用受控组件**：状态完全由props驱动
- **复杂状态使用useReducer**：替代多个useState
- **Context API**：用于跨组件状态共享
- **setState函数式更新**：确保获取最新状态

```jsx
// Context API示例
const MaoOCRContext = createContext();

export const MaoOCRProvider = ({ children }) => {
  const [ocrResults, setOcrResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const value = {
    ocrResults,
    setOcrResults,
    isProcessing,
    setIsProcessing
  };
  
  return (
    <MaoOCRContext.Provider value={value}>
      {children}
    </MaoOCRContext.Provider>
  );
};
```

### 2. Hooks使用规范
- **避免在循环、条件中使用Hooks**
- **useEffect依赖数组**：明确指定依赖，避免无依赖空数组
- **useCallback/useMemo优化**：缓存函数和计算结果
- **自定义Hooks**：抽离复用逻辑，命名以`use`开头

## 四、性能优化策略

### 1. 组件优化
- **React.memo**：包裹函数组件，避免不必要重渲染
- **useCallback**：缓存事件处理函数
- **useMemo**：缓存计算结果
- **错误边界**：捕获组件错误，防止应用崩溃

### 2. 列表优化
- **使用唯一key**：避免使用索引作为key
- **虚拟滚动**：处理大量数据列表

```jsx
// 虚拟滚动示例
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={50}
    >
      {Row}
    </List>
  );
};
```

## 五、测试策略

### 1. 测试类型
- **单元测试**：测试单个组件或函数
- **集成测试**：测试组件间交互
- **快照测试**：验证组件渲染输出

### 2. 测试覆盖率要求
- 单元测试覆盖率：≥ 80%
- 集成测试覆盖率：≥ 60%
- 关键路径覆盖率：100%

### 3. 测试示例
```jsx
// 组件单元测试
import { render, screen, fireEvent } from '@testing-library/react';
import FileUploadWidget from '../FileUploadWidget';

test('文件上传组件正常渲染', () => {
  render(<FileUploadWidget />);
  expect(screen.getByText('选择文件')).toBeInTheDocument();
});
```

## 六、工程化与工具链

### 1. 代码质量工具
- **ESLint + Prettier**：代码规范和格式化
- **Husky**：Git hooks，防止错误提交
- **PropTypes**：组件props类型校验

### 2. CI/CD流程
- 自动化测试：提交前运行测试
- 代码审查：至少1名团队成员审查
- 持续部署：合并到主分支自动部署

### 3. 常用命令
```bash
# 启动开发服务器
npm start

# 运行测试
npm test

# 代码检查
npm run lint

# 构建生产版本
npm run build
```

## 七、团队协作规范

### 1. Git工作流
- **分支策略**：main(主分支)、develop(开发分支)、feature/bugfix/hotfix分支
- **提交规范**：`<type>(<scope>): <subject>`
  - feat: 新功能
  - fix: 修复bug
  - docs: 文档更新
  - refactor: 重构

### 2. 代码审查清单
- [ ] 代码符合项目规范
- [ ] 添加了必要的PropTypes
- [ ] 使用了性能优化
- [ ] 添加了单元测试
- [ ] 组件职责单一

## 八、安全与资源管理

### 1. 资源管理
- 使用with语句管理文件操作
- 实现__enter__和__exit__方法
- 定期检查资源使用情况

### 2. 安全最佳实践
- 输入验证和清理
- 敏感信息处理
- 遵循最小权限原则

## 九、项目特定优化

- **OCR结果缓存机制**
- **文件上传进度优化**
- **实时通信错误处理**
- **响应式设计适配**

## 十、后端架构与设计模式实战经验

### 1. 架构设计决策
- **适配器模式**：统一不同OCR引擎接口，便于扩展和切换，建议配合工厂模式管理实例。
- **装饰器模式**：横切关注点如性能监控、缓存、错误处理，建议性能监控在最外层，缓存需考虑内存与过期策略。
- **策略模式**：智能选择不同处理策略，需缓存选择结果并处理失败情况。
- **动态资源监控**：实时监控CPU/GPU/内存/磁盘，需有缓存机制避免频繁查询，兼容多平台，定期清理监控数据。
- **多因子模型选择算法**：综合准确率、速度、资源效率等，权重需根据实际场景调整。

### 2. 系统集成与配置管理
- 配置分层管理，支持环境变量，便于维护和多环境部署。
- 错误处理分层，统一日志与异常返回，便于定位和恢复。
- 动态加载与卸载模型，释放不常用模型，提升内存利用率。
- 支持多种API风格（RESTful、WebSocket、gRPC），设计需兼容未来扩展。

### 3. 性能优化与资源管理
- LRU缓存减少重复计算，内存监控设置告警阈值。
- 并发处理：I/O密集用异步，CPU密集用多进程，线程池管理并发请求。
- 性能基准测试与压力测试，持续优化系统瓶颈。
- 资源管理规范，依赖管理标准化，环境配置标准化，监控与告警机制完善。

### 4. 工程化与CI/CD
- Dockerfile修改需稳定优先、文档齐全、回溯兼容，变更需团队审批。
- 版本控制规范，主版本/次版本/补丁号分明。
- CI/CD流程：本地构建、自动化测试、功能验证、安全检查、文档同步。
- 环境变量与依赖版本需明确记录，遵循最小权限原则。

### 5. 团队协作与知识沉淀
- 关键技术决策与经验教训及时记录，定期总结最佳实践。
- 代码审查与文档完善，持续提升团队协作效率。
- 版本管理与变更记录规范，便于追溯和回滚。

### 6. 典型实战经验举例
- **适配器+工厂模式**统一多引擎OCR，后续扩展只需实现新适配器。
- **装饰器链**实现性能监控+缓存+错误处理，提升系统健壮性。
- **分层配置+环境变量**支持本地/测试/生产多环境无缝切换。
- **LRU缓存+动态卸载**大幅降低内存占用，提升响应速度。
- **CI/CD自动化**保障每次变更都经过测试和安全校验。