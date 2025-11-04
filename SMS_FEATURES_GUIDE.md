# TreeTee SMS Features Guide

## Overview

TreeTee (MeshCentral) provides comprehensive SMS integration for two-factor authentication, user messaging, and phone number validation. You can use commercial SMS gateways (Twilio, Plivo, Telnyx) or configure a custom SMS endpoint.

## Available SMS Features

### 1. Two-Factor Authentication (2FA)
- Users with validated phone numbers see an "SMS" button on the login page
- Clicking the button sends a 6-digit login token via SMS
- Provides additional security layer beyond passwords
- Works with MeshCentral's existing translation system for multi-language support

### 2. Phone Number Validation
- Users can add their phone number in "My Account" tab
- MeshCentral sends a 6-digit verification code via SMS
- Once verified, the phone number is stored in the database
- Validated numbers can be used for 2FA and messaging

### 3. Administrative Messaging
- Administrators with user management rights can send SMS to users
- Quick messaging through an "SMS" button in the user list
- Only works for users with validated phone numbers
- Useful for urgent notifications or alerts

### 4. Testing and Debugging
- "My Server" / "Console" tab includes an `sms` command
- Test SMS gateway configuration without going through UI
- Verify gateway credentials and connectivity

## Supported SMS Providers

### Option 1: Twilio (Commercial)

**Configuration:**
```json
{
  "sms": {
    "provider": "twilio",
    "sid": "your-twilio-sid",
    "auth": "your-twilio-auth-token",
    "from": "your-twilio-phone-number"
  }
}
```

**Setup Steps:**
1. Create a Twilio account at https://www.twilio.com (free trial available)
2. Get your Account SID from the Twilio console
3. Get your Auth Token from the Twilio console
4. Purchase or verify a phone number for outbound SMS
5. Add configuration to `meshcentral-data/config.json.template`
6. Store credentials as environment variables in `.env`

**Environment Variables for Twilio:**
```bash
# Add to .env
TWILIO_SID=your_twilio_sid_here
TWILIO_AUTH=your_twilio_auth_token_here
TWILIO_FROM=+1234567890
```

**Template Configuration:**
```json
{
  "sms": {
    "provider": "twilio",
    "sid": "${TWILIO_SID}",
    "auth": "${TWILIO_AUTH}",
    "from": "${TWILIO_FROM}"
  }
}
```

### Option 2: Plivo (Commercial)

**Configuration:**
```json
{
  "sms": {
    "provider": "plivo",
    "auth_id": "your-plivo-auth-id",
    "auth_token": "your-plivo-auth-token",
    "from": "your-plivo-phone-number"
  }
}
```

**Setup Steps:**
1. Create a Plivo account at https://www.plivo.com (free trial available)
2. Get your Auth ID from the Plivo console
3. Get your Auth Token from the Plivo console
4. Purchase or verify a phone number for outbound SMS
5. Configure as shown above

### Option 3: Telnyx (Commercial)

**Configuration:**
```json
{
  "sms": {
    "provider": "telnyx",
    "api_key": "your-telnyx-api-key",
    "from": "your-telnyx-phone-number"
  }
}
```

### Option 4: Custom SMS Gateway (Recommended for Flexibility)

**Configuration:**
```json
{
  "sms": {
    "provider": "url",
    "url": "https://your-sms-gateway.com/api?phone={{phone}}&message={{message}}"
  }
}
```

**How It Works:**
- `{{phone}}` — Replaced with recipient's phone number (URL encoded)
- `{{message}}` — Replaced with SMS text (URL encoded, UTF-8)
- Your endpoint must return HTTP 200 for success
- Any other status code is treated as failure

**Use Cases:**
- Integration with existing corporate SMS infrastructure
- Using SMS providers not natively supported
- Custom rate limiting or routing logic
- Cost optimization through bulk SMS APIs

**Example Custom Endpoint:**
```json
{
  "sms": {
    "provider": "url",
    "url": "http://sms.mydomain.com/api.php?phone={{phone}}&message={{message}}"
  }
}
```

**Character Encoding:**
- Messages are UTF-8 encoded and then URL-encoded
- Example: Chinese characters become `%E4%B8%AD%E6%96%87`
- Your gateway must decode these properly

## Configuration in TreeTee

### Step 1: Choose Your SMS Provider

Decide which provider best fits your needs:
- **Twilio**: Most popular, reliable, global coverage
- **Plivo**: Cost-effective alternative to Twilio
- **Telnyx**: Developer-friendly, competitive pricing
- **Custom URL**: Maximum flexibility, use any SMS API

### Step 2: Update Environment Variables

Add SMS credentials to your `.env` file (NEVER commit this file):

```bash
# Example for Twilio
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH=your_auth_token_here
TWILIO_FROM=+15551234567
```

### Step 3: Update config.json.template

Add the SMS configuration section to `meshcentral-data/config.json.template`:

