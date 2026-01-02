# Hackathon Sponsorship Outreach Automation

## 🎯 Project Overview

This automation system streamlines the process of reaching out to potential sponsors for college hackathons. It reads sponsor data from CSV files, sends personalized emails based on sponsor categories, and implements enterprise-grade safety features including rate limiting, anti-duplication, and resumable execution.

### Key Features

- ✅ **Safe Email Automation**: Uses Gmail App Password authentication (never your real password)
- ✅ **Anti-Duplication Protection**: Ensures no sponsor receives more than one email
- ✅ **Rate Limiting**: Built-in delays and cooldowns to prevent spam flags
- ✅ **Resumable Execution**: Safely resumes from where it left off if interrupted
- ✅ **Category-Based Templates**: Different email content for Mechanical, CS, and General sponsors
- ✅ **PDF Attachments**: Automatically attaches relevant brochures based on category
- ✅ **Comprehensive Logging**: Full audit trail of all actions
- ✅ **CSV State Management**: Single source of truth for send status

## 🛠 Tech Stack

- **Language**: Python 3.7+
- **Email Protocol**: SMTP (Simple Mail Transfer Protocol)
- **Email Service**: Gmail SMTP
- **Authentication**: Gmail App Password
- **Data Format**: CSV (Comma-Separated Values)
- **Dependencies**: Standard library only (no external packages required)

## 🚀 Gmail App Password Setup

**⚠️ IMPORTANT: You MUST use an App Password, NOT your regular Gmail password.**

### Step 1: Enable 2-Step Verification

1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "How you sign in to Google," click "2-Step Verification"
4. Follow the setup process to enable 2-step verification
5. You'll need to verify your identity using your current phone number

### Step 2: Generate App Password

1. While still in Google Account settings → Security
2. Under "How you sign in to Google," find "App passwords"
3. Click "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Enter a name like "Hackathon Sponsorship Automation"
6. Click "Generate"
7. **IMPORTANT**: Copy the 16-character password immediately and save it somewhere safe
8. This password will look like: `abcd efgh ijkl mnop`

### Why App Password is Required?

- **Security**: App passwords are specific to applications and can be revoked independently
- **Gmail Policy**: Gmail blocks regular password access for automated scripts
- **Best Practice**: Separates application access from your main account password

## 🔧 Configuration

### Method 1: Config File (For Development)

Edit the `config/config.ini` file:

```ini
[SMTP]
user = your_email@gmail.com
password = your_16_character_app_password
```

## 📊 CSV Format

The `sponsors.csv` file is the single source of truth for all sponsor data and send status.

### Required Columns

| Column Name   | Description                                   | Example                      |
|---------------|-----------------------------------------------|------------------------------|
| Company Name  | Sponsor company name                          | "Microsoft Corporation"      |
| POC Name      | Point of Contact name                         | "James Wilson"               |
| Email Address | POC email address                             | "james.wilson@microsoft.com" |
| Category      | Sponsor category (Mechanical, CS, or General) | "CS"                         |
| Status        | Send status ("Not Sent" or "Sent")            | "Not Sent"                   |
| Sent Timestamp| When email was sent (ISO format)              | "2025-12-31 13:22:10"        |

### CSV Example

```csv
Company Name,POC Name,Email Address,Category,Status,Sent Timestamp
Microsoft Corporation,James Wilson,james.wilson@microsoft.com,CS,Not Sent,
Autodesk Inc.,Sarah Johnson,sarah.johnson@autodesk.com,Mechanical,Not Sent,
Dell Technologies,Steven Rodriguez,steven.rodriguez@dell.com,General,Not Sent,
```

### Category Handling Logic

- **Mechanical**: Triggers Vortex360 event emails with CAD/mechanical design focus
- **CS**: Triggers Equinox event emails with software/AI/IT focus  
- **General**: Triggers Equinox event emails with broad technology innovation focus
- **Invalid Categories**: Any category not exactly "Mechanical" or "CS" is treated as "General"

## 🎯 Category-Based Email Templates

### Mechanical Category
- **Event**: Vortex360
- **Focus**: CAD, mechanical design, engineering innovation
- **Attachment**: `Vortex360 '26.pdf`

### CS Category  
- **Event**: Equinox
- **Focus**: Software development, AI/ML, digital innovation
- **Attachment**: `Equinox '26.pdf`

### General Category
- **Event**: Equinox  
- **Focus**: Broad technology innovation and community engagement
- **Attachment**: `Equinox '26.pdf`

## ⚡ Rate Limiting & Cooldown Rules

The script implements strict rate limiting to prevent Gmail spam detection:

### Email Delays
- **Between Each Email**: Random delay of 5-13 seconds
- **Purpose**: Mimics human-like sending behavior

### Batch Cooldowns
- **After Every 40 Emails**: 35-minute cooldown period
- **Purpose**: Prevents Gmail from flagging automated behavior
- **Resume Safety**: If interrupted during cooldown, script resumes remaining time

### Logging
All rate limiting actions are logged clearly:
```
2025-12-31 10:21:42 - INFO - Waiting 8 seconds before next email...
2025-12-31 10:21:50 - INFO - Email sent successfully to james.wilson@microsoft.com
2025-12-31 10:25:30 - INFO - Reached 40 emails. Starting cooldown for 35 minutes.
2025-12-31 11:00:30 - INFO - Cooldown completed. Resuming email sending.
```

## 🔄 Resume Safety Mechanism

The script is designed to be completely resumable:

