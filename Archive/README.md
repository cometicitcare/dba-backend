# Archive Folder Structure

This folder contains non-essential files and documentation that were moved out of the root directory to maintain a clean codebase structure.

## Directory Organization

### 📚 Documentation/
Comprehensive documentation files, guides, and implementation summaries for various features and fixes:
- Feature implementation guides (Pagination, Response Structure, Temporary Entities)
- API integration documentation (Vihara, Bhikku, Objection System, Sasanarakshaka)
- Fix implementation summaries and analysis documents
- Quick reference guides and endpoint documentation

**Total Files:** 47 documentation files

### 🧪 TestScripts/
Test files, test collections, and testing utilities:
- Python test scripts for various endpoints and features
- Shell script test runners
- Postman collections for API testing
- PyTest test configurations

**Total Files:** 22 test files/folders

### 🔧 Fixes/
Migration and fix-related scripts:
- `fix_alembic_revision.py` - Database migration fixes
- `fix_migration.sh` - Migration helper script

### ⚙️ Setup/
Setup and maintenance scripts:
- `setup_bhikku.sh` - Bhikku module setup
- `check_prod_cookie_expiry.sh` - Production environment monitoring
- `sync_cmm_gndata.py` - Data synchronization utility

### 📡 APIReferences/
API endpoint reference files and guides:
- Endpoint specifications and listings
- API documentation text files
- Integration guides

**Total Files:** 4 reference files

### 📦 TempData/
Temporary data files:
- Database dumps
- Sample payload files
- Temporary data exports

### 🗑️ todel/
Files marked for deletion or being deprecated:
- Updated configuration files
- Old environment configurations
- Backup configuration files

## Cleaned Root Directory

The root directory now contains only essential files for the application:

**Configuration Files:**
- `alembic.ini` - Database migration configuration
- `docker-compose.yml` - Docker composition
- `Dockerfile` - Docker image definition
- `pyproject.toml` - Project metadata
- `railway.toml` - Railway deployment config
- `Makefile` - Build automation
- `.gitignore`, `.gitattributes` - Git configuration

**Application Structure:**
- `app/` - Main application source code
- `alembic/` - Database migrations
- `storage/` - File storage
- `data_backups/` - Data backup directory
- `official_backup_data/` - Official backups

**Utility Scripts:**
- `start.sh` - Application startup
- `verify_db.py` - Database verification

## Recovery

All archived files remain organized and accessible. To restore any file from the archive:

```bash
# Example: Move a file from archive back to root
mv Archive/Documentation/FILENAME.md ./
```

## Notes

- All archived files maintain their original names and content
- The hierarchical structure makes it easy to find and reference archived materials
- This archive serves as both a documentation repository and a repository for deprecated test files