```json
{
  "settings": {
    "cert": "${MESHCENTRAL_CERT_NAME}",
    "port": ${MESHCENTRAL_PORT},
    "redirPort": ${MESHCENTRAL_REDIRECT_PORT},
    "tlsOffload": true,
    "allowLoginToken": ${ALLOW_LOGIN_TOKEN},
    "WANonly": ${WAN_ONLY},
    "exactPort": true,
    "trustedProxy": ["0.0.0.0/0"]
  },
  "sms": {
    "provider": "twilio",
    "sid": "${TWILIO_SID}",
    "auth": "${TWILIO_AUTH}",
    "from": "${TWILIO_FROM}"
  },
  "domains": {
    "": {
      "title": "TreeTee",
      "newAccounts": ${ALLOW_NEW_ACCOUNTS},
      "ipkvm": ${ENABLE_IPKVM},
      "certUrl": "https://${MESHCENTRAL_CERT_NAME}:${MESHCENTRAL_PORT}"
    }
  }
}
```

### Step 4: Regenerate Configuration

```bash
# Generate config.json from template with environment variables
./generate-config.sh

# Verify SMS configuration is present
grep -A5 '"sms"' meshcentral-data/config.json
```

### Step 5: Deploy to Railway

```bash
# Set environment variables in Railway dashboard
railway variables set TWILIO_SID=ACxxxxxxxxx
railway variables set TWILIO_AUTH=your_token
railway variables set TWILIO_FROM=+15551234567

# Deploy
git add .env.example meshcentral-data/config.json.template
git commit -m "Add SMS support with Twilio integration"
git push origin main

# Or use Railway CLI
railway up --service TreeTee
```

### Step 6: Test SMS Configuration

1. **Login to TreeTee** at https://tee.up.railway.app
2. Navigate to **My Server** → **Console**
3. Type: `sms +15551234567 Test message`
4. Verify the test SMS is received
5. Go to **My Account** → **Phone Number**
6. Enter your phone number and request verification code
7. Confirm you receive the 6-digit code

## Enabling SMS 2FA for Users

### For Administrators:

1. Configure SMS gateway (as shown above)
2. Navigate to **My Server** → **Users**
3. Users can now validate their phone numbers
4. Once validated, they'll see "SMS" button on login page

### For Users:

1. Login to TreeTee
2. Go to **My Account** → **Phone Number**
3. Enter your phone number (with country code, e.g., +1234567890)
4. Click **"Send Verification Code"**
5. Enter the 6-digit code received via SMS
6. Phone number is now validated
7. On next login, you'll see an "SMS" option for 2FA

## Security Considerations

### Never Commit SMS Credentials

**Bad** (NEVER DO THIS):
```json
{
  "sms": {
    "provider": "twilio",
    "sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth": "hardcoded_auth_token_here"
  }
}
```

**Good** (Use Environment Variables):
```json
{
  "sms": {
    "provider": "twilio",
    "sid": "${TWILIO_SID}",
    "auth": "${TWILIO_AUTH}",
    "from": "${TWILIO_FROM}"
  }
}
```

### Pre-commit Hook Protection

The repository's pre-commit hook scans for:
- Twilio SID patterns (AC followed by 32 hex characters)
- Auth tokens
- Phone numbers in credentials
- API keys

### Railway Environment Variables

Set sensitive values in Railway dashboard:
1. Go to Railway project → TreeTee service
2. Click **"Variables"** tab
3. Add: `TWILIO_SID`, `TWILIO_AUTH`, `TWILIO_FROM`
4. These are encrypted and never exposed in logs

## Cost Considerations

### Twilio Pricing (2025)
- **SMS (US/Canada)**: $0.0079 per message
- **SMS (International)**: $0.05 - $0.15 per message
- **Free Trial**: $15 credit, supports trial phone numbers

### Plivo Pricing (2025)
- **SMS (US/Canada)**: $0.0065 per message
- **SMS (International)**: Varies by country
- **Free Trial**: Available with limited credits

### Telnyx Pricing (2025)
- **SMS (US/Canada)**: $0.004 per message
- **SMS (International)**: Competitive rates
- **Pay-as-you-go**: No monthly fees

### Cost Optimization Tips

1. **Use SMS 2FA only when needed**: Enable as optional, not required
2. **Rate limiting**: Prevent SMS spam/abuse through MeshCentral settings
3. **Custom gateway**: Integrate with bulk SMS providers for lower rates
4. **Regional providers**: Use local SMS providers for international users

## Troubleshooting

### SMS Not Sending

**Check Configuration:**
```bash
# View SMS config (credentials will be masked in logs)
railway logs --service TreeTee | grep -i sms

# Test from console
# In MeshCentral web UI: My Server → Console
sms +15551234567 Test message
```

**Common Issues:**
- Invalid credentials (SID/Auth Token)
- Phone number not in E.164 format (+1234567890)
- SMS gateway account not activated
- Insufficient credits in trial account
- Phone number not verified (for trial accounts)

