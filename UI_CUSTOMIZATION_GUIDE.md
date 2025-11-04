# TreeTee UI Customization Guide

MeshCentral provides extensive built-in UI customization options. You can customize colors, logos, text, and even completely rebrand the interface.

## Quick Customization (Config File Only)

### Edit config.json.template

Add these options to the `domains` section:

```json
{
  "domains": {
    "": {
      "title": "TreeTee",
      "title2": "AI Agent Control Platform",
      "newAccounts": false,
      "ipkvm": false,
      "certUrl": "https://tee.up.railway.app:443",

      // UI Customization Options:
      "titlePicture": "title-logo.png",
      "loginPicture": "login-logo.png",
      "welcomeText": "Welcome to TreeTee - Secure AI Agent Monitoring",
      "welcomePicture": "welcome-image.png",
      "footer": "<a href='https://yourdomain.com'>Your Company</a>",
      "nightMode": 1
    }
  }
}
```

### Available Config Options

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `title` | String | Main title (top left) | `"TreeTee"` |
| `title2` | String | Subtitle | `"AI Agent Platform"` |
| `titlePicture` | String | Logo image (450x66 PNG) | `"logo.png"` |
| `loginPicture` | String | Login page logo | `"login-logo.png"` |
| `welcomeText` | String | Text on welcome page | `"Welcome!"` |
| `welcomePicture` | String | Welcome page image | `"banner.png"` |
| `footer` | HTML | Custom footer HTML | `"<a href...>"` |
| `nightMode` | Number | Dark mode (0=off, 1=on, 2=user choice) | `2` |
| `userQuota` | Number | Disk space per user (bytes) | `1048576` |
| `meshQuota` | Number | Disk space per device group | `1048576` |
| `userNameIsEmail` | Boolean | Force email as username | `true` |
| `agentCustomization` | Object | Customize agent branding | See below |

## Advanced Customization (Custom Files)

### Step 1: Create Custom Web Directory

```bash
# Create custom web directory structure
mkdir -p meshcentral-web/public/images
mkdir -p meshcentral-web/public/styles
mkdir -p meshcentral-web/views
```

### Step 2: Add Custom Images

Place your custom images in `meshcentral-web/public/images/`:

**Required Image Sizes:**
- **Title Logo**: 450 x 66 pixels (PNG) - Top left corner logo
- **Login Logo**: Any size (PNG/JPG) - Login page logo
- **Welcome Image**: Any size (PNG/JPG) - Welcome page banner
- **Favicon**: 32 x 32 pixels (ICO) - Browser tab icon

**Example images to create:**
```bash
meshcentral-web/public/images/
├── title-logo.png          # 450x66 - Main logo
├── login-logo.png          # Login page logo
├── welcome-banner.png      # Welcome page banner
└── favicon.ico             # 32x32 - Browser icon
```

### Step 3: Custom CSS Styling

Create `meshcentral-web/public/styles/custom.css`:

```css
/* Custom CSS for TreeTee Branding */

/* Main background color */
body {
    background-color: #1a1a1a;
}

/* Top bar styling */
#topbar {
    background-color: #2c3e50;
    border-bottom: 2px solid #3498db;
}

/* Button colors */
.btn-primary {
    background-color: #3498db;
    border-color: #2980b9;
}

.btn-primary:hover {
    background-color: #2980b9;
}

/* Link colors */
a {
    color: #3498db;
}

a:hover {
    color: #5dade2;
}

/* Login page styling */
#loginpanel {
    background-color: rgba(44, 62, 80, 0.95);
    border: 1px solid #3498db;
}

/* Device list styling */
.device {
    border-left: 3px solid #3498db;
}

.device:hover {
    background-color: #34495e;
}

/* Custom branding text */
.footer-custom {
    text-align: center;
    padding: 10px;
    color: #7f8c8d;
    font-size: 12px;
}
```

### Step 4: Update config.json Template

Add custom CSS and images to config:

```json
{
  "domains": {
    "": {
      "title": "TreeTee",
      "title2": "AI Agent Control Platform",
      "titlePicture": "title-logo.png",
      "loginPicture": "login-logo.png",
      "welcomeText": "Welcome to TreeTee - Secure AI Agent Monitoring & Control",
      "welcomePicture": "welcome-banner.png",
      "footer": "<div class='footer-custom'>TreeTee &copy; 2025 | <a href='https://yourdomain.com'>Your Company</a></div>",
      "nightMode": 2,
      "newAccounts": false,
      "ipkvm": false,
      "certUrl": "https://${MESHCENTRAL_CERT_NAME}:${MESHCENTRAL_PORT}"
    }
  }
}
```

### Step 5: Custom Templates (Advanced)

To modify HTML templates, copy from `node_modules/meshcentral/views/` to `meshcentral-web/views/`:

```bash
# Copy login template for customization
cp node_modules/meshcentral/views/login.handlebars meshcentral-web/views/

# Edit meshcentral-web/views/login.handlebars
# Add custom HTML, modify layout, add branding
```

## Docker Integration

For Railway/Docker deployments, add custom files to your repository:

```bash
# Your project structure
trifecta/
├── meshcentral-web/
│   ├── public/
│   │   ├── images/
│   │   │   ├── title-logo.png
│   │   │   ├── login-logo.png
│   │   │   └── favicon.ico
│   │   └── styles/
│   │       └── custom.css
│   └── views/
│       └── (optional custom templates)
├── meshcentral-data/
│   └── config.json.template
└── Dockerfile
```

