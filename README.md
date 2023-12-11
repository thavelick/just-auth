# Just Auth
A minimal reverse proxy server with cookie based authentication.

## Installation and Usage
1. Clone the repository
    ```
    git clone https://github.com/thavelick/just-auth
    ```
2. Run the server
    ```
    cd just-auth
    ./just-auth.py
    ```

## Setup

The idea here is you'd put this between a reverse-proxy capable web server like nginx and your application.
It contains a simple login form, and sets a cookie to track logged in status.
The url you proxy to needs to be http, not https.
It is expected that the web server in front of Just Auth will provide https.

### Environment Variables

| Variable | Description | Default |
| -------- | ----------- | ------- |
| PASSWORD | The password to use for authentication | super secret password |
| SALT | The salt to use for hashing the password | pretty secret salt |
| PROXY_TO_URL | The url to proxy to | http://localhost:8000 |
| PORT | The port to listen on | 8486

### A realistic example

Let's say you want to put a site running with an nginx reverse proxy behind Just Auth. Assume before you begin that the site is already running on port 7777 with the following nginx config:

```
server {
	server_name bangs.my-site.xyz;
	location / {
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
		proxy_pass http://localhost:7777;
	}
	listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/my-site.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/my-site.xyz/privkey.pem;
}

server {
    if ($host = bangs.my-site.xyz) {
        return 301 https://$host$request_uri;
    }
	server_name bangs.my-site.xyz;
    listen 80;
    return 404;
}
```

To make this run behind just auth you'd

1. Instal just auth
2. Run just auth with
    ```
    JUST_AUTH_PASSWORD=your-pw JUST_AUTH_SALT=XdQ8KNyf2htjgsLqsY2AJ JUST_AUTH_PROXY_TO_URL=http://localhost:7777 PORT=7778 ./just-auth.py
    ```
3. Update the nginx config with to proxy to the just auth port instead:
    ```
    proxy_pass http://localhost:7778;
    ```
4. Restart nginx
    ```
    sudo systemctl restart nginx
    ```
5. Visit the site at https://bangs.my-site.xyz
6. You'll now see a login form.
    Enter the password you specified above and you'll be redirected to the site as normal until the cookie expires in a week.
## FAQ
Q. Why not just use http authentication?

A. Many browsers, particularly on mobile, don't keep credentials for very long at all.
   Also, if another site, (such as my own Just Bangs!) redirects to a site using http authentication,
   the browser can tend to hang waiting on the credentials, requiring a refresh which is annoying.
   Just Auth will just remember the auth token until it is removed

Q. Should I use this in production?

A. No, although it's secure to my limited knowledge and purposes, it's not very robust at all.
   It certainly hasn't had any kind of security review.
   Also, it's based on python's http.server module which the docs warn against using in production.