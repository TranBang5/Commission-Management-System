# AI Commission Management System - API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /auth/login
Đăng nhập người dùng

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "user_id",
      "username": "username",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "admin",
      "department": "IT",
      "position": "Manager",
      "preferences": {
        "theme": "light",
        "language": "vi",
        "notifications": {
          "email": true,
          "push": true,
          "sms": false
        }
      }
    },
    "token": "jwt_token_here"
  }
}
```

#### POST /auth/logout
Đăng xuất người dùng

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

#### GET /auth/me
Lấy thông tin người dùng hiện tại

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_id",
      "username": "username",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "admin",
      "department": "IT",
      "position": "Manager",
      "employeeId": "EMP001",
      "phone": "+84123456789",
      "avatar": "avatar_url",
      "preferences": {...},
      "permissions": ["view_dashboard", "manage_users"],
      "lastLogin": "2024-01-01T00:00:00.000Z",
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  }
}
```

### Commissions

#### GET /commissions
Lấy danh sách commission

**Query Parameters:**
- `page`: Số trang (default: 1)
- `limit`: Số lượng per page (default: 10)
- `year`: Năm
- `month`: Tháng
- `status`: Trạng thái (draft, calculated, pending_approval, approved, paid, disputed)
- `employee_id`: ID nhân viên
- `project_id`: ID dự án

**Response:**
```json
{
  "success": true,
  "data": {
    "commissions": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "pages": 10
    }
  }
}
```

#### POST /commissions/calculate
Tính toán commission bằng AI

**Request Body:**
```json
{
  "period": {
    "year": 2024,
    "month": 1
  },
  "project_id": "project_id",
  "employee_id": "employee_id",
  "performance_data": {
    "role": "developer",
    "kpi_score": 85,
    "quality_score": 90,
    "efficiency_score": 88,
    "teamwork_score": 92,
    "innovation_score": 85,
    "project_progress": 95,
    "client_satisfaction": 88,
    "deadline_adherence": 90,
    "base_salary": 20000000,
    "project_profit": 50000000
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {"year": 2024, "month": 1},
    "project_id": "project_id",
    "employee_id": "employee_id",
    "role": "developer",
    "base_salary": 20000000,
    "performance_metrics": {...},
    "ai_calculations": {
      "overall_score": 88.5,
      "performance_level": "good",
      "performance_bonus": 6000000,
      "project_bonus": 1000000,
      "quality_bonus": 2000000,
      "innovation_bonus": 1000000,
      "total_bonus": 10000000,
      "ai_confidence": 92.5,
      "ai_factors": [...]
    },
    "final_amount": 30000000,
    "currency": "VND",
    "calculation_timestamp": "2024-01-01T00:00:00.000Z"
  }
}
```

#### POST /commissions/{id}/approve
Phê duyệt commission

**Request Body:**
```json
{
  "approved": true,
  "notes": "Approved by manager"
}
```

#### POST /commissions/{id}/dispute
Tạo khiếu nại cho commission

**Request Body:**
```json
{
  "reason": "Calculation seems incorrect",
  "evidence": ["evidence1.pdf", "evidence2.pdf"]
}
```

### Projects

#### GET /projects
Lấy danh sách dự án

**Query Parameters:**
- `page`: Số trang
- `limit`: Số lượng per page
- `status`: Trạng thái (planning, active, on-hold, completed, cancelled)
- `manager_id`: ID quản lý dự án
- `category`: Loại dự án (web, mobile, desktop, api, consulting, training, maintenance)

**Response:**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "project_id",
        "name": "E-commerce Platform",
        "code": "ECOM001",
        "description": "Modern e-commerce platform",
        "client": {
          "name": "ABC Company",
          "email": "contact@abc.com",
          "phone": "+84123456789",
          "company": "ABC Corporation"
        },
        "manager": {
          "id": "manager_id",
          "name": "John Doe"
        },
        "team": [...],
        "status": "active",
        "priority": "high",
        "category": "web",
        "startDate": "2024-01-01T00:00:00.000Z",
        "endDate": "2024-06-01T00:00:00.000Z",
        "budget": {
          "planned": 1000000000,
          "actual": 950000000,
          "currency": "VND"
        },
        "revenue": {
          "planned": 1200000000,
          "actual": 1150000000,
          "received": 1000000000,
          "currency": "VND"
        },
        "progress": {
          "planned": 80,
          "actual": 85
        },
        "kpis": [...],
        "milestones": [...],
        "risks": [...],
        "documents": [...],
        "tags": ["e-commerce", "react", "nodejs"],
        "notes": "Project notes",
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z"
      }
    ],
    "pagination": {...}
  }
}
```

#### POST /projects
Tạo dự án mới

**Request Body:**
```json
{
  "name": "New Project",
  "code": "PROJ001",
  "description": "Project description",
  "client": {
    "name": "Client Name",
    "email": "client@example.com",
    "phone": "+84123456789",
    "company": "Client Company"
  },
  "manager": "manager_id",
  "category": "web",
  "startDate": "2024-01-01T00:00:00.000Z",
  "endDate": "2024-06-01T00:00:00.000Z",
  "budget": {
    "planned": 1000000000,
    "currency": "VND"
  },
  "revenue": {
    "planned": 1200000000,
    "currency": "VND"
  },
  "priority": "medium",
  "tags": ["tag1", "tag2"]
}
```

### Users

#### GET /users
Lấy danh sách người dùng (Admin only)

**Query Parameters:**
- `page`: Số trang
- `limit`: Số lượng per page
- `role`: Vai trò (admin, manager, staff, partner)
- `department`: Phòng ban
- `isActive`: Trạng thái hoạt động

#### POST /users
Tạo người dùng mới (Admin only)

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe",
  "role": "staff",
  "department": "IT",
  "position": "Developer",
  "employeeId": "EMP002",
  "phone": "+84123456789",
  "permissions": ["view_dashboard", "view_reports"]
}
```