### SMS 2FA Button Not Appearing

**Requirements:**
1. SMS gateway must be configured in config.json
2. User must have validated phone number
3. Phone number must be confirmed (not just entered)

**Verification:**
1. Check user has green checkmark next to phone number
2. Try logging out and back in
3. Check browser console for JavaScript errors

### Custom Gateway Not Working

**Debug Checklist:**
- Endpoint returns HTTP 200 on success
- URL template variables `{{phone}}` and `{{message}}` are correct
- Endpoint can handle URL-encoded UTF-8 characters
- Network firewall allows outbound HTTPS from Railway
- Check Railway logs for HTTP error responses

**Test Custom Endpoint:**
```bash
# Test your custom gateway manually
curl "https://your-gateway.com/api?phone=%2B15551234567&message=Test%20Message"

# Should return HTTP 200
```

### Phone Number Format Issues

**Correct Format (E.164):**
- US: `+15551234567`
- UK: `+447911123456`
- International: `+[country code][number]`

**Incorrect Formats:**
- `(555) 123-4567` (has formatting characters)
- `5551234567` (missing country code)
- `+1 555 123 4567` (has spaces)

## Advanced Configuration

### Disable SMS 2FA (Admin Only)

In config.json.template:
```json
{
  "domains": {
    "": {
      "passwordRequirements": {
        "disableSms2FA": true
      }
    }
  }
}
```

### Custom SMS Templates

MeshCentral uses its translation system for SMS messages. To customize:

1. Check current translations in MeshCentral source
2. Override via custom translation files
3. Support for multiple languages

### Rate Limiting

Prevent SMS abuse:
```json
{
  "domains": {
    "": {
      "limits": {
        "maxSMSPerHour": 5,
        "maxSMSPerDay": 20
      }
    }
  }
}
```

## Integration Examples

### Example 1: Twilio with Railway

**.env:**
```bash
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH=your_auth_token
TWILIO_FROM=+15551234567
```

**config.json.template:**
```json
{
  "sms": {
    "provider": "twilio",
    "sid": "${TWILIO_SID}",
    "auth": "${TWILIO_AUTH}",
    "from": "${TWILIO_FROM}"
  }
}
```

**Railway Variables:**
```bash
railway variables set TWILIO_SID=ACxxxxxxxxx
railway variables set TWILIO_AUTH=your_token
railway variables set TWILIO_FROM=+15551234567
```

### Example 2: Custom Gateway with Python FastAPI

**FastAPI SMS Gateway (external service):**
```python
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/sms")
async def send_sms(phone: str, message: str):
    # Your SMS logic here
    # Example: forward to another SMS provider
    try:
        response = requests.post(
            "https://sms-provider.com/api/send",
            json={"to": phone, "body": message}
        )
        if response.status_code == 200:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=500, detail="SMS failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**config.json.template:**
```json
{
  "sms": {
    "provider": "url",
    "url": "https://your-sms-api.example.com/sms?phone={{phone}}&message={{message}}"
  }
}
```

### Example 3: Custom Gateway with Tailscale VPN

If running a private SMS gateway on your Tailscale network:

**config.json.template:**
```json
{
  "sms": {
    "provider": "url",
    "url": "http://sms-gateway.tailnet:8000/send?phone={{phone}}&message={{message}}"
  }
}
```

**Note**: Railway service must have Tailscale configured to reach internal endpoints.

## Quick Reference

### Configuration Options

| Provider | Required Fields | Optional Fields |
|----------|----------------|-----------------|
| Twilio | `sid`, `auth`, `from` | - |
| Plivo | `auth_id`, `auth_token`, `from` | - |
| Telnyx | `api_key`, `from` | - |
| Custom URL | `url` (with `{{phone}}` and `{{message}}`) | - |

### SMS Commands (Console)

```bash
# Test SMS sending
sms +15551234567 Test message

# Check SMS configuration
info

# View SMS-related logs
log sms
```

### Phone Number Validation Flow

1. User enters phone number → Request code → Receives SMS
2. User enters 6-digit code → Validates → Phone number confirmed
3. User can now use SMS 2FA on login

## Next Steps

1. **Choose SMS provider** (Twilio recommended for ease of use)
2. **Create account** and get credentials
3. **Update .env** with SMS credentials
4. **Update config.json.template** with SMS configuration
5. **Regenerate config** using `./generate-config.sh`
6. **Deploy to Railway** with new environment variables
7. **Test SMS** from My Server → Console
8. **Validate phone number** in My Account
9. **Enable SMS 2FA** for users

## Resources

- **Twilio**: https://www.twilio.com
- **Plivo**: https://www.plivo.com
- **Telnyx**: https://telnyx.com
- **MeshCentral SMS Blog Post**: https://meshcentral2.blogspot.com/2020/04/meshcentral-plivo-and-twilio-sms-support.html
- **Custom SMS Gateway**: https://github.com/Ylianst/MeshCentral/issues/4478