### How It Works
1. **CSV as Source of Truth**: All send status is stored in the CSV file
2. **Status-Based Filtering**: Only sends to rows where Status != "Sent"
3. **Immediate Updates**: After each successful send, updates CSV immediately
4. **Graceful Interruption**: Can be stopped at any time with Ctrl+C
5. **Safe Resume**: Restarts and continues from unsent emails only

### Anti-Duplication Guarantees
- ✅ Same email address never receives multiple emails
- ✅ Status check happens before every send
- ✅ CSV update happens immediately after successful sends
- ✅ Failed sends never mark status as "Sent"

## 🏃 How to Run the Script

### Prerequisites
1. Python 3.7+ installed
2. Gmail account with 2-step verification enabled
3. Gmail App Password generated
4. CSV file with sponsor data prepared

### Execution Steps

1. **Navigate to project directory**:
   ```bash
   cd hackathon_sponsorship_outreach
   ```

2. **Set up credentials** (choose one method):

   **Edit config file**:
   Edit `config/config.ini` with your credentials

3. **Prepare your CSV file**:
   - Edit `sponsors.csv` with your actual sponsor data
   - Ensure all required columns are present
   - Set Status to "Not Sent" for new campaigns

4. **Run the script**:
   ```bash
   python main.py
   ```

### Expected Output
```
2025-12-31 10:21:42 - INFO - Starting Hackathon Sponsorship Outreach Automation
2025-12-31 10:21:42 - INFO - ============================================================
2025-12-31 10:21:42 - INFO - Configuration loaded successfully for user: your_email@gmail.com
2025-12-31 10:21:42 - INFO - Loaded 40 sponsors from CSV
2025-12-31 10:21:42 - INFO - ============================================================
2025-12-31 10:21:42 - INFO - Processing 1/40 sponsors: Microsoft Corporation
2025-12-31 10:21:42 - INFO - Email sent successfully to james.wilson@microsoft.com
2025-12-31 10:21:50 - INFO - Waiting 8 seconds before next email...
```

## 📋 Safety & Troubleshooting

### Safety Features

1. **No Hardcoded Credentials**: All sensitive data must be configured
2. **Status Validation**: Never sends to already-sent addresses
3. **Error Handling**: Continues processing even if individual emails fail
4. **Immediate State Updates**: CSV is updated after each successful send
5. **Graceful Shutdown**: Responds to Ctrl+C interruption

### Common Issues & Solutions

#### Issue: "SMTP authentication failed"
**Solution**: 
- Verify your App Password is correct (16 characters with hyphens)
- Ensure 2-step verification is enabled
- Check that you're using the App Password, not your regular password

#### Issue: "Connection refused" or timeout
**Solution**:
- Check internet connection
- Verify Gmail SMTP settings (server: smtp.gmail.com, port: 587)
- Try running script again

#### Issue: "CSV file not found"
**Solution**:
- Ensure `sponsors.csv` exists in the project directory
- Check file permissions
- Verify CSV format is correct

#### Issue: Emails going to spam
**Solution**:
- Rate limiting is already implemented to prevent this
- Consider using a less common sending email address
- Recipients can whitelist your email address

#### Issue: Script stops unexpectedly
**Solution**:
- This is normal behavior after 35-minute cooldowns
- Check logs for cooldown messages
- Script will automatically resume after cooldown

### Testing Without Sending

To test the script without actually sending emails:

1. Create a test CSV with your own email address
2. Run the script and observe the logs
3. Verify the email content and format
4. Check that CSV status updates correctly

### Monitoring Progress

The script provides comprehensive logging:
- Total sponsors loaded
- Current sponsor being processed
- Email send success/failure
- Rate limiting delays
- Batch cooldown periods
- Final completion summary

## 📁 Project Structure

```
hackathon_sponsorship_outreach/
├── main.py                    # Main automation script
├── sponsors.csv               # Sponsor data and status tracking
├── config/
│   └── config.ini            # Configuration file (development)
├── email_templates/
│   ├── mechanical_template.txt
│   ├── cs_template.txt
│   └── general_template.txt
├── brochures/
│   ├── mechanical_brochure.pdf
│   ├── cs_brochure.pdf
│   └── general_brochure.pdf
└── README.md                  # This documentation
```

## 🔒 Security Best Practices

1. **Never share App Passwords**: Keep them confidential
2. **Use Environment Variables**: For production deployments
3. **Regular Password Rotation**: Change App Passwords periodically
4. **Monitor Gmail Activity**: Check your Gmail account for unusual activity
5. **Secure File Permissions**: Protect config files from unauthorized access
6. **Backup CSV Data**: Regularly backup your sponsor data

## 🤝 Contributing

This project is designed to be self-contained and requires no external dependencies. To customize:

1. **Email Templates**: Edit files in `email_templates/`
2. **Rate Limiting**: Modify constants in `main.py`
3. **CSV Format**: Ensure compatibility with existing structure
4. **Brochures**: Replace placeholder files with actual PDFs

## 📄 License

This project is provided as-is for educational and commercial use. Please ensure compliance with Gmail's Terms of Service and applicable anti-spam regulations when using this tool.

## ⚠️ Important Notes

- **Compliance**: Ensure your use complies with CAN-SPAM Act and local regulations
- **Professional Use**: This tool is designed for legitimate business outreach
- **Rate Limits**: Gmail has sending limits; this script respects them
- **Data Privacy**: Handle sponsor data according to your privacy policies
- **Testing**: Always test with a small batch before large campaigns

---
