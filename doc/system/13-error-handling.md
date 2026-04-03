## 13. Error Handling Contract

### 13.1 HTTP Status Mapping

| Status | Trigger |
|-------|---------|
| `201` | Successful create |
| `400` | Validation failure in governed service logic |
| `404` | Requested governed version not found |
| `409` | Duplicate or conflicting governed version |
| `422` | FastAPI request-body validation failure |

### 13.2 Error Translation

Route handlers translate governed service exceptions into explicit HTTP failures.
No route silently degrades a missing or incompatible binding into a success path.