Update your Dockerfile to include custom files:

```dockerfile
# Copy custom web files
COPY meshcentral-web /app/meshcentral-web
```

## Agent Branding (Advanced)

Customize the agent installer and running agent:

Add to config.json:

```json
{
  "domains": {
    "": {
      "agentCustomization": {
        "displayName": "TreeTee Agent",
        "description": "TreeTee AI Agent Monitor",
        "companyName": "Your Company",
        "serviceName": "TreeTeeAgent",
        "image": "custom-agent-icon.png"
      }
    }
  }
}
```

**Important**: Agent customization must be done BEFORE deploying agents!

## Night Mode Options

Control dark/light theme:

```json
"nightMode": 0    // Disabled (light mode only)
"nightMode": 1    // Enabled (dark mode only)
"nightMode": 2    // User choice (default)
```

## Example: Complete Branding Configuration

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
  "domains": {
    "": {
      "title": "TreeTee",
      "title2": "AI Agent Monitoring Platform",
      "titlePicture": "title-logo.png",
      "loginPicture": "login-logo.png",
      "welcomeText": "Welcome to TreeTee - The Universal Handshake Protocol for AI Agents",
      "welcomePicture": "welcome-banner.png",
      "footer": "<div style='text-align:center;padding:10px;color:#888;'>TreeTee &copy; 2025 | Powered by MeshCentral | <a href='https://github.com/J-Palomino/trifecta'>GitHub</a></div>",
      "nightMode": 2,
      "newAccounts": ${ALLOW_NEW_ACCOUNTS},
      "ipkvm": ${ENABLE_IPKVM},
      "certUrl": "https://${MESHCENTRAL_CERT_NAME}:${MESHCENTRAL_PORT}",
      "agentCustomization": {
        "displayName": "TreeTee Agent",
        "description": "TreeTee AI Agent Monitor and Control",
        "companyName": "TreeTee",
        "serviceName": "TreeTeeAgent"
      }
    }
  },
  "letsencrypt": {
    "email": "${LETSENCRYPT_EMAIL}",
    "names": "${LETSENCRYPT_DOMAIN}",
    "skipChallengeVerification": false,
    "production": ${LETSENCRYPT_PRODUCTION}
  }
}
```

## Quick Wins (Easiest Changes)

### 1. Change Title
```json
"title": "Your Platform Name"
```

### 2. Add Welcome Message
```json
"welcomeText": "Welcome to Your AI Agent Platform!"
```

### 3. Enable Dark Mode
```json
"nightMode": 1
```

### 4. Add Custom Footer
```json
"footer": "<a href='https://yourcompany.com'>Your Company</a> © 2025"
```

## Deployment Process

1. **Make changes** to `config.json.template`
2. **Add custom images** to `meshcentral-web/public/images/`
3. **Regenerate config**: `./generate-config.sh`
4. **Commit changes**: `git add . && git commit -m "UI customization"`
5. **Deploy**: `git push && railway up --service TreeTee --detach`

## Testing Locally

```bash
# Test customization locally
docker-compose down
./generate-config.sh
docker-compose up -d

# View at http://localhost
# (Accept self-signed cert warning)
```

## Resources and References

### Official Documentation
- **Customization Guide**: https://ylianst.github.io/MeshCentral/meshcentral/customization/
- **Config Options**: https://ylianst.github.io/MeshCentral/meshcentral/config/
- **Community Wiki**: https://meshcentral-community.com/doku.php?id=howto:customization

### Image Resources
- **Logo Maker**: https://www.canva.com (free)
- **Favicon Generator**: https://favicon.io
- **Image Optimizer**: https://tinypng.com

### CSS Frameworks
MeshCentral uses standard HTML/CSS, so you can use:
- Bootstrap classes (already included)
- Custom CSS in `custom.css`
- Inline styles in config footer/welcome text

## Common Customization Use Cases

### 1. Corporate Branding
```json
{
  "title": "Acme IT Management",
  "titlePicture": "acme-logo.png",
  "footer": "Acme Corporation © 2025 | IT Department"
}
```

### 2. MSP/Service Provider
```json
{
  "title": "TechSupport Pro",
  "title2": "Managed IT Services",
  "welcomeText": "24/7 Remote Support for Your Business"
}
```

### 3. Personal Lab
```json
{
  "title": "HomeLab Central",
  "nightMode": 1,
  "welcomeText": "My Personal Infrastructure Management"
}
```

## Troubleshooting

### Images not showing
- Ensure images are in `meshcentral-web/public/images/`
- Check file names match config exactly (case-sensitive)
- Verify image format (PNG recommended)
- Clear browser cache

### CSS not applying
- Verify `custom.css` is in `meshcentral-web/public/styles/`
- Link must be added to templates manually
- Check browser console for 404 errors

### Changes not visible
- Regenerate config: `./generate-config.sh`
- Restart MeshCentral: `docker-compose restart`
- Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R)

## Next Steps

1. Create your custom images (logo, login banner, etc.)
2. Update `config.json.template` with new titles and text
3. Optional: Add `custom.css` for colors/styling
4. Test locally with `docker-compose`
5. Deploy to Railway

**The UI customization is entirely through configuration and file placement - no code changes needed!**