### AI Engine

#### POST /ai/calculate-reward
Tính toán thưởng bằng AI

**Request Body:**
```json
{
  "period": {"year": 2024, "month": 1},
  "project_id": "project_id",
  "employee_id": "employee_id",
  "performance_data": {
    "role": "developer",
    "kpi_scores": {"task_completion": 85, "quality": 90},
    "project_progress": 95,
    "client_satisfaction": 88,
    "deadline_adherence": 90,
    "quality_score": 90,
    "efficiency_score": 88,
    "teamwork_score": 92,
    "innovation_score": 85,
    "base_salary": 20000000,
    "project_profit": 50000000
  }
}
```

#### POST /ai/process-feedback
Xử lý phản hồi bằng NLP

**Request Body:**
```json
{
  "text": "Employee performed exceptionally well on this project",
  "source": "client",
  "context": {
    "project_id": "project_id",
    "employee_id": "employee_id"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "confidence": 0.95,
    "key_points": ["exceptional performance", "well on project"],
    "satisfaction_score": 9.2,
    "recommendations": ["Consider for promotion", "Increase bonus"],
    "processed_at": "2024-01-01T00:00:00.000Z"
  }
}
```

#### POST /ai/analyze-dispute
Phân tích khiếu nại bằng AI

**Request Body:**
```json
{
  "commission_id": "commission_id",
  "reason": "The calculation seems incorrect based on my performance",
  "evidence": ["performance_report.pdf", "timesheet.xlsx"],
  "employee_id": "employee_id"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": "negative",
    "confidence": 0.87,
    "key_points": ["calculation incorrect", "performance based"],
    "recommendation": "modify",
    "suggested_adjustment": 500000,
    "reasoning": "Employee has valid concerns about calculation",
    "risk_level": "medium",
    "processed_at": "2024-01-01T00:00:00.000Z"
  }
}
```

### Reports

#### GET /reports/dashboard
Lấy dữ liệu dashboard

**Response:**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_commissions": 150,
      "total_amount": 4500000000,
      "pending_approvals": 12,
      "active_disputes": 3
    },
    "charts": {
      "monthly_commissions": [...],
      "performance_distribution": [...],
      "project_progress": [...]
    },
    "recent_activities": [...],
    "top_performers": [...]
  }
}
```

#### GET /reports/commission
Báo cáo commission

**Query Parameters:**
- `year`: Năm
- `month`: Tháng
- `format`: Định dạng (json, pdf, excel)

#### GET /reports/project
Báo cáo dự án

**Query Parameters:**
- `project_id`: ID dự án
- `format`: Định dạng

### Health Check

#### GET /health
Kiểm tra sức khỏe hệ thống

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 3600,
  "environment": "production",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_engine": "healthy"
  }
}
```

## Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Please enter a valid email"
    }
  ]
}
```

### Authentication Error (401)
```json
{
  "success": false,
  "message": "Access denied. No token provided."
}
```

### Authorization Error (403)
```json
{
  "success": false,
  "message": "Access denied. Admin privileges required."
}
```

### Not Found Error (404)
```json
{
  "success": false,
  "message": "Resource not found"
}
```

### Server Error (500)
```json
{
  "success": false,
  "message": "Server Error",
  "stack": "Error stack trace (development only)"
}
```

## Rate Limiting

API có rate limiting để bảo vệ hệ thống:
- Authentication endpoints: 5 requests per 15 minutes
- File upload: 10 requests per hour
- AI endpoints: 20 requests per minute
- General API: 100 requests per 15 minutes

## Pagination

Các endpoint trả về danh sách đều hỗ trợ pagination:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10,
    "hasNext": true,
    "hasPrev": false
  }
}
```

## File Upload

Để upload file, sử dụng `multipart/form-data`:

```
POST /upload
Content-Type: multipart/form-data

file: [binary data]
```

## WebSocket Events

Hệ thống hỗ trợ WebSocket cho real-time updates:

### Connection
```
ws://localhost:5000/socket
```

### Events
- `commission_updated`: Cập nhật commission
- `project_progress`: Cập nhật tiến độ dự án
- `notification`: Thông báo mới
- `ai_calculation_complete`: Hoàn thành tính toán AI 