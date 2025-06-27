# BugAgaric Development Guidelines

## Dockerfile Modification Rules

### General Principles
1. **Stability First**: The Dockerfile should be treated as a stable configuration file. Avoid unnecessary modifications.
2. **Version Control**: Any changes to the Dockerfile must be carefully considered and documented.
3. **Backward Compatibility**: Changes should maintain backward compatibility with existing deployments.

### When to Modify Dockerfile
The Dockerfile should only be modified in the following cases:
1. Critical security updates
2. Major version upgrades of core dependencies
3. Bug fixes that cannot be resolved through other means
4. Performance optimizations that are absolutely necessary

### When NOT to Modify Dockerfile
Do NOT modify the Dockerfile for:
1. Minor dependency updates
2. Style changes
3. Experimental features
4. Personal preferences
5. Temporary solutions

### Modification Process
If a Dockerfile modification is necessary:
1. Document the reason for the change
2. Test the changes thoroughly
3. Update the version number
4. Update the documentation
5. Get approval from the team

## Best Practices
1. Keep the base image version stable
2. Document all environment variables
3. Use specific version tags for dependencies
4. Maintain clear comments
5. Follow the principle of least privilege

## Version Control
- Major version changes: Update the first number (e.g., 1.0.0 -> 2.0.0)
- Minor changes: Update the second number (e.g., 1.0.0 -> 1.1.0)
- Bug fixes: Update the third number (e.g., 1.0.0 -> 1.0.1)

## Testing Requirements
Before committing any Dockerfile changes:
1. Build the image locally
2. Run all tests
3. Verify all functionality
4. Check for any security implications
5. Document the testing process 