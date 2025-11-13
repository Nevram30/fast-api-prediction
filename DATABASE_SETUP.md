# Database Setup Guide - Railway MySQL Integration

This guide explains how to set up and use the MySQL database integration for saving fish price predictions.

## Overview

The API now automatically saves all prediction requests and results to a MySQL database. This allows you to:
- Track all prediction requests with metadata (IP, timestamp, location)
- Query historical predictions
- Analyze prediction patterns
- Retrieve predictions by various filters

## Database Schema

### Tables

#### `prediction_requests`
Stores metadata about each prediction request.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Auto-increment primary key |
| request_id | VARCHAR(36) | UUID for tracking |
| species | VARCHAR(50) | Fish species (tilapia/bangus) |
| province | VARCHAR(100) | Province name |
| city | VARCHAR(100) | City/Municipality name |
| date_from | DATE | Start date of prediction range |
| date_to | DATE | End date of prediction range |
| created_at | TIMESTAMP | When request was made |
| ip_address | VARCHAR(45) | Client IP address |
| user_agent | TEXT | Client user agent |

#### `predictions`
Stores individual prediction points.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Auto-increment primary key |
| request_id | VARCHAR(36) | Foreign key to prediction_requests |
| prediction_date | DATE | Date of this prediction |
| predicted_price | DECIMAL(10,2) | Predicted price in PHP |
| confidence_lower | DECIMAL(10,2) | Lower confidence bound (optional) |
| confidence_upper | DECIMAL(10,2) | Upper confidence bound (optional) |
| created_at | TIMESTAMP | When prediction was saved |

## Railway Setup

### Step 1: Add MySQL Database to Railway

1. Go to your Railway project dashboard
2. Click "New" → "Database" → "Add MySQL"
3. Railway will automatically create a MySQL database and provide connection details
4. The `DATABASE_URL` environment variable will be automatically set

### Step 2: Verify Database Connection

Railway automatically provides the `DATABASE_URL` in this format:
```
mysql://user:password@host:port/database
```

The application will automatically convert this to the SQLAlchemy format:
```
mysql+pymysql://user:password@host:port/database
```

### Step 3: Deploy Your Application

1. Push your code to GitHub (if using GitHub integration)
2. Railway will automatically redeploy
3. Check the logs to verify database connection:
   ```
   ✓ Database connection established successfully
   ✓ Database tables created successfully
   Database features enabled
   ```

## Local Development Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Local MySQL (Optional)

If you want to test locally with MySQL:

```bash
# Install MySQL locally or use Docker
docker run --name mysql-fish-forecast \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=fish_forecast \
  -p 3306:3306 \
  -d mysql:8.0
```

### Step 3: Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/fish_forecast
```

### Step 4: Run the Application

```bash
python -m uvicorn app.main:app --reload
```

The application will:
1. Connect to the database
2. Automatically create tables if they don't exist
3. Start accepting requests

## API Endpoints

### 1. Make Prediction (Auto-saves to Database)

**POST** `/api/v1/predict`

```json
{
  "city": "Panabo",
  "dateFrom": "2024-01-01",
  "dateTo": "2024-01-31",
  "province": "Pampanga",
  "species": "tilapia"
}
```

**Response includes `request_id`:**
```json
{
  "success": true,
  "predictions": [...],
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    ...
  }
}
```

### 2. Get All Saved Predictions

**GET** `/api/v1/predictions`

**Query Parameters:**
- `species` (optional): Filter by species (tilapia/bangus)
- `province` (optional): Filter by province
- `city` (optional): Filter by city
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Max results (default: 100, max: 100)

**Example:**
```bash
GET /api/v1/predictions?species=tilapia&province=Pampanga&limit=10
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
      "species": "tilapia",
      "province": "Pampanga",
      "city": "Panabo",
      "date_from": "2024-01-01",
      "date_to": "2024-01-31",
      "created_at": "2024-01-15T10:30:00",
      "prediction_count": 31
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### 3. Get Specific Prediction by ID

**GET** `/api/v1/predictions/{request_id}`

**Example:**
```bash
GET /api/v1/predictions/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "success": true,
  "request": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "species": "tilapia",
    "province": "Pampanga",
    "city": "Panabo",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "created_at": "2024-01-15T10:30:00",
    "ip_address": "192.168.1.1"
  },
  "predictions": [
    {
      "date": "2024-01-01",
      "predicted_price": 975.0,
      "confidence_lower": null,
      "confidence_upper": null
    },
    ...
  ],
  "prediction_count": 31
}
```

### 4. Delete Prediction

**DELETE** `/api/v1/predictions/{request_id}`

**Example:**
```bash
DELETE /api/v1/predictions/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "success": true,
  "message": "Prediction request 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

## Error Handling

The application is designed to be resilient:

1. **Database Unavailable**: If the database is not configured or unavailable, the API will still work but won't save predictions. A warning will be logged.

2. **Database Save Failure**: If saving to the database fails, the prediction will still be returned to the user. The error will be logged.

3. **Query Endpoints**: If the database is unavailable, query endpoints will return a 503 Service Unavailable error.

## Monitoring

### Check Database Status

The `/api/v1/health` endpoint includes database status:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "tilapia": true,
    "bangus": true
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Check Logs

Railway logs will show:
- Database connection status
- Table creation status
- Prediction save operations
- Any database errors

## Database Maintenance

### Backup

Railway provides automatic backups for MySQL databases. You can also:

1. Use Railway's backup feature in the dashboard
2. Export data using MySQL tools:
   ```bash
   mysqldump -h host -u user -p database > backup.sql
   ```

### Cleanup Old Data

You can delete old predictions using the DELETE endpoint or directly in the database:

```sql
-- Delete predictions older than 90 days
DELETE FROM prediction_requests 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

## Troubleshooting

### Connection Issues

**Problem**: "Database not available" warning

**Solutions**:
1. Verify `DATABASE_URL` is set in Railway environment variables
2. Check database is running in Railway dashboard
3. Verify connection string format is correct

### Table Creation Issues

**Problem**: Tables not created automatically

**Solutions**:
1. Check application logs for errors
2. Verify database user has CREATE TABLE permissions
3. Manually create tables using the schema above

### Performance Issues

**Problem**: Slow queries

**Solutions**:
1. Indexes are automatically created on frequently queried columns
2. Use pagination (skip/limit) for large result sets
3. Consider upgrading Railway database plan for more resources

## Security Considerations

1. **Connection String**: Never commit `.env` file with real credentials
2. **Railway Variables**: Use Railway's environment variables (automatically secure)
3. **SQL Injection**: All queries use SQLAlchemy ORM (protected by default)
4. **Access Control**: Consider adding authentication for DELETE endpoints in production

## Next Steps

1. Monitor database usage in Railway dashboard
2. Set up alerts for database errors
3. Consider adding indexes for custom queries
4. Implement data retention policies
5. Add authentication/authorization for sensitive endpoints
