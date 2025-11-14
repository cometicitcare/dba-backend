# Email Services Dependencies

The email services require the following Python packages (already included in most FastAPI projects):

## Core Dependencies

**Already in standard library (no installation needed):**
- `smtplib` - SMTP email sending
- `email` - Email message handling
- `logging` - Logging functionality
- `pathlib` - Path handling
- `secrets` - Secure random generation
- `datetime` - Date and time handling

## External Dependencies

**Required (check if already in requirements.txt):**
```
fastapi>=0.100.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

**Optional but recommended:**
```
redis>=4.0.0          # For production OTP storage (future enhancement)
aiosmtplib>=2.0.0     # For async SMTP (future enhancement)
jinja2>=3.0.0         # For template rendering (future enhancement)
```

## Installation

All core dependencies are already included with a standard FastAPI setup. If you need to install missing packages:

```bash
pip install fastapi pydantic python-dotenv
```

## Verify Installation

Test that all required modules are available:

```python
# Test imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional
import logging
import secrets
import string
from datetime import datetime, timedelta

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

print("All dependencies available! ✓")
```

## Optional: Production Enhancements

### Redis for OTP Storage
```bash
pip install redis
```

### Async SMTP
```bash
pip install aiosmtplib
```

### Template Engine
```bash
pip install jinja2
```

## Version Compatibility

- Python 3.10+
- FastAPI 0.100.0+
- Pydantic 2.0.0+
- python-dotenv 1.0.0+

## Checking Current Installation

```bash
# List installed packages
pip list | grep -E "fastapi|pydantic|python-dotenv"

# Or use:
pip list
```

## Troubleshooting

If you get import errors:

1. **"No module named 'fastapi'"**
   ```bash
   pip install fastapi uvicorn
   ```

2. **"No module named 'pydantic'"**
   ```bash
   pip install pydantic
   ```

3. **"No module named 'dotenv'"**
   ```bash
   pip install python-dotenv
   ```

4. **All at once:**
   ```bash
   pip install -r requirements.txt
   ```

## notes

The email system is designed to work with existing dependencies in your project. No additional packages are required for basic functionality. The core SMTP functionality uses Python's built-in `smtplib` module, which is part of the Python standard library.
