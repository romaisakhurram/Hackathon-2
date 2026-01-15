# Data Model: Professional SaaS Todo

## Task Entity

### Fields
- **id**: string (required, unique, auto-generated)
- **title**: string (required, max 255 characters)
- **description**: string (optional, max 1000 characters)
- **priority**: string (required, enum: 'low', 'medium', 'high', default: 'medium')
- **status**: string (required, enum: 'pending', 'in-progress', 'completed', default: 'pending')
- **created_at**: datetime (required, server-generated)
- **updated_at**: datetime (required, server-generated)
- **user_id**: string (required, foreign key from user)

### Validation Rules
- Title must be 1-255 characters
- Description, if provided, must be 1-1000 characters
- Priority must be one of 'low', 'medium', 'high'
- Status must be one of 'pending', 'in-progress', 'completed'

### State Transitions
- Status can transition from 'pending' → 'in-progress' → 'completed'
- Status can transition from 'in-progress' → 'pending' or 'completed'
- Status can transition from 'completed' → 'in-progress'

## User Entity (Managed by Better Auth)

### Fields
- **id**: string (required, unique, auto-generated)
- **email**: string (required, unique)
- **name**: string (optional)
- **created_at**: datetime (required, server-generated)
- **updated_at**: datetime (required, server-generated)

### Validation Rules
- Email must be valid email format and unique
- Name, if provided, must be 1-255 characters