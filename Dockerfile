# Start from the official Frappe + Nginx image
FROM ghcr.io/frappe/frappe-nginx:v14.31.1

# Clone your custom LMS app
RUN bench get-app https://github.com/olgagaga/lmsqos --branch main

# Install LMS and apply changes
WORKDIR /home/frappe/frappe-bench
RUN bench install-app lmsqos

# Rebuild assets (if frontend files changed)
RUN bench build
