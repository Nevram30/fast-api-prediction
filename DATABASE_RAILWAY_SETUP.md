# 🗄️ Enable Database Saving on Railway

## Current Status
Your code is ready for database support, but you're seeing this error:
```
ERROR:app.database:✗ Failed to connect to database: No module named 'MySQLdb'
WARNING:app.main:Database features disabled - predictions will not be saved
```

## Why This Happens
1. Railway hasn't redeployed with the updated `requirements.txt` yet, OR
2. You haven't added a MySQL database to your Railway project yet

## ✅ Solution: Add MySQL Database to Railway

### Step 1: Add MySQL Database

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your project** (the one with your FastAPI service)
3. **Click "New"** button (top right corner)
4. **Select "Database"**
5. **Choose "Add MySQL"**
6. **Wait for it to provision** (takes ~30 seconds)

### Step 2: Verify DATABASE_URL is Set

Railway will automatically:
- Create a MySQL database
- Generate a `DATABASE_URL` environment variable
- Link it to your FastAPI service

The `DATABASE_URL` will look like:
```
mysql://root:password@containers-us-west-xxx.railway.app:6379/railway
```

### Step 3: Trigger Redeploy

After adding MySQL:
1. Go to your FastAPI service in Railway
2. Click **"Deployments"** tab
3. Click **"Redeploy"** on the latest deployment

OR simply push a small change:
```bash
# Make a small change to trigger redeploy
git commit --allow-empty -m "Trigger redeploy for database"
git push origin main
```

### Step 4: Verify Database Connection

After redeployment, check the logs. You should see:
```
✓ Database connection established successfully
✓ Database tables created successfully
Database features enabled
```

Instead of the error.

## 🎯 What Will Work After Setup

Once database is connected, your API will:

### 1. Save All Predictions
Every prediction request will be saved with:
- Request ID (UUID)
- Species, province, city
- Date range
- All prediction points
- Timestamp
- Client IP and user agent

### 2. Retrieve Past Predictions

**Get all predictions:**
```bash
GET https://your-app.railway.app/api/v1/predictions
```

**Filter by species:**
```bash
GET https://your-app.railway.app/api/v1/predictions?species=tilapia
```

**Filter by location:**
```bash
GET https://your-app.railway.app/api/v1/predictions?province=Pampanga&city=Mexico
```

**Pagination:**
```bash
GET https://your-app.railway.app/api/v1/predictions?skip=0&limit=50
```

### 3. Get Specific Prediction

```bash
GET https://your-app.railway.app/api/v1/predictions/{request_id}
```

Returns the full prediction with all data points.

### 4. Delete Predictions

```bash
DELETE https://your-app.railway.app/api/v1/predictions/{request_id}
```

## 📊 Database Schema

The database will have these tables:

### `prediction_requests`
- `request_id` (UUID, Primary Key)
- `species` (tilapia/bangus)
- `province`
- `city`
- `date_from`
- `date_to`
- `created_at`
- `ip_address`
- `user_agent`

### `predictions`
- `id` (Auto-increment, Primary Key)
- `request_id` (Foreign Key)
- `prediction_date`
- `predicted_harvest`
- `confidence_lower`
- `confidence_upper`
- `created_at`

## 🔍 Troubleshooting

### Still seeing "No module named 'MySQLdb'" after adding database?

1. **Check if Railway redeployed:**
   - Go to Deployments tab
   - Look for a new deployment after you added MySQL
   - If not, manually trigger redeploy

2. **Verify DATABASE_URL exists:**
   - Go to Settings → Variables
   - Check if `DATABASE_URL` is listed
   - Should start with `mysql://`

3. **Check build logs:**
   - Look for `Installing collected packages: ... cryptography ...`
   - This confirms the new requirements.txt was used

### Database connected but tables not created?

Check logs for:
```
✓ Database tables created successfully
```

If you see errors, the database user might not have CREATE TABLE permissions.

## 💡 Alternative: Use SQLite (No Railway Database Needed)

If you don't want to use MySQL, you can switch to SQLite:

1. Update `app/config.py`:
```python
database_url: str = os.getenv("DATABASE_URL", "sqlite:///./predictions.db")
```

2. Update `requirements.txt` - remove `pymysql` and `cryptography`

3. SQLite will create a local file `predictions.db`

**Note:** SQLite on Railway will reset on each deployment (ephemeral storage).

## 📝 Summary

**To enable database saving:**
1. ✅ Code is ready (already pushed)
2. ⏳ Add MySQL database in Railway dashboard
3. ⏳ Wait for automatic redeploy
4. ✅ Database will work automatically

**Current behavior without database:**
- ✅ Predictions work perfectly
- ❌ Predictions are not saved
- ✅ No errors in API responses
- ⚠️ Warning in logs (expected)

---

**Need help?** Check Railway logs or the interactive docs at `/docs` to test the database endpoints once connected.
