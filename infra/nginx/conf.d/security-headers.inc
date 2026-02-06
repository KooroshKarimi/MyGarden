add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; font-src 'self'; frame-src 'self';" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
