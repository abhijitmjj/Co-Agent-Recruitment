# Security Configuration and Guidelines

## Environment Variables

### Required Production Variables
- `NEXTAUTH_SECRET`: Minimum 32 characters, cryptographically secure random string
- `NEXTAUTH_URL`: Must be a valid HTTPS URL in production
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (minimum 10 characters)
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret (minimum 10 characters)
- `GITHUB_CLIENT_ID`: GitHub OAuth client ID (minimum 10 characters)
- `GITHUB_CLIENT_SECRET`: GitHub OAuth client secret (minimum 10 characters)

### Optional Variables
- `GEMINI_MODEL`: AI model name (alphanumeric, hyphens, and dots only)

## Security Measures Implemented

### Input Validation
1. **Resume Text Sanitization**: All user inputs are sanitized to prevent XSS and injection attacks
2. **URL Validation**: All URLs are validated to ensure they use HTTP/HTTPS protocols
3. **Email Validation**: Basic email format validation
4. **Size Limits**: Input text limited to 50KB to prevent DoS attacks

### Authentication
1. **OAuth Integration**: Secure OAuth2 integration with Google and GitHub
2. **Session Management**: Secure session handling with NextAuth
3. **Environment Validation**: Comprehensive environment variable validation

### Infrastructure Security
1. **Docker Security**: 
   - Containers run as non-root users
   - Resource limits to prevent DoS
   - Health checks for service monitoring
   - Ports bound to localhost only
2. **Volume Security**: Named volumes instead of bind mounts

### Data Protection
1. **Error Handling**: Sanitized error messages to prevent information disclosure
2. **Input Sanitization**: HTML tag removal and JavaScript injection prevention
3. **Model Configuration**: AI model names configurable via environment variables

## Dependency Management

### Security Updates
- All dependencies use compatible version ranges (^) for automatic security updates
- Pydantic v2+ for improved validation and security
- Latest stable versions of core dependencies

### Known Vulnerable Dependencies
Check and update these regularly:
- node-fetch: Update to latest version
- firebase packages: Keep updated for security patches

## Development Guidelines

1. **Never commit secrets**: Use .env files and add to .gitignore
2. **Validate all inputs**: Use pydantic models and custom validators
3. **Use environment variables**: For all configuration, especially secrets
4. **Regular updates**: Keep dependencies updated for security patches
5. **Error handling**: Log errors securely without exposing internal details